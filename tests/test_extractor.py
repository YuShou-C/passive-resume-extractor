import asyncio

import pytest

from passive_resume_extractor.extractor import extract_resume_fields


class FakeLLMClient:
    """Duck-typed LLM client returning a fixed delta."""

    def __init__(self, delta):
        self.delta = delta
        self.calls = []

    async def chat_json(self, system_prompt, user_input, **kwargs):
        self.calls.append(
            {"system_prompt": system_prompt, "user_input": user_input, **kwargs}
        )
        return self.delta


def test_extract_returns_delta():
    client = FakeLLMClient(
        {"target_position": "后端开发工程师", "target_location": "杭州"}
    )
    delta = asyncio.run(
        extract_resume_fields("我想找后端开发，去杭州", {}, client)
    )
    assert delta == {"target_position": "后端开发工程师", "target_location": "杭州"}


def test_extract_ignores_non_dict_result():
    client = FakeLLMClient("not a dict")
    delta = asyncio.run(extract_resume_fields("你好", {}, client))
    assert delta == {}


def test_extract_requires_client():
    with pytest.raises(RuntimeError):
        asyncio.run(extract_resume_fields("你好", {}, None))
