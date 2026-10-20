"""User reads and administrator account management."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, pagination_params, require_roles
from app.core.database import get_db
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.auth import StaffUserCreate, UserAdminUpdate
from app.schemas.common import Page, PageParams
from app.schemas.user import UserRead
from app.services import users as user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=Page[UserRead])
def list_users(
    role: UserRole | None = None,
    is_active: bool | None = None,
    department_id: uuid.UUID | None = None,
    q: str | None = Query(default=None, max_length=200),
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[UserRead]:
    return user_service.list_accounts(
        db,
        params,
        current_user,
        role=role,
        is_active=is_active,
        department_id=department_id,
        query=q,
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: StaffUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.system_admin)),
) -> UserRead:
    return user_service.create_staff(db, payload, current_user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return user_service.get_account(db, user_id, current_user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.system_admin)),
) -> UserRead:
    return user_service.update_account(db, user_id, payload, current_user)
