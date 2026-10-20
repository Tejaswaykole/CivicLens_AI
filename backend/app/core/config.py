"""Environment-based settings. Credentials are never hardcoded."""

from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "CivicLens AI"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cors_allow_credentials: bool = False
    seed_label: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def blank_database_url(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value[len("postgresql://") :]
        url = make_url(value)
        if url.get_backend_name() != "postgresql":
            raise ValueError("DATABASE_URL must use PostgreSQL. SQLite is not supported.")
        return value

    @field_validator("app_env")
    @classmethod
    def normalize_env(cls, value: str) -> str:
        return value.strip().lower()

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @model_validator(mode="after")
    def reject_unsafe_cors(self) -> "Settings":
        if self.cors_allow_credentials and "*" in self.cors_origin_list:
            raise ValueError("CORS_ALLOW_CREDENTIALS cannot be combined with a wildcard origin.")
        return self

    def database_target_label(self) -> str:
        """Host and database name with the password hidden, for logs and errors."""
        if not self.database_url:
            return "not configured"
        return make_url(self.database_url).render_as_string(hide_password=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
