"""Registration and login. Public registration always creates an unverified citizen."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.passwords import hash_password, verify_password
from app.core.tokens import create_access_token
from app.domain.enums import AuditAction, UserRole
from app.models.user import User
from app.repositories.users import get_user_by_email
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerificationResponse,
)
from app.services.audit import record_audit


def _duplicate_email() -> AppError:
    return AppError("duplicate_email", "An account with this email already exists.", 409)


def _invalid_credentials() -> AppError:
    return AppError("invalid_credentials", "Invalid email or password.", 401)


def _debug_token(token: str) -> str | None:
    settings = get_settings()
    if settings.email_verification_debug and settings.app_env in {"development", "test"}:
        return token
    return None


def _store_verification_token(user: User) -> str:
    token = secrets.token_urlsafe(32)
    settings = get_settings()
    user.email_verification_token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    user.email_verification_expires_at = datetime.now(UTC) + timedelta(
        hours=settings.email_verification_ttl_hours
    )
    return token


def register_citizen(db: Session, payload: RegisterRequest) -> RegisterResponse:
    user = User(
        display_name=payload.display_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        email_verified=False,
        role=UserRole.citizen,
        is_active=True,
        ward_or_zone=payload.ward_or_zone,
    )
    verification_token = _store_verification_token(user)
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        raise _duplicate_email() from exc
    record_audit(
        db,
        action=AuditAction.ACCOUNT_CREATED,
        entity_type="user",
        entity_id=user.id,
        actor_user_id=None,
        summary="Citizen account created.",
        event_metadata={"role": UserRole.citizen.value},
    )
    db.flush()
    token, expires_in = create_access_token(user.id)
    return RegisterResponse(
        access_token=token,
        expires_in=expires_in,
        dev_verification_token=_debug_token(verification_token),
    )


def verify_email(db: Session, token: str) -> VerificationResponse:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    user = db.scalar(select(User).where(User.email_verification_token_hash == digest))
    expires_at = user.email_verification_expires_at if user is not None else None
    if user is None or expires_at is None or expires_at < datetime.now(UTC):
        raise AppError(
            "invalid_verification_token",
            "Invalid or expired verification token.",
            400,
        )
    user.email_verified = True
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None
    record_audit(
        db,
        action=AuditAction.ACCOUNT_UPDATED,
        entity_type="user",
        entity_id=user.id,
        actor_user_id=user.id,
        summary="Email address verified.",
        event_metadata={"fields": ["email_verified"]},
    )
    db.flush()
    return VerificationResponse(email_verified=True)


def refresh_verification(db: Session, user: User) -> VerificationResponse:
    if user.email_verified:
        return VerificationResponse(email_verified=True)
    token = _store_verification_token(user)
    db.flush()
    return VerificationResponse(
        email_verified=False,
        dev_verification_token=_debug_token(token),
    )


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = get_user_by_email(db, payload.email)
    password_hash = user.password_hash if user is not None else None
    if not verify_password(payload.password, password_hash) or user is None or not user.is_active:
        raise _invalid_credentials()
    token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=expires_in)
