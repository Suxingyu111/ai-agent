from app.core.config import Settings
from app.db.models import KnowledgeChunkModel
from app.db.session import SessionFactory, create_db_and_tables, create_session_factory
from app.modules.knowledge.collector import UrlFetchResult
from app.modules.knowledge.embedding import LocalHashEmbeddingService
from app.modules.knowledge.service import KnowledgeService
from app.modules.knowledge.text import parse_markdown, split_markdown
from app.modules.knowledge.vector_store import VectorPoint, VectorSearchHit


def _session_factory() -> SessionFactory:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_db_and_tables(session_factory)
    return session_factory


def _service() -> KnowledgeService:
    session_factory = _session_factory()
    return KnowledgeService(settings=Settings(APP_ENV="test"), session_factory=session_factory)


class SelectiveVectorStore:
    def __init__(self, marker: str) -> None:
        self.marker = marker
        self.points: list[VectorPoint] = []

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        self.points.extend(points)

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]:
        for point in self.points:
            if self.marker in str(point.payload.get("content")):
                return [VectorSearchHit(point_id=point.point_id, score=0.95, payload=point.payload)]
        return []


class InspectableVectorStore:
    def __init__(self) -> None:
        self.points: dict[str, VectorPoint] = {}
        self.deleted_filters: list[dict[str, object]] = []

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        for point in points:
            self.points[point.point_id] = point

    def delete(self, collection_name: str, *, filters: dict[str, object]) -> None:
        self.deleted_filters.append(filters)
        self.points = {
            point_id: point
            for point_id, point in self.points.items()
            if not all(point.payload.get(key) == value for key, value in filters.items())
        }

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]:
        hits = [
            VectorSearchHit(point_id=point.point_id, score=0.9, payload=point.payload)
            for point in self.points.values()
            if all(point.payload.get(key) == value for key, value in filters.items())
        ]
        return hits[:limit]


def test_split_markdown_merges_short_sections_into_context_rich_chunk() -> None:
    chunks = split_markdown(
        """# 数字边界沟通原则

## 适用场景

用户被要求查手机、共享定位、随时报备，或想谈回复速度和隐私边界。

## 核心原则

亲密关系不等于放弃隐私。健康的数字边界应建立在信任和协商上，而不是监控。

## 可执行步骤

说明你愿意保持透明，但不接受被检查和被控制。提出双方都能接受的联系规则。

## 可参考话术

可以说：我愿意让你安心，但查手机会让我觉得不被信任。
""",
        {
            "title": "数字边界沟通原则",
            "relationship_stage": "general",
            "primary_category": "safety_boundaries",
        },
    )

    assert len(chunks) == 1
    assert "适用场景 + 核心原则 + 可执行步骤 + 可参考话术" in chunks[0].title_path
    assert "【适用场景】" in chunks[0].content
    assert "【可参考话术】" in chunks[0].content
    assert "亲密关系不等于放弃隐私" in chunks[0].content


def test_query_love_master_expands_hit_with_same_document_context() -> None:
    vector_store = SelectiveVectorStore(marker="命中片段")
    service = KnowledgeService(
        settings=Settings(APP_ENV="test", RAG_CONTEXT_MAX_CHARS=2200),
        session_factory=_session_factory(),
        vector_store=vector_store,
    )
    knowledge_base = service.ensure_love_master_default_base()
    long_context = " ".join(["命中片段：手机隐私边界需要先识别控制和信任问题。"] * 45)
    service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri="local://love-master/digital-context.md",
        markdown=f"""---
title: 数字边界完整沟通
relationship_stage: general
primary_category: safety_boundaries
safety_level: normal
---

# 数字边界完整沟通

## 识别问题

{long_context}

## 可参考话术

可以说：我愿意让你安心，但查手机会让我觉得不被信任。我们可以约定忙的时候提前说一声。
""",
    )

    result = service.query_love_master(
        query="如何沟通手机隐私？",
        tenant_id="default",
        project_id="default",
        limit=5,
    )

    assert result.knowledge_used is True
    assert result.evidence[0].title == "数字边界完整沟通"
    assert "命中片段" in result.evidence[0].content
    assert "可参考话术" in result.evidence[0].content
    assert "查手机会让我觉得不被信任" in result.evidence[0].content


def test_reindex_rebuilds_existing_project_document_chunks_and_removes_stale_vectors(
    tmp_path,
) -> None:
    knowledge_path = tmp_path / "knowledge"
    curated_path = knowledge_path / "curated"
    curated_path.mkdir(parents=True)
    (curated_path / "digital.md").write_text(
        """---
title: 数字边界迁移测试
relationship_stage: general
primary_category: safety_boundaries
safety_level: normal
---

# 数字边界迁移测试

## 适用场景

用户被要求查手机、共享定位、随时报备。

## 核心原则

亲密关系不等于放弃隐私。

## 可参考话术

可以说：我愿意让你安心，但查手机会让我觉得不被信任。
""",
        encoding="utf-8",
    )
    vector_store = InspectableVectorStore()
    session_factory = _session_factory()
    service = KnowledgeService(
        settings=Settings(APP_ENV="test", KNOWLEDGE_DOCUMENTS_PATH=str(knowledge_path)),
        session_factory=session_factory,
        vector_store=vector_store,
    )
    service.seed_default_documents()
    documents = service.list_love_master_documents()
    document = documents.documents[0]
    stale_chunk = KnowledgeChunkModel(
        chunk_id="chunk_stale_short",
        document_id=document.document_id,
        knowledge_base_id=document.knowledge_base_id,
        chunk_index=99,
        title=document.title,
        title_path=f"{document.title} / 历史短切片",
        content="标题：数字边界迁移测试\n章节：历史短切片\n正文：\n陈旧短切片",
        content_hash="stale",
        token_count=10,
        qdrant_point_id="point_stale_short",
        status="indexed",
        metadata_json=document.metadata,
    )
    with session_factory() as session:
        session.add(stale_chunk)
        session.commit()
    vector_store.upsert(
        "test_collection",
        [
            VectorPoint(
                point_id="point_stale_short",
                vector=LocalHashEmbeddingService(64).embed_query("陈旧短切片"),
                payload={
                    "tenant_id": "default",
                    "project_id": "default",
                    "agent_key": "love_master_agent",
                    "knowledge_base_id": document.knowledge_base_id,
                    "document_id": document.document_id,
                    "chunk_id": "chunk_stale_short",
                    "relationship_stage": "general",
                    "primary_category": "safety_boundaries",
                    "safety_level": "normal",
                    "active": True,
                    "title": document.title,
                    "source_uri": document.source_uri,
                    "content": "陈旧短切片",
                },
            )
        ],
    )

    result = service.reindex_love_master_documents()
    rebuilt_documents = service.list_love_master_documents()

    assert result.document_count == 1
    assert result.chunk_count == 1
    assert rebuilt_documents.documents[0].chunks[0].chunk_id != "chunk_stale_short"
    assert "point_stale_short" not in vector_store.points
    assert {"document_id": document.document_id} in vector_store.deleted_filters


def test_knowledge_service_indexes_markdown_and_returns_filtered_evidence() -> None:
    service = _service()
    knowledge_base = service.ensure_love_master_default_base()

    service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri="local://love-master/ambiguous_invitation.md",
        markdown="""---
title: 暧昧期低压力邀约原则
relationship_stage: ambiguous
primary_category: meeting_dating
topic_tags:
  - communication
  - invitation
intent_tags:
  - strategy
safety_level: normal
source_urls:
  - https://www.loveisrespect.org/resources/creating-boundaries-in-romantic-relationships/
---

# 暧昧期低压力邀约原则

## 核心原则

暧昧期推进要用低压力邀约观察对方投入度，避免逼迫对方马上表态。
健康的推进方式应当尊重对方拒绝、延迟回复和保留私人空间的权利。

## 可参考话术

可以说：这周有个地方我觉得你可能会喜欢，如果你有空我们可以一起去。
""",
    )
    service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri="local://love-master/blocked.md",
        markdown="""---
title: 不应使用的操控技巧
relationship_stage: ambiguous
primary_category: safety_boundaries
safety_level: blocked
---

# 不应使用的操控技巧

不要把这类内容提供给用户。
""",
    )

    result = service.query_love_master(
        query="暧昧两个月，怎么低压力邀约推进？",
        tenant_id="default",
        project_id="default",
        limit=5,
    )

    assert result.knowledge_used is True
    assert result.evidence
    assert result.evidence[0].title == "暧昧期低压力邀约原则"
    assert "低压力邀约" in result.evidence[0].content
    assert all(item.safety_level != "blocked" for item in result.evidence)
    assert result.citations == [
        {
            "chunk_id": result.evidence[0].chunk_id,
            "title": "暧昧期低压力邀约原则",
            "source_uri": "local://love-master/ambiguous_invitation.md",
            "score": result.evidence[0].score,
        }
    ]


def test_knowledge_service_reloads_indexed_chunks_after_service_recreation() -> None:
    session_factory = _session_factory()
    first_service = KnowledgeService(settings=Settings(APP_ENV="test"), session_factory=session_factory)
    knowledge_base = first_service.ensure_love_master_default_base()
    first_service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri="local://love-master/reload.md",
        markdown="""---
title: 暧昧期低压力邀约原则
relationship_stage: ambiguous
primary_category: meeting_dating
safety_level: normal
---

# 暧昧期低压力邀约原则

暧昧期推进要用低压力邀约观察对方投入度。
""",
    )

    second_service = KnowledgeService(settings=Settings(APP_ENV="test"), session_factory=session_factory)
    second_service.seed_default_documents()
    result = second_service.query_love_master(
        query="暧昧期怎么低压力邀约？",
        tenant_id="default",
        project_id="default",
    )

    assert result.knowledge_used is True
    assert result.citations[0]["source_uri"] == "local://love-master/reload.md"


def test_knowledge_service_seeds_default_documents_from_project_markdown(tmp_path) -> None:
    knowledge_path = tmp_path / "knowledge"
    curated_path = knowledge_path / "curated"
    curated_path.mkdir(parents=True)
    (curated_path / "custom_seed.md").write_text(
        """---
title: 项目沉淀知识卡片
relationship_stage: ambiguous
primary_category: meeting_dating
safety_level: normal
---

# 项目沉淀知识卡片

从项目目录读取的低压力邀约资料，适合观察对方投入度。
""",
        encoding="utf-8",
    )
    session_factory = _session_factory()
    service = KnowledgeService(
        settings=Settings(APP_ENV="test", KNOWLEDGE_DOCUMENTS_PATH=str(knowledge_path)),
        session_factory=session_factory,
    )

    service.seed_default_documents()
    result = service.query_love_master(
        query="暧昧期怎么低压力邀约？",
        tenant_id="default",
        project_id="default",
    )

    assert result.knowledge_used is True
    assert result.citations[0]["source_uri"] == "local://love-master/curated/custom_seed.md"


def test_knowledge_service_seed_adds_new_project_documents_when_database_has_existing_doc(
    tmp_path,
) -> None:
    knowledge_path = tmp_path / "knowledge"
    curated_path = knowledge_path / "curated"
    curated_path.mkdir(parents=True)
    (curated_path / "new_boundary.md").write_text(
        """---
title: 新增边界知识卡片
relationship_stage: general
primary_category: safety_boundaries
safety_level: normal
---

# 新增边界知识卡片

健康关系需要尊重手机隐私和数字边界。
""",
        encoding="utf-8",
    )
    session_factory = _session_factory()
    service = KnowledgeService(
        settings=Settings(APP_ENV="test", KNOWLEDGE_DOCUMENTS_PATH=str(knowledge_path)),
        session_factory=session_factory,
    )
    knowledge_base = service.ensure_love_master_default_base()
    service.ingest_markdown(
        knowledge_base_id=knowledge_base.knowledge_base_id,
        source_uri="local://love-master/existing.md",
        markdown="""---
title: 既有知识卡片
relationship_stage: ambiguous
primary_category: meeting_dating
safety_level: normal
---

# 既有知识卡片

暧昧期可以用低压力邀约观察投入度。
""",
    )

    service.seed_default_documents()
    documents = service.list_love_master_documents()

    assert any(
        document.source_uri == "local://love-master/curated/new_boundary.md"
        for document in documents.documents
    )


def test_project_curated_love_master_knowledge_covers_core_domains() -> None:
    curated_path = Settings().knowledge_documents_path
    service = _service()
    base_path = service._knowledge_documents_base_path() / "curated"
    markdown_files = sorted(base_path.rglob("*.md"))

    assert curated_path == "./knowledge/love_master"
    assert len(markdown_files) >= 30

    categories = {
        str(parse_markdown(path.read_text(encoding="utf-8")).metadata.get("primary_category"))
        for path in markdown_files
    }
    assert {
        "relationship_basics",
        "communication",
        "safety_boundaries",
        "meeting_dating",
        "conflict_repair",
        "trust_jealousy",
        "long_term_commitment",
        "breakup_recovery",
        "risk_safety",
    }.issubset(categories)


class FakeUrlFetcher:
    def fetch(self, url: str) -> UrlFetchResult:
        return UrlFetchResult(
            url=url,
            html="""
            <html>
              <head>
                <title>Creating healthy romantic boundaries</title>
                <meta name="description" content="Healthy relationships need clear boundaries." />
              </head>
              <body>
                <nav>Navigation should not enter the knowledge card.</nav>
                <main>
                  <h1>Creating healthy romantic boundaries</h1>
                  <p>Healthy boundaries help both people understand what feels respectful.</p>
                  <p>Partners should be able to say no, ask for space, and discuss expectations.</p>
                </main>
              </body>
            </html>
            """,
        )


def test_knowledge_service_collects_url_into_markdown_file_and_indexes_it(tmp_path) -> None:
    session_factory = _session_factory()
    service = KnowledgeService(
        settings=Settings(APP_ENV="test", KNOWLEDGE_DOCUMENTS_PATH=str(tmp_path / "knowledge")),
        session_factory=session_factory,
        url_fetcher=FakeUrlFetcher(),
    )

    result = service.collect_love_master_url(
        source_url="https://example.com/healthy-boundaries",
        relationship_stage="general",
        primary_category="safety_boundaries",
        topic_tags=["boundaries", "communication"],
        intent_tags=["explain"],
    )

    assert result.source_url == "https://example.com/healthy-boundaries"
    assert result.document.status == "indexed"
    assert result.markdown_path is not None
    markdown_path = tmp_path / "knowledge" / "collected" / result.markdown_path.split("/")[-1]
    assert markdown_path.read_text(encoding="utf-8") == result.markdown
    assert "title: Creating healthy romantic boundaries" in result.markdown
    assert "relationship_stage: general" in result.markdown
    assert "Healthy boundaries help both people" in result.markdown
    assert "Navigation should not enter" not in result.markdown

    query_result = service.query_love_master(
        query="关系边界怎么沟通？",
        tenant_id="default",
        project_id="default",
    )
    assert query_result.knowledge_used is True
    assert query_result.citations[0]["source_uri"] == "https://example.com/healthy-boundaries"
