from typing import Literal

from pydantic import BaseModel, Field

from app.agents.love_master_agent.schemas import LoveReportOutput


class ConversationCreateRequest(BaseModel):
    agent_key: str = "love_master_agent"
    title: str | None = None


class ConversationCreateResponse(BaseModel):
    conversation_id: str
    thread_id: str
    agent_key: str
    title: str
    memory_namespace: str


class ConversationDetailResponse(ConversationCreateResponse):
    memory_summary: str


class ConversationListResponse(BaseModel):
    conversations: list[ConversationDetailResponse]


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class ConversationMessageOut(BaseModel):
    message_id: str
    role: Literal["user", "assistant"]
    content: str
    safety_flags: list[str] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)


class MessageCreateResponse(BaseModel):
    conversation_id: str
    user_message: ConversationMessageOut
    assistant_message: ConversationMessageOut
    memory_summary: str
    safety_flags: list[str] = Field(default_factory=list)
    knowledge_used: bool = False
    citations: list[dict[str, object]] = Field(default_factory=list)


class ConversationMessagesResponse(BaseModel):
    conversation_id: str
    memory_summary: str
    messages: list[ConversationMessageOut]


class LoveReportCreateRequest(BaseModel):
    focus: str | None = Field(default=None, max_length=80)
    style: str | None = Field(default=None, max_length=80)


class LoveReportCreateResponse(BaseModel):
    conversation_id: str
    report: LoveReportOutput
    memory_summary: str
    safety_flags: list[str] = Field(default_factory=list)
