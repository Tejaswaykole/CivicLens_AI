"""JWT access tokens. The signing secret comes from the environment."""

import ipaddress
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import Settings, get_settings
from app.core.errors import AppError

_REJECTED_SECRETS = {
    "replace-with-a-long-random-secret",
    "change-me",
    "changeme",
    "secret",
    "jwt-secret",
}


class TokenError(Exception):
    """The access token is missing, invalid, or expired."""


def secret_is_acceptable(secret: str | None) -> bool:
    if secret is None:
        return False
    cleaned = secret.strip()
    if len(cleaned) < 32:
        return False
    if cleaned.lower() in _REJECTED_SECRETS:
        return False
    if len(set(cleaned)) < 8:
        return False
    return True


def host_is_loopback(host: str) -> bool:
    """True only for names that cannot accept traffic from another machine."""
    cleaned = host.strip().lower().strip("[]")
    if cleaned == "localhost":
        return True
    try:
        return ipaddress.ip_address(cleaned).is_loopback
    except ValueError:
        return False


def require_signing_secret(settings: Settings | None = None) -> str:
    current = settings or get_settings()
    if current.jwt_algorithm != "HS256":
        raise AppError("auth_not_configured", "JWT signing is not configured.", 503)
    if not secret_is_acceptable(current.jwt_secret):
        raise AppError("auth_not_configured", "JWT_SECRET is not configured.", 503)
    assert current.jwt_secret is not None
    return current.jwt_secret


def create_access_token(user_id: uuid.UUID, settings: Settings | None = None) -> tuple[str, int]:
    current = settings or get_settings()
    secret = require_signing_secret(current)
    expires_in = current.jwt_access_token_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires_in


def read_access_token_subject(token: str, settings: Settings | None = None) -> uuid.UUID:
    current = settings or get_settings()
    secret = require_signing_secret(current)
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "iat"]},
        )
        return uuid.UUID(str(payload["sub"]))
    except (InvalidTokenError, ValueError, TypeError) as exc:
        raise TokenError("Invalid or expired token.") from exc
