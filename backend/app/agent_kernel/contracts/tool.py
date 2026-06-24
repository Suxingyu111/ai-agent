from typing import Any

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    tool_key: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_key: str
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
