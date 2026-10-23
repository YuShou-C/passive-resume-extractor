"""Passive resume field extraction from natural conversation.

The extractor asks an LLM to return only the *delta* — the fields the user
volunteered in the latest message — which is then merged by ``merge.py``
into the existing profile.

The LLM client is duck-typed: any object exposing an
``async chat_json(system_prompt, user_input, **kwargs)`` coroutine works
(DeepSeek, OpenAI, local models, etc.).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .prompt import EXTRACTION_PROMPT
from .schema import build_flat_profile_for_llm

logger = logging.getLogger("passive_resume_extractor.extractor")


async def extract_resume_fields(
    user_input: str,
    existing_data: Optional[Dict[str, Any]] = None,
    llm_client=None,
) -> Dict[str, Any]:
    """Extract resume-related fields from *user_input* using the LLM.

    This is a passive extraction: the LLM only returns fields the user
    explicitly mentioned in this message. It never asks questions and never
    fabricates information.

    Args:
        user_input: The user's latest message text.
        existing_data: The user's current ``resume_data`` dict (or ``None``
            if first-time extraction). Used to avoid re-extracting known info.
        llm_client: Any object exposing
            ``async chat_json(system_prompt, user_input, **kwargs)``.

    Returns:
        A delta dict containing only newly extracted/changed fields.
        Returns ``{}`` if nothing extractable was found.

    Raises:
        RuntimeError: If *llm_client* is ``None``.
    """
    if llm_client is None:
        raise RuntimeError("llm_client is required for LLM-based extraction")

    # Build context string from existing data so the LLM knows what's already known
    if existing_data:
        context = build_flat_profile_for_llm(existing_data)
    else:
        context = "暂无已知简历信息"

    extract_msg = (
        "请从以下用户消息中提取简历相关信息。\n\n"
        f"已知简历数据：\n{context}\n\n"
        f"用户消息：{user_input}"
    )

    logger.debug("Calling LLM for resume field extraction")

    try:
        result = await llm_client.chat_json(
            system_prompt=EXTRACTION_PROMPT,
            user_input=extract_msg,
            temperature=0.1,  # low temperature for consistent extraction
            max_tokens=2048,
        )

        if not isinstance(result, dict):
            logger.warning(f"LLM returned non-dict result: {type(result)}")
            return {}

        # Filter out empty results
        result = {k: v for k, v in result.items() if v not in (None, "", [], {})}
        if not result:
            logger.debug("LLM extraction returned empty (no new info)")
            return {}

        logger.info(f"LLM extracted {len(result)} field(s): {list(result.keys())}")
        return result

    except Exception as exc:
        logger.error(f"LLM extraction failed: {exc}", exc_info=True)
        return {}
