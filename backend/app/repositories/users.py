"""User queries. Password hashes are deferred."""

import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, defer, joinedload

from app.domain.enums import UserRole
from app.models.user import User
from app.repositories.query import contains_pattern
from app.schemas.common import PageParams


def user_query() -> Select[tuple[User]]:
    return select(User).options(defer(User.password_hash), joinedload(User.department))


def get_user(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalar(user_query().where(User.id == user_id))


def list_users(
    db: Session,
    params: PageParams,
    *,
    role: UserRole | None,
    is_active: bool | None,
    department_id: uuid.UUID | None,
    query: str | None,
) -> tuple[list[User], int]:
    filters = []
    if role is not None:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if department_id is not None:
        filters.append(User.department_id == department_id)
    if query:
        pattern = contains_pattern(query.strip())
        filters.append(
            or_(
                User.display_name.ilike(pattern, escape="\\"),
                User.email.ilike(pattern, escape="\\"),
                User.designation.ilike(pattern, escape="\\"),
            )
        )
    stmt = user_query().where(*filters)
    total = db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
    rows = db.scalars(
        stmt.order_by(User.display_name.asc()).offset(params.offset).limit(params.page_size)
    ).unique()
    return list(rows), int(total)
