"""Public registration, login, and the current user profile."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError
from app.core.rate_limit import allow
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerificationResponse,
    VerifyEmailRequest,
)
from app.schemas.mappers import user_to_read
from app.schemas.user import UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_host(request: Request) -> str:
    if request.client is None or not request.client.host:
        return "unknown"
    return request.client.host


def limit_login(request: Request) -> None:
    settings = get_settings()
    if allow("auth-login", settings.auth_login_rate_limit, _client_host(request)):
        return
    raise AppError("rate_limited", "Too many attempts. Try again later.", 429)


def limit_register(request: Request) -> None:
    settings = get_settings()
    if allow("auth-register", settings.auth_register_rate_limit, _client_host(request)):
        return
    raise AppError("rate_limited", "Too many attempts. Try again later.", 429)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    _: None = Depends(limit_register),
    db: Session = Depends(get_db),
) -> RegisterResponse:
    """Create an unverified citizen. A role field is rejected."""
    return auth_service.register_citizen(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    _: None = Depends(limit_login),
    db: Session = Depends(get_db),
) -> TokenResponse:
    return auth_service.login(db, payload)


@router.post("/verify-email", response_model=VerificationResponse)
def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> VerificationResponse:
    return auth_service.verify_email(db, payload.token)


@router.post("/verification", response_model=VerificationResponse)
def refresh_verification(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VerificationResponse:
    return auth_service.refresh_verification(db, current_user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return user_to_read(current_user)
