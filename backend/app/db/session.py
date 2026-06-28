from collections.abc import Callable

from sqlalchemy import Engine, create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db import models  # noqa: F401

SessionFactory = Callable[[], Session]


def create_database_engine(database_url: str) -> Engine:
    connect_args = {}
    engine_kwargs = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if database_url.endswith(":memory:"):
            engine_kwargs["poolclass"] = StaticPool

    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_database_engine(database_url)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_db_and_tables(session_factory: sessionmaker[Session]) -> None:
    engine = session_factory.kw["bind"]
    Base.metadata.create_all(engine)
    _apply_compatibility_migrations(engine)


def _apply_compatibility_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    if "conversation_messages" not in inspector.get_table_names():
        return

    message_columns = {column["name"] for column in inspector.get_columns("conversation_messages")}
    if "citations" in message_columns:
        return

    with engine.begin() as connection:
        if engine.dialect.name == "mysql":
            connection.execute(text("ALTER TABLE conversation_messages ADD COLUMN citations JSON NULL"))
        else:
            connection.execute(
                text("ALTER TABLE conversation_messages ADD COLUMN citations JSON DEFAULT '[]'")
            )
