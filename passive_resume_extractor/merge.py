"""Delta merge logic for passive resume extraction.

When the LLM returns a delta (only the fields that changed), this module
merges it into the existing resume data without clobbering previously
extracted information. Each field type has a dedicated strategy:

- scalar fields           -> overwrite
- dict fields             -> merge (update)
- list fields             -> dedupe + append
- repeating fields        -> add new entries, or update entries matched by key
  (list-of-dict)

This is the core anti-overwrite guarantee of the design: repeated turns of
conversation never erase information that was extracted earlier.
"""

from __future__ import annotations

from typing import Any, Dict, List

DELTA_TAG_ADD = "add"
DELTA_TAG_UPDATE = "update"

# Which top-level keys are always safe to overwrite (non-repeating, single-value)
SIMPLE_OVERWRITE_KEYS = {
    "target_position",
    "target_industry",
    "target_location",
    "name",
    "gender",
    "phone",
    "email",
    "photo",
    "graduation_date",
    "availability",
    "personal_summary",
}

# Dict-type keys that get merged
DICT_MERGE_KEYS = {
    "hard_skills",
    "language_skills",
    "portfolio_links",
}

# List-type keys (non-repeating, non-dict) that get appended
LIST_APPEND_KEYS = {
    "soft_skills",
    "certificates",
    "other_experiences",
}

# Repeating (list-of-dict) keys
REPEATING_FIELD_KEYS = {
    "education_list",
    "work_experience_list",
    "project_experience_list",
}


def merge_extracted_fields(existing: Dict[str, Any], delta: Dict[str, Any]) -> None:
    """Merge a delta dict into existing resume_data **in-place**.

    Args:
        existing: The current ``resume_data`` dict (modified in-place).
        delta: The delta dict returned by the LLM extraction call.
    """
    if not delta:
        return

    for key, value in delta.items():
        if value is None or value == "" or value == [] or value == {}:
            continue  # skip empty values

        if key in SIMPLE_OVERWRITE_KEYS:
            # Simple scalar field — just overwrite
            existing[key] = value

        elif key in DICT_MERGE_KEYS:
            # Dict field — merge (existing dict gets updated)
            existing_val = existing.get(key, {})
            if not isinstance(existing_val, dict):
                existing_val = {}
            if isinstance(value, dict):
                existing_val.update(value)
                existing[key] = existing_val

        elif key in LIST_APPEND_KEYS:
            # List field — append unique items
            existing_val = existing.get(key, [])
            if not isinstance(existing_val, list):
                existing_val = []
            if isinstance(value, list):
                seen = set(existing_val)
                for item in value:
                    if item not in seen:
                        existing_val.append(item)
                        seen.add(item)
                existing[key] = existing_val

        elif key in REPEATING_FIELD_KEYS:
            # Repeating (list-of-dict) field
            existing_val = existing.get(key, [])
            if not isinstance(existing_val, list):
                existing_val = []

            if isinstance(value, list):
                for entry in value:
                    if not isinstance(entry, dict):
                        continue
                    op = entry.pop("_op", None)
                    match_key = entry.pop("_match", None)

                    if op == DELTA_TAG_ADD:
                        # Add a new entry
                        existing_val.append(entry)

                    elif op == DELTA_TAG_UPDATE and match_key:
                        # Update matching entry
                        _apply_update_to_matching(existing_val, match_key, entry)

                existing[key] = existing_val

        else:
            # Unknown key — still apply as simple overwrite
            existing[key] = value


def _apply_update_to_matching(
    entries: List[Dict[str, Any]],
    match_key: Dict[str, Any],
    updates: Dict[str, Any],
) -> None:
    """Find an entry in *entries* matching *match_key* and apply *updates*.

    Uses the first matching entry (matched by ALL key-value pairs in
    ``match_key``). If no match is found, the updates are silently ignored
    (the LLM may hallucinate a non-existent entry).
    """
    for entry in entries:
        if isinstance(entry, dict) and all(
            entry.get(k) == v for k, v in match_key.items()
        ):
            entry.update(updates)
            return
