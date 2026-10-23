"""passive-resume-extractor — Schema 驱动的被动简历提取库。

公开 API：
- schema.py    : 字段定义、校验、画像展平
- merge.py     : 增量（delta）合并逻辑
- prompt.py    : Schema 驱动的 LLM 提取提示词
- extractor.py : 被动提取入口（鸭子类型 LLM 客户端）
"""

from .schema import (
    ALL_FIELDS,
    FIELDS_BY_MODULE,
    MODULE_LABELS,
    MODULE_ORDER,
    FieldType,
    ResumeFieldDef,
    ResumeModule,
    build_flat_profile_for_llm,
    get_schema_summary,
    new_empty_resume_data,
    validate_resume_data,
)
from .merge import merge_extracted_fields
from .prompt import EXTRACTION_PROMPT, build_extraction_prompt
from .extractor import extract_resume_fields

__version__ = "0.1.0"

__all__ = [
    "ALL_FIELDS",
    "EXTRACTION_PROMPT",
    "FIELDS_BY_MODULE",
    "MODULE_LABELS",
    "MODULE_ORDER",
    "FieldType",
    "ResumeFieldDef",
    "ResumeModule",
    "build_extraction_prompt",
    "build_flat_profile_for_llm",
    "extract_resume_fields",
    "get_schema_summary",
    "merge_extracted_fields",
    "new_empty_resume_data",
    "validate_resume_data",
]
