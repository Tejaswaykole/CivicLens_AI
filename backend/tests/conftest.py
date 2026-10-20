"""PostgreSQL fixtures. Tests never connect unless TEST_DATABASE_URL names a _test database."""

import os
import secrets
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _is_safe_test_database(url: str) -> bool:
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql":
        return False
    name = parsed.database or ""
    return "_test" in name


@pytest.fixture(scope="session")
def postgres_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL", "").strip()
    if not url or not _is_safe_test_database(url):
        pytest.skip(
            "TEST_DATABASE_URL is not set to a PostgreSQL database whose name contains '_test'."
        )
    return url


@pytest.fixture(scope="session")
def migrated_engine(postgres_url: str) -> Generator[Engine, None, None]:
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["APP_ENV"] = "test"
    from alembic.config import Config

    from alembic import command
    from app.core.config import clear_settings_cache
    from app.core.database import get_engine, reset_engine

    clear_settings_cache()
    reset_engine()
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    command.upgrade(config, "head")
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Test database engine was not created.")
    yield engine


@pytest.fixture
def db_session(migrated_engine: Engine) -> Generator[Session, None, None]:
    connection = migrated_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session, postgres_url: str):
    previous = {
        "DATABASE_URL": os.environ.get("DATABASE_URL"),
        "APP_ENV": os.environ.get("APP_ENV"),
        "JWT_SECRET": os.environ.get("JWT_SECRET"),
        "API_HOST": os.environ.get("API_HOST"),
        "EMAIL_VERIFICATION_DEBUG": os.environ.get("EMAIL_VERIFICATION_DEBUG"),
        "AUTH_LOGIN_RATE_LIMIT": os.environ.get("AUTH_LOGIN_RATE_LIMIT"),
        "AUTH_REGISTER_RATE_LIMIT": os.environ.get("AUTH_REGISTER_RATE_LIMIT"),
    }
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["APP_ENV"] = "test"
    os.environ["API_HOST"] = "127.0.0.1"
    os.environ["EMAIL_VERIFICATION_DEBUG"] = "true"
    os.environ["AUTH_LOGIN_RATE_LIMIT"] = "30/minute"
    os.environ["AUTH_REGISTER_RATE_LIMIT"] = "20/minute"
    os.environ["JWT_SECRET"] = secrets.token_urlsafe(48)
    from app.core.rate_limit import reset_rate_limits

    reset_rate_limits()
    from fastapi.testclient import TestClient

    from app.core.config import clear_settings_cache
    from app.core.database import get_db, reset_engine
    from app.main import app

    clear_settings_cache()
    reset_engine()

    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    clear_settings_cache()
    reset_engine()
    for name, value in previous.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
