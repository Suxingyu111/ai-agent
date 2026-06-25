from typing import Protocol, TypeVar

from pydantic import BaseModel

StructuredModelT = TypeVar("StructuredModelT", bound=BaseModel)


class StructuredOutputError(RuntimeError):
    """模型未能生成符合 schema 的结构化输出。"""


class ChatModelClient(Protocol):
    async def generate(self, messages: list[dict[str, str]]) -> str:
        """根据标准 chat messages 生成助手回复。"""

    async def generate_structured(
        self,
        messages: list[dict[str, str]],
        schema: type[StructuredModelT],
    ) -> StructuredModelT:
        """根据 Pydantic schema 生成可校验的结构化回复。"""
