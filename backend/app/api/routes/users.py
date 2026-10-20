"""User reads. These routes are not authenticated."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import pagination_params
from app.core.database import get_db
from app.domain.enums import UserRole
from app.schemas.common import Page, PageParams
from app.schemas.user import UserRead
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Page[UserRead])
def list_users(
    role: UserRole | None = None,
    is_active: bool | None = None,
    department_id: uuid.UUID | None = None,
    q: str | None = Query(default=None, max_length=200),
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
) -> Page[UserRead]:
    """List users. Unprotected in Phase 3. Password hashes are never returned."""
    return user_service.list_accounts(
        db,
        params,
        role=role,
        is_active=is_active,
        department_id=department_id,
        query=q,
    )


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserRead:
    """Fetch one user. Unprotected in Phase 3. Password hashes are never returned."""
    return user_service.get_account(db, user_id)
