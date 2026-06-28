from app.core.config import Settings


def test_settings_can_be_built_from_environment_values() -> None:
    settings = Settings(
        APP_ENV="test",
        SERVER_HOST="127.0.0.1",
        SERVER_PORT=9000,
        CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173",
    )

    assert settings.app_env == "test"
    assert settings.server_port == 9000
    assert settings.cors_allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_settings_reads_comma_separated_cors_origins_from_env_file(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_ENV=development",
                "CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_env == "development"
    assert settings.cors_allowed_origins == [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]


def test_settings_reads_single_generic_llm_configuration() -> None:
    settings = Settings(
        APP_ENV="test",
        LLM_MODEL="openai/gpt-4.1-mini",
        LLM_API_KEY="test-api-key",
        LLM_BASE_URL="https://openrouter.ai/api/v1",
        LLM_TEMPERATURE=0.6,
        LLM_MAX_TOKENS=1600,
        LLM_TIMEOUT_SECONDS=45,
        LLM_MAX_RETRIES=2,
    )

    assert settings.llm_model == "openai/gpt-4.1-mini"
    assert settings.llm_api_key == "test-api-key"
    assert settings.llm_base_url == "https://openrouter.ai/api/v1"
    assert settings.llm_temperature == 0.6
    assert settings.llm_max_tokens == 1600
    assert settings.llm_timeout_seconds == 45
    assert settings.llm_max_retries == 2


def test_settings_reads_guardrail_configuration() -> None:
    settings = Settings(
        APP_ENV="test",
        GUARDRAILS_ENABLED=False,
        GUARDRAILS_AUDIT_ENABLED=True,
        GUARDRAILS_DEFAULT_BLOCK_MESSAGE="安全策略已拦截。",
    )

    assert settings.guardrails_enabled is False
    assert settings.guardrails_audit_enabled is True
    assert settings.guardrails_default_block_message == "安全策略已拦截。"


def test_settings_reads_rag_and_embedding_configuration() -> None:
    settings = Settings(
        APP_ENV="test",
        QDRANT_URL="http://127.0.0.1:6333",
        QDRANT_COLLECTION_PREFIX="ai_agent_test",
        EMBEDDING_PROVIDER="local_hash",
        EMBEDDING_MODEL="local-hash-v1",
        EMBEDDING_DIMENSION=64,
        RAG_TOP_K=12,
        RAG_FINAL_TOP_N=4,
        RAG_SCORE_THRESHOLD=0.2,
        RAG_CONTEXT_MAX_CHARS=2400,
        KNOWLEDGE_COLLECTION_TIMEOUT_SECONDS=8,
        KNOWLEDGE_COLLECTION_MAX_CHARS=3200,
        KNOWLEDGE_DOCUMENTS_PATH="./knowledge/test-love-master",
    )

    assert settings.qdrant_url == "http://127.0.0.1:6333"
    assert settings.qdrant_collection_prefix == "ai_agent_test"
    assert settings.embedding_provider == "local_hash"
    assert settings.embedding_model == "local-hash-v1"
    assert settings.embedding_dimension == 64
    assert settings.rag_top_k == 12
    assert settings.rag_final_top_n == 4
    assert settings.rag_score_threshold == 0.2
    assert settings.rag_context_max_chars == 2400
    assert settings.knowledge_collection_timeout_seconds == 8
    assert settings.knowledge_collection_max_chars == 3200
    assert settings.knowledge_documents_path == "./knowledge/test-love-master"
