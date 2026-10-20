"""Shared existence checks. A matching user id is not treated as authentication."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.department import Department
from app.models.user import User
from app.repositories.departments import get_department
from app.repositories.users import get_user


def require_user(db: Session, user_id: uuid.UUID) -> User:
    user = get_user(db, user_id)
    if user is None:
        raise AppError("not_found", "User not found.", 404)
    return user


def require_active_user(db: Session, user_id: uuid.UUID) -> User:
    user = require_user(db, user_id)
    if not user.is_active:
        raise AppError("inactive_user", "The referenced user is inactive.", 409)
    return user


def require_department(db: Session, department_id: uuid.UUID) -> Department:
    department = get_department(db, department_id)
    if department is None:
        raise AppError("not_found", "Department not found.", 404)
    return department


def require_active_department(db: Session, department_id: uuid.UUID) -> Department:
    department = require_department(db, department_id)
    if not department.is_active:
        raise AppError("inactive_department", "The department is inactive.", 409)
    return department
