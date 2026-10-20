"""Read-only user queries for Phase 3."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import UserRole
from app.repositories.users import get_user, list_users
from app.schemas.common import Page, PageParams
from app.schemas.mappers import user_to_read
from app.schemas.user import UserRead


def list_accounts(
    db: Session,
    params: PageParams,
    *,
    role: UserRole | None,
    is_active: bool | None,
    department_id: uuid.UUID | None,
    query: str | None,
) -> Page[UserRead]:
    rows, total = list_users(
        db,
        params,
        role=role,
        is_active=is_active,
        department_id=department_id,
        query=query,
    )
    return Page(
        items=[user_to_read(row) for row in rows],
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


def get_account(db: Session, user_id: uuid.UUID) -> UserRead:
    user = get_user(db, user_id)
    if user is None:
        raise AppError("not_found", "User not found.", 404)
    return user_to_read(user)
