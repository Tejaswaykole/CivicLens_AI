"""Synchronous SQLAlchemy session management."""

import logging
from collections.abc import Generator
from typing import Literal

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def reset_engine() -> None:
    """Drop the cached engine. Used when tests change DATABASE_URL."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def _is_transaction_pooler(database_url: str) -> bool:
    """Detect whether connection string targets a transaction-mode pooler (such as Supabase port 6543)."""
    try:
        from sqlalchemy.engine.url import make_url

        url = make_url(database_url)
        # Port 6543 is Supabase's standard transaction pooler port.
        # Query parameter pooler=transaction is also respected if explicitly supplied.
        if url.port == 6543 or url.query.get("pooler") == "transaction":
            return True
        return False
    except Exception:
        return False


def get_connect_args(database_url: str) -> dict:
    """Return driver connection arguments appropriate for the configured host and pooler."""
    connect_args = {}
    if _is_transaction_pooler(database_url):
        connect_args["prepare_threshold"] = None
    return connect_args


def get_engine() -> Engine | None:
    global _engine, _session_factory
    settings = get_settings()
    if not settings.database_url:
        return None
    if _engine is None:
        connect_args = get_connect_args(settings.database_url)

        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args=connect_args,
        )
        _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def check_database() -> Literal["ok", "unavailable", "not_configured"]:
    """Return ok, not_configured, or unavailable. Never claims success without SELECT 1."""
    if get_engine() is None:
        return "not_configured"
    engine = get_engine()
    assert engine is not None
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        logger.warning("Database health check failed (%s).", type(exc).__name__)
        return "unavailable"


def get_db() -> Generator[Session, None, None]:
    get_engine()
    if _session_factory is None:
        from app.core.errors import AppError

        raise AppError(
            "database_not_configured",
            "DATABASE_URL is not configured.",
            status_code=503,
        )
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
