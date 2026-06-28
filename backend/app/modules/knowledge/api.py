from fastapi import APIRouter, Request, status

from app.modules.knowledge.schemas import (
    KnowledgeBatchCollectRequest,
    KnowledgeBatchCollectResponse,
    KnowledgeBaseOut,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentsReadableResponse,
    KnowledgeDocumentOut,
    KnowledgeReindexResponse,
    KnowledgeRetrievalDebugResponse,
    KnowledgeRetrievalEvaluationRequest,
    KnowledgeRetrievalEvaluationResponse,
    KnowledgeSourceCollectRequest,
    KnowledgeCollectedSourceOut,
    KnowledgeSourcesReadableResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResult,
)
from app.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/knowledge-bases")


def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


@router.get("/love-master-default", response_model=KnowledgeBaseOut)
async def get_love_master_default_knowledge_base(request: Request) -> KnowledgeBaseOut:
    return get_knowledge_service(request).ensure_love_master_default_base()


@router.post(
    "/love-master-default/documents",
    response_model=KnowledgeDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_love_master_knowledge_document(
    payload: KnowledgeDocumentCreateRequest,
    request: Request,
) -> KnowledgeDocumentOut:
    service = get_knowledge_service(request)
    knowledge_base = service.ensure_love_master_default_base()
    return service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri=payload.source_uri,
        markdown=payload.markdown,
    )


@router.get(
    "/love-master-default/documents",
    response_model=KnowledgeDocumentsReadableResponse,
)
async def list_love_master_knowledge_documents(
    request: Request,
) -> KnowledgeDocumentsReadableResponse:
    return get_knowledge_service(request).list_love_master_documents()


@router.post(
    "/love-master-default/documents/reindex",
    response_model=KnowledgeReindexResponse,
)
async def reindex_love_master_knowledge_documents(request: Request) -> KnowledgeReindexResponse:
    return get_knowledge_service(request).reindex_love_master_documents()


@router.get(
    "/love-master-default/sources",
    response_model=KnowledgeSourcesReadableResponse,
)
async def list_love_master_knowledge_sources(
    request: Request,
) -> KnowledgeSourcesReadableResponse:
    return get_knowledge_service(request).list_love_master_sources()


@router.post(
    "/love-master-default/sources/collect",
    response_model=KnowledgeCollectedSourceOut,
    status_code=status.HTTP_201_CREATED,
)
async def collect_love_master_knowledge_source(
    payload: KnowledgeSourceCollectRequest,
    request: Request,
) -> KnowledgeCollectedSourceOut:
    return get_knowledge_service(request).collect_love_master_url(
        source_url=payload.source_url,
        title=payload.title,
        relationship_stage=payload.relationship_stage,
        primary_category=payload.primary_category,
        topic_tags=payload.topic_tags,
        intent_tags=payload.intent_tags,
        safety_level=payload.safety_level,
    )


@router.post(
    "/love-master-default/sources/batch-collect",
    response_model=KnowledgeBatchCollectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def batch_collect_love_master_knowledge_sources(
    payload: KnowledgeBatchCollectRequest,
    request: Request,
) -> KnowledgeBatchCollectResponse:
    return get_knowledge_service(request).batch_collect_love_master_urls(payload.sources)


@router.post("/love-master-default/query", response_model=KnowledgeQueryResult)
async def query_love_master_knowledge_base(
    payload: KnowledgeQueryRequest,
    request: Request,
) -> KnowledgeQueryResult:
    return get_knowledge_service(request).query_love_master(
        query=payload.query,
        tenant_id="default",
        project_id="default",
        limit=payload.limit,
    )


@router.get(
    "/love-master-default/retrieval-debug",
    response_model=KnowledgeRetrievalDebugResponse,
)
async def debug_love_master_knowledge_retrieval(
    query: str,
    request: Request,
    limit: int | None = None,
) -> KnowledgeRetrievalDebugResponse:
    return get_knowledge_service(request).debug_love_master_retrieval(
        query=query,
        tenant_id="default",
        project_id="default",
        limit=limit,
    )


@router.post(
    "/love-master-default/retrieval-evaluations",
    response_model=KnowledgeRetrievalEvaluationResponse,
)
async def evaluate_love_master_knowledge_retrieval(
    payload: KnowledgeRetrievalEvaluationRequest,
    request: Request,
) -> KnowledgeRetrievalEvaluationResponse:
    return get_knowledge_service(request).evaluate_love_master_retrieval(
        query=payload.query,
        expected_titles=payload.expected_titles,
        forbidden_titles=payload.forbidden_titles,
        tenant_id="default",
        project_id="default",
        limit=payload.limit,
    )
