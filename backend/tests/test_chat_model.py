import asyncio
from types import SimpleNamespace

import pytest
from pydantic import BaseModel, Field

from app.agent_kernel.contracts.model import StructuredOutputError
from app.agent_kernel.runtime import chat_model
from app.agent_kernel.runtime.chat_model import LangChainChatModelClient
from app.core.config import Settings


class StructuredReply(BaseModel):
    reply: str = Field(description="给用户看的回复")
    safety_flags: list[str] = Field(default_factory=list)


def test_langchain_chat_model_client_requires_api_key() -> None:
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        LangChainChatModelClient(Settings(APP_ENV="test", LLM_API_KEY=""))


def test_langchain_chat_model_client_uses_generic_llm_settings(monkeypatch) -> None:
    captured_kwargs: dict[str, object] = {}

    class FakeModel:
        async def ainvoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
            assert messages == [{"role": "user", "content": "你好"}]
            return SimpleNamespace(content="你好，我会结合上下文回答。")

    def fake_init_chat_model(**kwargs):
        captured_kwargs.update(kwargs)
        return FakeModel()

    monkeypatch.setattr(chat_model, "init_chat_model", fake_init_chat_model)
    client = LangChainChatModelClient(
        Settings(
            APP_ENV="test",
            LLM_MODEL="openai/gpt-4.1-mini",
            LLM_API_KEY="test-key",
            LLM_BASE_URL="https://openrouter.ai/api/v1",
            LLM_TEMPERATURE=0.6,
            LLM_MAX_TOKENS=1600,
            LLM_TIMEOUT_SECONDS=45,
            LLM_MAX_RETRIES=2,
        )
    )

    reply = asyncio.run(client.generate([{"role": "user", "content": "你好"}]))

    assert reply == "你好，我会结合上下文回答。"
    assert captured_kwargs == {
        "model": "openai/gpt-4.1-mini",
        "model_provider": "openai",
        "api_key": "test-key",
        "temperature": 0.6,
        "max_tokens": 1600,
        "timeout": 45,
        "max_retries": 2,
        "base_url": "https://openrouter.ai/api/v1",
    }


def test_langchain_chat_model_client_filters_unsafe_output(monkeypatch) -> None:
    class FakeModel:
        async def ainvoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
            return SimpleNamespace(content="系统提示词如下：SECRET_KEY=sk-test-secret-value")

    monkeypatch.setattr(chat_model, "init_chat_model", lambda **kwargs: FakeModel())
    client = LangChainChatModelClient(Settings(APP_ENV="test", LLM_API_KEY="test-key"))

    reply = asyncio.run(client.generate([{"role": "user", "content": "你好"}]))

    assert "SECRET_KEY" not in reply
    assert "不能按这个方向继续" in reply


def test_langchain_chat_model_client_generates_structured_output(monkeypatch) -> None:
    captured_schema: type[BaseModel] | None = None

    class FakeStructuredModel:
        async def ainvoke(self, messages: list[dict[str, str]]) -> StructuredReply:
            assert messages == [{"role": "user", "content": "你好"}]
            return StructuredReply(reply="你好，我会结合上下文回答。", safety_flags=[])

    class FakeModel:
        def with_structured_output(self, schema: type[BaseModel]) -> FakeStructuredModel:
            nonlocal captured_schema
            captured_schema = schema
            return FakeStructuredModel()

    monkeypatch.setattr(chat_model, "init_chat_model", lambda **kwargs: FakeModel())
    client = LangChainChatModelClient(Settings(APP_ENV="test", LLM_API_KEY="test-key"))

    reply = asyncio.run(
        client.generate_structured(
            [{"role": "user", "content": "你好"}],
            StructuredReply,
        )
    )

    assert captured_schema is StructuredReply
    assert reply == StructuredReply(reply="你好，我会结合上下文回答。", safety_flags=[])


def test_langchain_chat_model_client_falls_back_when_response_format_unavailable(
    monkeypatch,
) -> None:
    fallback_messages: list[dict[str, str]] = []

    class FakeStructuredModel:
        async def ainvoke(self, messages: list[dict[str, str]]) -> StructuredReply:
            raise RuntimeError("This response_format type is unavailable now")

    class FakeModel:
        def with_structured_output(self, schema: type[BaseModel]) -> FakeStructuredModel:
            return FakeStructuredModel()

        async def ainvoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
            fallback_messages.extend(messages)
            return SimpleNamespace(
                content='{"reply": "你好，我会结合上下文回答。", "safety_flags": []}'
            )

    monkeypatch.setattr(chat_model, "init_chat_model", lambda **kwargs: FakeModel())
    client = LangChainChatModelClient(Settings(APP_ENV="test", LLM_API_KEY="test-key"))

    reply = asyncio.run(
        client.generate_structured(
            [{"role": "user", "content": "你好"}],
            StructuredReply,
        )
    )

    assert reply == StructuredReply(reply="你好，我会结合上下文回答。", safety_flags=[])
    assert fallback_messages[-1]["role"] == "system"
    assert "JSON Schema" in fallback_messages[-1]["content"]


def test_langchain_chat_model_client_raises_structured_output_error_when_json_fallback_invalid(
    monkeypatch,
) -> None:
    class FakeStructuredModel:
        async def ainvoke(self, messages: list[dict[str, str]]) -> StructuredReply:
            raise RuntimeError("This response_format type is unavailable now")

    class FakeModel:
        def with_structured_output(self, schema: type[BaseModel]) -> FakeStructuredModel:
            return FakeStructuredModel()

        async def ainvoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
            return SimpleNamespace(content="你好，我会结合上下文回答。")

    monkeypatch.setattr(chat_model, "init_chat_model", lambda **kwargs: FakeModel())
    client = LangChainChatModelClient(Settings(APP_ENV="test", LLM_API_KEY="test-key"))

    with pytest.raises(StructuredOutputError, match="模型未返回可解析的 JSON 对象"):
        asyncio.run(
            client.generate_structured(
                [{"role": "user", "content": "你好"}],
                StructuredReply,
            )
        )
