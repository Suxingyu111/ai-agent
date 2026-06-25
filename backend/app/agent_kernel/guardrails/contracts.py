from enum import StrEnum
from typing import Literal, Protocol

from pydantic import BaseModel, Field


class GuardrailDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"
    REWRITE = "rewrite"
    ESCALATE = "escalate"


class GuardrailFinding(BaseModel):
    category: str
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    span: str | None = None
    redacted_value: str | None = None


class GuardrailResult(BaseModel):
    decision: GuardrailDecision
    sanitized_content: str | None = None
    user_message: str | None = None
    findings: list[GuardrailFinding] = Field(default_factory=list)


class GuardrailContext(BaseModel):
    tenant_id: str
    project_id: str
    user_id: str | None = None
    agent_key: str
    run_id: str
    conversation_id: str | None = None
    direction: Literal["input", "output", "tool_input", "tool_output"]
    safety_profile: str = "default"


class GuardrailInterceptor(Protocol):
    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        """检查并可选改写内容。"""
