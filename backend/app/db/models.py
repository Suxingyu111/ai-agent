from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class ConversationSessionModel(Base):
    __tablename__ = "conversation_sessions"
    __table_args__ = (
        Index("ix_conversation_sessions_agent_updated", "agent_key", "updated_at"),
    )

    conversation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    agent_key: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    memory_namespace: Mapped[str] = mapped_column(String(120), nullable=False)
    memory_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    messages: Mapped[list["ConversationMessageModel"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessageModel.sequence_no",
    )


class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_conversation_messages_conversation_sequence", "conversation_id", "sequence_no"),
    )

    message_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversation_sessions.conversation_id"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    safety_flags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    conversation: Mapped[ConversationSessionModel] = relationship(back_populates="messages")


class ConversationMemoryModel(Base):
    __tablename__ = "conversation_memories"
    __table_args__ = (
        Index("ix_conversation_memories_conversation", "conversation_id", "created_at"),
    )

    memory_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversation_sessions.conversation_id"),
        nullable=False,
    )
    agent_key: Mapped[str] = mapped_column(String(80), nullable=False)
    namespace: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
    requires_user_consent: Mapped[bool] = mapped_column(default=True, nullable=False)
    source_message_id: Mapped[str | None] = mapped_column(String(64), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LoveReportModel(Base):
    __tablename__ = "love_reports"
    __table_args__ = (
        Index("ix_love_reports_conversation_created", "conversation_id", "created_at"),
    )

    report_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversation_sessions.conversation_id"),
        nullable=False,
    )
    report: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    safety_flags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
