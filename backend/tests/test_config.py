"""Configuration guards."""

import asyncio

import pytest
from pydantic import ValidationError
from uvicorn.config import Config
from uvicorn.lifespan.on import LifespanOn

from app.core.bind import BindSecurityError
from app.core.config import Settings, clear_settings_cache
from app.core.tokens import host_is_loopback
from app.main import create_app


def test_sqlite_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite:///civiclens.db")


def test_blank_database_url_means_unconfigured() -> None:
    settings = Settings(database_url="  ")
    assert settings.database_url is None


def test_postgres_url_is_normalized_to_psycopg() -> None:
    settings = Settings(database_url="postgresql://user:secret@localhost:5432/civiclens")
    assert settings.database_url is not None
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert "secret" not in settings.database_target_label()


def test_direct_url_is_normalized_and_validated() -> None:
    with pytest.raises(ValidationError):
        Settings(direct_url="sqlite:///direct.db")

    settings = Settings(direct_url="postgresql://user:secret@localhost:5432/civiclens_direct")
    assert settings.direct_url is not None
    assert settings.direct_url.startswith("postgresql+psycopg://")
    assert "secret" not in settings.direct_target_label()

    blank = Settings(direct_url="   ")
    assert blank.direct_url is None
    assert blank.direct_target_label() == "not configured"


def test_alembic_database_url_prefers_direct_url(monkeypatch) -> None:
    import importlib.util
    from pathlib import Path

    backend_root = Path(__file__).resolve().parents[1]
    env_py_path = backend_root / "alembic" / "env.py"
    spec = importlib.util.spec_from_file_location("alembic_env_module", str(env_py_path))
    assert spec is not None and spec.loader is not None
    alembic_env = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alembic_env)

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/runtime_db")
    monkeypatch.setenv("DIRECT_URL", "postgresql://user:pass@localhost:5432/direct_db")
    clear_settings_cache()
    # DIRECT_URL takes precedence
    assert "direct_db" in alembic_env.database_url()

    # When DIRECT_URL is absent, falls back to DATABASE_URL
    monkeypatch.delenv("DIRECT_URL", raising=False)
    clear_settings_cache()
    assert "runtime_db" in alembic_env.database_url()
    clear_settings_cache()


def test_conditional_pooler_detection_and_prepared_statements() -> None:
    from app.core.database import _is_transaction_pooler, get_connect_args

    # Standard port 5432 or default local DB is not a transaction pooler
    assert not _is_transaction_pooler("postgresql+psycopg://user:pass@localhost:5432/civiclens")
    assert get_connect_args("postgresql+psycopg://user:pass@localhost:5432/civiclens") == {}

    # Supabase standard transaction pooler port 6543
    assert _is_transaction_pooler("postgresql+psycopg://user:pass@pooler.supabase.com:6543/postgres")
    assert get_connect_args("postgresql+psycopg://user:pass@pooler.supabase.com:6543/postgres") == {
        "prepare_threshold": None
    }

    # Explicit pooler=transaction query param
    assert _is_transaction_pooler("postgresql+psycopg://user:pass@localhost:5432/civiclens?pooler=transaction")
    assert get_connect_args("postgresql+psycopg://user:pass@localhost:5432/civiclens?pooler=transaction") == {
        "prepare_threshold": None
    }


def test_wildcard_cors_with_credentials_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins="*", cors_allow_credentials=True)


def test_placeholder_jwt_secret_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            database_url="postgresql://user:secret@localhost:5432/civiclens",
            jwt_secret="replace-with-a-long-random-secret",
        )


def test_short_jwt_secret_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            database_url="postgresql://user:secret@localhost:5432/civiclens",
            jwt_secret="too-short",
        )


def test_loopback_development_starts_without_a_secret() -> None:
    settings = Settings(app_env="development", api_host="127.0.0.1", jwt_secret=None)
    assert settings.jwt_secret is None


def test_non_loopback_host_requires_a_strong_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="development", api_host="0.0.0.0", jwt_secret=None)


def test_repeated_character_secret_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            database_url="postgresql://user:secret@localhost:5432/civiclens",
            jwt_secret="a" * 40,
        )


def test_production_rejects_verification_debug() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            database_url="postgresql://user:secret@localhost:5432/civiclens",
            jwt_secret="abcdefghij" * 4,
            email_verification_debug=True,
        )


def test_loopback_range_is_recognized() -> None:
    assert host_is_loopback("127.0.0.1")
    assert host_is_loopback("127.0.0.2")
    assert host_is_loopback("localhost")
    assert host_is_loopback("::1")
    assert not host_is_loopback("0.0.0.0")
    assert not host_is_loopback("::")


def test_loopback_bind_allows_development_without_a_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare_bind_env(monkeypatch, api_host="localhost", jwt_secret="")
    try:
        config = _load_factory(uvicorn_host="127.0.0.1")
    finally:
        clear_settings_cache()
    assert config.loaded


def test_public_bind_cannot_hide_behind_loopback_api_host(monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare_bind_env(monkeypatch, api_host="127.0.0.1", jwt_secret="")
    try:
        with pytest.raises(BindSecurityError, match="binding to 0.0.0.0"):
            _load_factory(uvicorn_host="0.0.0.0")
    finally:
        clear_settings_cache()


def test_public_bind_still_disagrees_when_a_strong_secret_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prepare_bind_env(monkeypatch, api_host="127.0.0.1", jwt_secret="abcdefghij" * 4)
    try:
        with pytest.raises(BindSecurityError, match="binding to 0.0.0.0"):
            _load_factory(uvicorn_host="0.0.0.0")
    finally:
        clear_settings_cache()


def test_matching_public_bind_accepts_a_strong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare_bind_env(monkeypatch, api_host="0.0.0.0", jwt_secret="abcdefghij" * 4)
    try:
        config = _load_factory(uvicorn_host="0.0.0.0")
    finally:
        clear_settings_cache()
    assert config.loaded


def test_production_loopback_bind_requires_a_strong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare_bind_env(
        monkeypatch,
        app_env="production",
        api_host="127.0.0.1",
        jwt_secret="",
        database_url="postgresql://user:secret@localhost:5432/civiclens",
    )
    try:
        with pytest.raises(ValidationError):
            _load_factory(uvicorn_host="127.0.0.1")
    finally:
        clear_settings_cache()


def test_imported_app_rejects_a_later_public_bind(monkeypatch: pytest.MonkeyPatch) -> None:
    _prepare_bind_env(monkeypatch, api_host="127.0.0.1", jwt_secret="")
    try:
        built = create_app()
        config = Config(built, host="0.0.0.0", port=9, log_config=None)
        config.loaded = True
        config.loaded_app = built
        config.interface = "asgi3"
        lifespan = LifespanOn(config)

        async def start() -> bool:
            await asyncio.wait_for(lifespan.startup(), timeout=2)
            return lifespan.should_exit

        assert asyncio.run(start()) is True
    finally:
        clear_settings_cache()


def _prepare_bind_env(
    monkeypatch: pytest.MonkeyPatch,
    *,
    api_host: str,
    jwt_secret: str,
    app_env: str = "development",
    database_url: str = "",
) -> None:
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("API_HOST", api_host)
    monkeypatch.setenv("JWT_SECRET", jwt_secret)
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("EMAIL_VERIFICATION_DEBUG", "false")
    clear_settings_cache()


def _load_factory(uvicorn_host: str) -> Config:
    def factory() -> object:
        clear_settings_cache()
        return create_app()

    config = Config(factory, host=uvicorn_host, port=9, factory=True, log_config=None)
    config.load()
    return config
