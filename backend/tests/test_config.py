"""Configuration guards."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


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


def test_wildcard_cors_with_credentials_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins="*", cors_allow_credentials=True)
