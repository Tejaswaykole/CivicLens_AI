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
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    seed_dev_password: str | None = None
    api_host: str = "127.0.0.1"
    enable_api_docs: bool = False
    auth_login_rate_limit: str = "10/minute"
    auth_register_rate_limit: str = "5/minute"
    email_verification_debug: bool = False
    email_verification_ttl_hours: int = 24
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None

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

    @field_validator(
        "jwt_secret",
        "seed_dev_password",
        "smtp_host",
        "smtp_username",
        "smtp_password",
        "email_from",
        mode="before",
    )
    @classmethod
    def blank_secret(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def only_hs256(cls, value: str) -> str:
        if value.strip().upper() != "HS256":
            raise ValueError("JWT_ALGORITHM must be HS256.")
        return "HS256"

    @field_validator("jwt_access_token_expire_minutes")
    @classmethod
    def expire_window(cls, value: int) -> int:
        if value < 5 or value > 24 * 60:
            raise ValueError("JWT access token lifetime must be between 5 and 1440 minutes.")
        return value

    @field_validator("api_host")
    @classmethod
    def normalize_host(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("API_HOST cannot be empty.")
        return cleaned

    @field_validator("auth_login_rate_limit", "auth_register_rate_limit")
    @classmethod
    def rate_limit_text(cls, value: str) -> str:
        from limits import parse

        parsed = parse(value.strip())
        if parsed.amount < 1:
            raise ValueError("Auth rate limits must allow at least one request per window.")
        return value.strip()

    @field_validator("email_verification_ttl_hours")
    @classmethod
    def verification_window(cls, value: int) -> int:
        if value < 1 or value > 72:
            raise ValueError("Email verification lifetime must be between 1 and 72 hours.")
        return value

    @field_validator("smtp_port", mode="before")
    @classmethod
    def blank_port(cls, value: object) -> object:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @model_validator(mode="after")
    def reject_unsafe_cors(self) -> "Settings":
        if self.cors_allow_credentials and "*" in self.cors_origin_list:
            raise ValueError("CORS_ALLOW_CREDENTIALS cannot be combined with a wildcard origin.")
        from app.core.tokens import host_is_loopback, secret_is_acceptable

        # API_HOST is only the declared address. enforce_server_bind also reads
        # the host Uvicorn is actually using, so the two cannot quietly differ.
        exposed = self.app_env == "production" or not host_is_loopback(self.api_host)
        if exposed and not secret_is_acceptable(self.jwt_secret):
            raise ValueError(
                "Set a JWT_SECRET of at least 32 characters with 8 or more distinct "
                "characters when APP_ENV=production or API_HOST is not loopback."
            )
        if self.app_env == "production" and self.email_verification_debug:
            raise ValueError("EMAIL_VERIFICATION_DEBUG cannot be enabled when APP_ENV=production.")
        if self.app_env == "production" and self.database_url is None:
            raise ValueError("Production startup requires DATABASE_URL.")
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
