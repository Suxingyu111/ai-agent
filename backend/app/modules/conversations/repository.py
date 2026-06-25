from uuid import uuid4

from sqlalchemy import func, select

from app.db.models import (
    ConversationMemoryModel,
    ConversationMessageModel,
    ConversationSessionModel,
    LoveReportModel,
    utcnow,
)
from app.db.session import SessionFactory
from app.modules.conversations.schemas import ConversationMessageOut


class ConversationRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def create_conversation(
        self,
        *,
        agent_key: str,
        title: str,
        memory_namespace: str,
    ) -> ConversationSessionModel:
        conversation = ConversationSessionModel(
            conversation_id=f"conv_{uuid4().hex}",
            thread_id=f"thread_{uuid4().hex}",
            agent_key=agent_key,
            title=title,
            memory_namespace=memory_namespace,
            memory_summary="",
        )
        with self._session_factory() as session:
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    def get_conversation(self, conversation_id: str) -> ConversationSessionModel | None:
        with self._session_factory() as session:
            return session.get(ConversationSessionModel, conversation_id)

    def list_conversations(self) -> list[ConversationSessionModel]:
        with self._session_factory() as session:
            statement = (
                select(ConversationSessionModel)
                .where(ConversationSessionModel.deleted_at.is_(None))
                .order_by(ConversationSessionModel.updated_at.desc())
            )
            return list(session.scalars(statement))

    def list_messages(self, conversation_id: str) -> list[ConversationMessageOut]:
        with self._session_factory() as session:
            statement = (
                select(ConversationMessageModel)
                .where(ConversationMessageModel.conversation_id == conversation_id)
                .order_by(ConversationMessageModel.sequence_no)
            )
            return [self._message_out(message) for message in session.scalars(statement)]

    def add_message(
        self,
        conversation_id: str,
        message: ConversationMessageOut,
    ) -> None:
        with self._session_factory() as session:
            sequence_no = self._next_sequence_no(session, conversation_id)
            session.add(
                ConversationMessageModel(
                    message_id=message.message_id,
                    conversation_id=conversation_id,
                    role=message.role,
                    content=message.content,
                    safety_flags=message.safety_flags,
                    sequence_no=sequence_no,
                )
            )
            self._touch_conversation(session, conversation_id)
            session.commit()

    def update_memory_summary(
        self,
        conversation_id: str,
        memory_summary: str,
    ) -> None:
        with self._session_factory() as session:
            conversation = session.get(ConversationSessionModel, conversation_id)
            if conversation is None:
                return
            conversation.memory_summary = memory_summary
            conversation.updated_at = utcnow()
            session.commit()

    def add_memory_candidate(
        self,
        *,
        conversation_id: str,
        agent_key: str,
        namespace: str,
        memory_type: str,
        content: str,
        confidence: float,
        requires_user_consent: bool,
    ) -> None:
        with self._session_factory() as session:
            session.add(
                ConversationMemoryModel(
                    memory_id=f"mem_{uuid4().hex}",
                    conversation_id=conversation_id,
                    agent_key=agent_key,
                    namespace=namespace,
                    type=memory_type,
                    content=content,
                    confidence=confidence,
                    requires_user_consent=requires_user_consent,
                )
            )
            session.commit()

    def add_love_report(
        self,
        *,
        conversation_id: str,
        report: dict[str, object],
        safety_flags: list[str],
    ) -> None:
        with self._session_factory() as session:
            session.add(
                LoveReportModel(
                    report_id=f"report_{uuid4().hex}",
                    conversation_id=conversation_id,
                    report=report,
                    safety_flags=safety_flags,
                )
            )
            self._touch_conversation(session, conversation_id)
            session.commit()

    def _next_sequence_no(self, session, conversation_id: str) -> int:
        max_sequence = session.scalar(
            select(func.max(ConversationMessageModel.sequence_no)).where(
                ConversationMessageModel.conversation_id == conversation_id
            )
        )
        return int(max_sequence or 0) + 1

    def _touch_conversation(self, session, conversation_id: str) -> None:
        conversation = session.get(ConversationSessionModel, conversation_id)
        if conversation is not None:
            conversation.updated_at = utcnow()

    def _message_out(self, message: ConversationMessageModel) -> ConversationMessageOut:
        return ConversationMessageOut(
            message_id=message.message_id,
            role=message.role,  # type: ignore[arg-type]
            content=message.content,
            safety_flags=list(message.safety_flags or []),
        )
