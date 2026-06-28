from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = Field(default="AI 多智能体平台", validation_alias="APP_NAME")
    app_env: str = Field(default="test", validation_alias="APP_ENV")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    server_host: str = Field(default="127.0.0.1", validation_alias="SERVER_HOST")
    server_port: int = Field(default=8000, validation_alias="SERVER_PORT")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    cors_allowed_origins_raw: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5174,http://localhost:5174",
        validation_alias="CORS_ALLOWED_ORIGINS",
    )

    secret_key: str = Field(default="dev-change-me", validation_alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=1440,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_minutes: int = Field(
        default=43200,
        validation_alias="REFRESH_TOKEN_EXPIRE_MINUTES",
    )

    database_url: str = Field(
        default="mysql+pymysql://ai_agent:ai_agent_password@127.0.0.1:3306/ai_agent_dev?charset=utf8mb4",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://127.0.0.1:6379/0", validation_alias="REDIS_URL")
    llm_model: str = Field(
        default="openai/gpt-4.1-mini",
        validation_alias="LLM_MODEL",
    )
    llm_api_key: str = Field(default="", validation_alias="LLM_API_KEY")
    llm_base_url: str = Field(default="", validation_alias="LLM_BASE_URL")
    llm_temperature: float = Field(default=0.7, validation_alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1200, validation_alias="LLM_MAX_TOKENS")
    llm_timeout_seconds: int = Field(default=60, validation_alias="LLM_TIMEOUT_SECONDS")
    llm_max_retries: int = Field(default=3, validation_alias="LLM_MAX_RETRIES")
    vector_store_provider: str = Field(default="qdrant", validation_alias="VECTOR_STORE_PROVIDER")
    qdrant_url: str = Field(default="http://127.0.0.1:6333", validation_alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", validation_alias="QDRANT_API_KEY")
    qdrant_collection_prefix: str = Field(
        default="ai_agent_dev",
        validation_alias="QDRANT_COLLECTION_PREFIX",
    )
    embedding_provider: str = Field(default="local_hash", validation_alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="local-hash-v1", validation_alias="EMBEDDING_MODEL")
    embedding_base_url: str = Field(default="", validation_alias="EMBEDDING_BASE_URL")
    embedding_api_key: str = Field(default="", validation_alias="EMBEDDING_API_KEY")
    embedding_dimension: int = Field(default=64, validation_alias="EMBEDDING_DIMENSION")
    rag_top_k: int = Field(default=20, validation_alias="RAG_TOP_K")
    rag_final_top_n: int = Field(default=5, validation_alias="RAG_FINAL_TOP_N")
    rag_score_threshold: float = Field(default=0.1, validation_alias="RAG_SCORE_THRESHOLD")
    rag_context_max_chars: int = Field(default=3000, validation_alias="RAG_CONTEXT_MAX_CHARS")
    knowledge_collection_timeout_seconds: int = Field(
        default=15,
        validation_alias="KNOWLEDGE_COLLECTION_TIMEOUT_SECONDS",
    )
    knowledge_collection_max_chars: int = Field(
        default=6000,
        validation_alias="KNOWLEDGE_COLLECTION_MAX_CHARS",
    )
    knowledge_documents_path: str = Field(
        default="./knowledge/love_master",
        validation_alias="KNOWLEDGE_DOCUMENTS_PATH",
    )
    storage_provider: str = Field(default="local", validation_alias="STORAGE_PROVIDER")
    mcp_enabled: bool = Field(default=True, validation_alias="MCP_ENABLED")
    sandbox_enabled: bool = Field(default=True, validation_alias="SANDBOX_ENABLED")
    guardrails_enabled: bool = Field(default=True, validation_alias="GUARDRAILS_ENABLED")
    guardrails_audit_enabled: bool = Field(
        default=True,
        validation_alias="GUARDRAILS_AUDIT_ENABLED",
    )
    guardrails_default_block_message: str = Field(
        default="这个请求可能涉及安全或隐私风险，我不能按这个方向继续。",
        validation_alias="GUARDRAILS_DEFAULT_BLOCK_MESSAGE",
    )

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
