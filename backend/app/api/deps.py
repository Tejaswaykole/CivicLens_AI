"""Shared route dependencies."""

import uuid

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.tokens import TokenError, read_access_token_subject
from app.domain.enums import UserRole
from app.models.user import User
from app.repositories.users import get_user
from app.schemas.common import PageParams

_bearer = HTTPBearer(auto_error=False)


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def get_access_token_subject(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> uuid.UUID:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise AppError("not_authenticated", "Authentication is required.", 401)
    try:
        return read_access_token_subject(credentials.credentials)
    except TokenError as exc:
        raise AppError("invalid_token", "Invalid or expired token.", 401) from exc


def get_current_user(
    user_id: uuid.UUID = Depends(get_access_token_subject),
    db: Session = Depends(get_db),
) -> User:
    user = get_user(db, user_id)
    if user is None:
        raise AppError("invalid_token", "Invalid or expired token.", 401)
    if not user.is_active:
        raise AppError("inactive_account", "This account is inactive.", 401)
    return user


def require_roles(*roles: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AppError("forbidden", "You do not have permission to perform this action.", 403)
        return user

    return checker
