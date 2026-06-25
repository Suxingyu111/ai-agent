from fastapi import APIRouter, Request, status

from app.modules.conversations.schemas import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationMessagesResponse,
    LoveReportCreateRequest,
    LoveReportCreateResponse,
    MessageCreateRequest,
    MessageCreateResponse,
)
from app.modules.conversations.service import ConversationService

router = APIRouter(prefix="/conversations")


def get_conversation_service(request: Request) -> ConversationService:
    return request.app.state.conversation_service


@router.post("", response_model=ConversationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest,
    request: Request,
) -> ConversationCreateResponse:
    service = get_conversation_service(request)
    return service.create_conversation(payload)


@router.get("", response_model=ConversationListResponse)
async def list_conversations(request: Request) -> ConversationListResponse:
    service = get_conversation_service(request)
    return service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
) -> ConversationDetailResponse:
    service = get_conversation_service(request)
    return service.get_conversation(conversation_id)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: str,
    payload: MessageCreateRequest,
    request: Request,
) -> MessageCreateResponse:
    service = get_conversation_service(request)
    return await service.create_message(conversation_id, payload)


@router.get("/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def list_messages(conversation_id: str, request: Request) -> ConversationMessagesResponse:
    service = get_conversation_service(request)
    return service.list_messages(conversation_id)


@router.post(
    "/{conversation_id}/love-report",
    response_model=LoveReportCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_love_report(
    conversation_id: str,
    payload: LoveReportCreateRequest,
    request: Request,
) -> LoveReportCreateResponse:
    service = get_conversation_service(request)
    return await service.create_love_report(conversation_id, payload)
