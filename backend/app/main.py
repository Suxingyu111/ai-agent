from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.agent_kernel.runtime.chat_model import LangChainChatModelClient
from app.agent_kernel.guardrails.pipeline import GuardrailPipeline, build_default_guardrail_pipeline
from app.core.config import Settings, get_settings
from app.db import create_db_and_tables, create_session_factory
from app.modules.conversations import ConversationService
from app.modules.knowledge import KnowledgeService


DEFAULT_DATABASE_URL = Settings.model_fields["database_url"].default


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title=app_settings.app_name,
        debug=app_settings.debug,
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=app_settings.api_v1_prefix)
    app.state.settings = app_settings
    guardrail_pipeline = (
        build_default_guardrail_pipeline()
        if app_settings.guardrails_enabled
        else GuardrailPipeline(interceptors=[])
    )
    model_client = None
    if app_settings.llm_api_key:
        model_client = LangChainChatModelClient(
            app_settings,
            guardrail_pipeline=guardrail_pipeline,
        )
    database_url = app_settings.database_url
    if app_settings.app_env == "test" and not database_url.startswith("sqlite"):
        database_url = "sqlite+pysqlite:///:memory:"
    session_factory = create_session_factory(database_url)

    def initialize_database() -> None:
        create_db_and_tables(session_factory)

    if settings is None:
        app.router.on_startup.append(initialize_database)
    else:
        initialize_database()

    knowledge_service = KnowledgeService(settings=app_settings, session_factory=session_factory)
    if settings is not None:
        knowledge_service.seed_default_documents()
    else:
        app.router.on_startup.append(knowledge_service.seed_default_documents)

    app.state.knowledge_service = knowledge_service
    app.state.conversation_service = ConversationService(
        model_client=model_client,
        guardrail_pipeline=guardrail_pipeline,
        session_factory=session_factory,
        knowledge_service=knowledge_service,
    )
    return app


app = create_app()
