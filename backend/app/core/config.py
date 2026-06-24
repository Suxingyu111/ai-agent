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
        default="http://127.0.0.1:5173",
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
    default_llm_provider: str = Field(default="openrouter", validation_alias="DEFAULT_LLM_PROVIDER")
    default_chat_model: str = Field(
        default="openai/gpt-4.1-mini",
        validation_alias="DEFAULT_CHAT_MODEL",
    )
    vector_store_provider: str = Field(default="qdrant", validation_alias="VECTOR_STORE_PROVIDER")
    storage_provider: str = Field(default="local", validation_alias="STORAGE_PROVIDER")
    mcp_enabled: bool = Field(default=True, validation_alias="MCP_ENABLED")
    sandbox_enabled: bool = Field(default=True, validation_alias="SANDBOX_ENABLED")

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
