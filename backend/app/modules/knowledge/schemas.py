from pydantic import BaseModel, Field


class KnowledgeBaseOut(BaseModel):
    knowledge_base_id: str
    name: str
    domain: str
    status: str


class KnowledgeDocumentCreateRequest(BaseModel):
    source_uri: str = Field(min_length=1, max_length=500)
    markdown: str = Field(min_length=1)


class KnowledgeSourceCollectRequest(BaseModel):
    source_url: str = Field(min_length=1, max_length=500)
    title: str | None = Field(default=None, max_length=200)
    relationship_stage: str | None = Field(default=None, max_length=80)
    primary_category: str | None = Field(default=None, max_length=80)
    topic_tags: list[str] = Field(default_factory=list)
    intent_tags: list[str] = Field(default_factory=list)
    safety_level: str = Field(default="normal", max_length=40)


class KnowledgeBatchCollectRequest(BaseModel):
    sources: list[KnowledgeSourceCollectRequest] = Field(min_length=1, max_length=20)


class KnowledgeDocumentOut(BaseModel):
    document_id: str
    knowledge_base_id: str
    title: str
    source_uri: str
    status: str
    chunk_count: int


class KnowledgeChunkReadableOut(BaseModel):
    chunk_id: str
    chunk_index: int
    title: str
    title_path: str
    content: str
    token_count: int
    qdrant_point_id: str | None = None
    status: str
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeDocumentReadableOut(BaseModel):
    document_id: str
    knowledge_base_id: str
    title: str
    source_type: str
    source_uri: str
    version: str
    status: str
    metadata: dict[str, object] = Field(default_factory=dict)
    chunks: list[KnowledgeChunkReadableOut] = Field(default_factory=list)


class KnowledgeDocumentsReadableResponse(BaseModel):
    knowledge_base_id: str
    document_count: int
    chunk_count: int
    documents: list[KnowledgeDocumentReadableOut] = Field(default_factory=list)


class KnowledgeCollectedSourceOut(BaseModel):
    source_url: str
    markdown_path: str
    markdown: str
    document: KnowledgeDocumentOut


class KnowledgeBatchCollectResponse(BaseModel):
    collected_count: int
    sources: list[KnowledgeCollectedSourceOut] = Field(default_factory=list)


class KnowledgeSourceReadableOut(BaseModel):
    document_id: str
    title: str
    source_uri: str
    source_urls: list[str] = Field(default_factory=list)
    source_type: str
    review_status: str
    primary_category: str
    relationship_stage: str
    safety_level: str
    chunk_count: int


class KnowledgeSourcesReadableResponse(BaseModel):
    knowledge_base_id: str
    source_count: int
    sources: list[KnowledgeSourceReadableOut] = Field(default_factory=list)


class KnowledgeReindexResponse(BaseModel):
    knowledge_base_id: str
    collection_name: str
    document_count: int
    chunk_count: int


class KnowledgeEvidence(BaseModel):
    chunk_id: str
    document_id: str
    knowledge_base_id: str
    title: str
    source_uri: str
    content: str
    score: float
    relationship_stage: str | None = None
    primary_category: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    intent_tags: list[str] = Field(default_factory=list)
    safety_level: str = "normal"


class KnowledgeQueryRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int | None = Field(default=None, ge=1, le=20)


class KnowledgeQueryResult(BaseModel):
    knowledge_used: bool
    evidence: list[KnowledgeEvidence] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)


class KnowledgeRetrievalDebugResponse(BaseModel):
    query: str
    classification: dict[str, object]
    knowledge_used: bool
    candidate_count: int
    selected_evidence: list[KnowledgeEvidence] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)


class KnowledgeRetrievalEvaluationRequest(BaseModel):
    query: str = Field(min_length=1)
    expected_titles: list[str] = Field(default_factory=list)
    forbidden_titles: list[str] = Field(default_factory=list)
    limit: int | None = Field(default=None, ge=1, le=20)


class KnowledgeRetrievalEvaluationResponse(BaseModel):
    query: str
    passed: bool
    matched_expected_titles: list[str] = Field(default_factory=list)
    missing_expected_titles: list[str] = Field(default_factory=list)
    forbidden_title_hits: list[str] = Field(default_factory=list)
    retrieved_titles: list[str] = Field(default_factory=list)
    result: KnowledgeQueryResult
