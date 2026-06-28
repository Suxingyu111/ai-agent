from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.modules.knowledge.collector import UrlFetchResult


def test_love_master_knowledge_api_indexes_and_queries_markdown() -> None:
    app = create_app(settings=Settings(APP_ENV="test", LLM_API_KEY=""))
    client = TestClient(app)

    document_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/documents",
        json={
            "source_uri": "local://love-master/ambiguous_invitation_api.md",
            "markdown": """---
title: 暧昧期低压力邀约原则
relationship_stage: ambiguous
primary_category: meeting_dating
safety_level: normal
---

# 暧昧期低压力邀约原则

低压力邀约可以帮助用户观察对方投入度，同时尊重对方边界。
""",
        },
    )
    assert document_response.status_code == 201
    assert document_response.json()["chunk_count"] == 1

    query_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/query",
        json={"query": "暧昧期如何低压力邀约？", "limit": 3},
    )

    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["knowledge_used"] is True
    assert payload["citations"][0]["title"] == "暧昧期低压力邀约原则"


def test_love_master_knowledge_api_lists_documents_with_chunks() -> None:
    app = create_app(settings=Settings(APP_ENV="test", LLM_API_KEY=""))
    client = TestClient(app)

    client.post(
        "/api/v1/knowledge-bases/love-master-default/documents",
        json={
            "source_uri": "local://love-master/debug-view.md",
            "markdown": """---
title: 可读调试知识卡片
relationship_stage: general
primary_category: relationship
safety_level: normal
---

# 可读调试知识卡片

## 核心原则

这是用于调试查看的原始知识片段。
""",
        },
    )

    response = client.get("/api/v1/knowledge-bases/love-master-default/documents")

    assert response.status_code == 200
    payload = response.json()
    assert payload["knowledge_base_id"] == "kb_love_master_default"
    assert payload["document_count"] >= 1
    assert payload["chunk_count"] >= 1
    document = next(
        item
        for item in payload["documents"]
        if item["source_uri"] == "local://love-master/debug-view.md"
    )
    assert document["title"] == "可读调试知识卡片"
    assert document["metadata"]["relationship_stage"] == "general"
    chunk = document["chunks"][0]
    assert chunk["chunk_index"] == 1
    assert chunk["title_path"] == "可读调试知识卡片 / 核心原则"
    assert chunk["qdrant_point_id"]
    assert "这是用于调试查看的原始知识片段" in chunk["content"]


class FakeUrlFetcher:
    def fetch(self, url: str) -> UrlFetchResult:
        title = "Healthy digital boundaries"
        paragraph = "Digital boundaries include expectations about reply speed and privacy."
        if "repair" in url:
            title = "Repair conversations after conflict"
            paragraph = "Repair conversations help partners lower defensiveness after conflict."
        return UrlFetchResult(
            url=url,
            html=f"""
            <html>
              <head><title>{title}</title></head>
              <body>
                <article>
                  <h1>{title}</h1>
                  <p>{paragraph}</p>
                  <p>Respectful partners do not demand constant access to each other's phones.</p>
                </article>
              </body>
            </html>
            """,
        )


def test_love_master_knowledge_api_collects_url_and_indexes_result(tmp_path) -> None:
    app = create_app(
        settings=Settings(
            APP_ENV="test",
            LLM_API_KEY="",
            KNOWLEDGE_DOCUMENTS_PATH=str(tmp_path / "knowledge"),
        )
    )
    app.state.knowledge_service.set_url_fetcher(FakeUrlFetcher())
    client = TestClient(app)

    collect_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/sources/collect",
        json={
            "source_url": "https://example.com/digital-boundaries",
            "primary_category": "safety_boundaries",
            "topic_tags": ["boundaries", "digital_boundaries"],
        },
    )

    assert collect_response.status_code == 201
    payload = collect_response.json()
    assert payload["source_url"] == "https://example.com/digital-boundaries"
    assert payload["document"]["status"] == "indexed"
    assert payload["markdown_path"].startswith(str(tmp_path / "knowledge" / "collected"))
    assert "Healthy digital boundaries" in (tmp_path / "knowledge" / "collected").joinpath(
        payload["markdown_path"].split("/")[-1]
    ).read_text(encoding="utf-8")
    assert "Healthy digital boundaries" in payload["markdown"]

    query_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/query",
        json={"query": "如何处理回复速度和手机隐私的边界？"},
    )
    assert query_response.status_code == 200
    assert query_response.json()["citations"][0]["source_uri"] == (
        "https://example.com/digital-boundaries"
    )


def test_love_master_knowledge_api_supports_batch_sources_reindex_debug_and_evaluation(
    tmp_path,
) -> None:
    app = create_app(
        settings=Settings(
            APP_ENV="test",
            LLM_API_KEY="",
            KNOWLEDGE_DOCUMENTS_PATH=str(tmp_path / "knowledge"),
        )
    )
    app.state.knowledge_service.set_url_fetcher(FakeUrlFetcher())
    client = TestClient(app)

    batch_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/sources/batch-collect",
        json={
            "sources": [
                {
                    "source_url": "https://example.com/digital-boundaries",
                    "primary_category": "safety_boundaries",
                    "topic_tags": ["boundaries", "privacy"],
                },
                {
                    "source_url": "https://example.com/repair",
                    "primary_category": "conflict_repair",
                    "topic_tags": ["conflict", "repair"],
                },
            ]
        },
    )

    assert batch_response.status_code == 201
    assert batch_response.json()["collected_count"] == 2

    sources_response = client.get("/api/v1/knowledge-bases/love-master-default/sources")
    assert sources_response.status_code == 200
    sources_payload = sources_response.json()
    assert sources_payload["source_count"] >= 2
    assert any(item["review_status"] == "reviewed" for item in sources_payload["sources"])

    reindex_response = client.post("/api/v1/knowledge-bases/love-master-default/documents/reindex")
    assert reindex_response.status_code == 200
    assert reindex_response.json()["chunk_count"] >= 2

    debug_response = client.get(
        "/api/v1/knowledge-bases/love-master-default/retrieval-debug",
        params={"query": "如何沟通手机隐私和回复速度？", "limit": 5},
    )
    assert debug_response.status_code == 200
    debug_payload = debug_response.json()
    assert debug_payload["knowledge_used"] is True
    assert debug_payload["classification"]["primary_category"] == "safety_boundaries"
    assert debug_payload["selected_evidence"]
    assert "Digital boundaries" in debug_payload["selected_evidence"][0]["content"]

    evaluation_response = client.post(
        "/api/v1/knowledge-bases/love-master-default/retrieval-evaluations",
        json={
            "query": "如何沟通手机隐私和回复速度？",
            "expected_titles": ["Healthy digital boundaries"],
            "forbidden_titles": ["Repair conversations after conflict"],
            "limit": 5,
        },
    )
    assert evaluation_response.status_code == 200
    evaluation_payload = evaluation_response.json()
    assert evaluation_payload["matched_expected_titles"] == ["Healthy digital boundaries"]
    assert evaluation_payload["forbidden_title_hits"] == []
    assert evaluation_payload["passed"] is True
