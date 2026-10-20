"""User reads and administrator account provisioning."""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.passwords import hash_password
from app.domain.enums import AuditAction, UserRole
from app.models.user import User
from app.repositories.users import get_user, list_users
from app.schemas.auth import StaffUserCreate, UserAdminUpdate
from app.schemas.common import Page, PageParams
from app.schemas.mappers import user_to_read
from app.schemas.user import UserRead
from app.services.audit import record_audit
from app.services.authorization import STAFF_ROLES, forbid
from app.services.lookups import require_active_department

_USER_MISSING = AppError("not_found", "User not found.", 404)


def list_accounts(
    db: Session,
    params: PageParams,
    viewer: User,
    *,
    role: UserRole | None,
    is_active: bool | None,
    department_id: uuid.UUID | None,
    query: str | None,
) -> Page[UserRead]:
    roles: tuple[UserRole, ...] | None = None
    if viewer.role == UserRole.citizen:
        raise forbid("You do not have permission to list users.")
    if viewer.role == UserRole.department_officer:
        if viewer.department_id is None:
            raise forbid("Your account is not assigned to a department.")
        if department_id is not None and department_id != viewer.department_id:
            raise forbid("You can only list users in your department.")
        if role == UserRole.citizen:
            raise forbid("You do not have permission to list citizen accounts.")
        department_id = viewer.department_id
        if role is None:
            roles = STAFF_ROLES
    elif viewer.role == UserRole.grievance_officer:
        if role == UserRole.citizen:
            raise forbid("You do not have permission to list citizen accounts.")
        if role is None:
            roles = STAFF_ROLES
    elif viewer.role != UserRole.system_admin:
        raise forbid("You do not have permission to list users.")

    rows, total = list_users(
        db,
        params,
        role=role,
        is_active=is_active,
        department_id=department_id,
        query=query,
        roles=roles,
    )
    return Page(
        items=[user_to_read(row) for row in rows],
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


def get_account(db: Session, user_id: uuid.UUID, viewer: User) -> UserRead:
    user = get_user(db, user_id)
    if user is None or not _can_view_user(viewer, user):
        raise _USER_MISSING
    return user_to_read(user)


def create_staff(db: Session, payload: StaffUserCreate, actor: User) -> UserRead:
    if actor.role != UserRole.system_admin:
        raise forbid("Only a system administrator can create staff accounts.")
    if payload.role == UserRole.department_officer and payload.department_id is None:
        raise AppError(
            "validation_error",
            "A department officer must belong to a department.",
            422,
        )
    if payload.department_id is not None:
        require_active_department(db, payload.department_id)
    user = User(
        display_name=payload.display_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        email_verified=True,
        role=payload.role,
        is_active=True,
        department_id=payload.department_id,
        designation=payload.designation,
        ward_or_zone=payload.ward_or_zone,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        raise AppError(
            "duplicate_email",
            "An account with this email already exists.",
            409,
        ) from exc
    record_audit(
        db,
        action=AuditAction.ACCOUNT_CREATED,
        entity_type="user",
        entity_id=user.id,
        actor_user_id=actor.id,
        summary="Staff account created.",
        event_metadata={"role": payload.role.value},
    )
    db.flush()
    created = get_user(db, user.id)
    if created is None:
        raise AppError("not_found", "User not found.", 404)
    return user_to_read(created)


def update_account(
    db: Session,
    user_id: uuid.UUID,
    payload: UserAdminUpdate,
    actor: User,
) -> UserRead:
    if actor.role != UserRole.system_admin:
        raise forbid("Only a system administrator can update accounts.")
    user = get_user(db, user_id)
    if user is None:
        raise _USER_MISSING
    if payload.department_id is not None and payload.clear_department:
        raise AppError(
            "validation_error",
            "Send either department_id or clear_department, not both.",
            422,
        )

    changed_fields: list[str] = []
    if payload.role is not None and payload.role != user.role:
        if user.id == actor.id:
            raise forbid("You cannot change your own role.")
        previous_role = user.role
        user.role = payload.role
        record_audit(
            db,
            action=AuditAction.ROLE_CHANGED,
            entity_type="user",
            entity_id=user.id,
            actor_user_id=actor.id,
            summary="Account role changed.",
            event_metadata={
                "previous_role": previous_role.value,
                "new_role": payload.role.value,
            },
        )
    if payload.is_active is not None and payload.is_active != user.is_active:
        if user.id == actor.id and payload.is_active is False:
            raise forbid("You cannot deactivate your own account.")
        user.is_active = payload.is_active
        changed_fields.append("is_active")
    if payload.clear_department and user.department_id is not None:
        user.department_id = None
        changed_fields.append("department_id")
    elif payload.department_id is not None and payload.department_id != user.department_id:
        require_active_department(db, payload.department_id)
        user.department_id = payload.department_id
        changed_fields.append("department_id")
    if payload.designation is not None and payload.designation != user.designation:
        user.designation = payload.designation
        changed_fields.append("designation")
    if payload.ward_or_zone is not None and payload.ward_or_zone != user.ward_or_zone:
        user.ward_or_zone = payload.ward_or_zone
        changed_fields.append("ward_or_zone")

    if user.role == UserRole.department_officer and user.department_id is None:
        raise AppError(
            "validation_error",
            "A department officer must belong to a department.",
            422,
        )
    if changed_fields:
        record_audit(
            db,
            action=AuditAction.ACCOUNT_UPDATED,
            entity_type="user",
            entity_id=user.id,
            actor_user_id=actor.id,
            summary="Account updated.",
            event_metadata={"fields": changed_fields},
        )
    db.flush()
    refreshed = get_user(db, user.id)
    if refreshed is None:
        raise _USER_MISSING
    return user_to_read(refreshed)


def _can_view_user(viewer: User, user: User) -> bool:
    if viewer.role == UserRole.system_admin or viewer.id == user.id:
        return True
    if user.role == UserRole.citizen:
        return False
    if viewer.role == UserRole.grievance_officer:
        return True
    if viewer.role == UserRole.department_officer:
        return (
            viewer.department_id is not None
            and user.department_id == viewer.department_id
            and user.role in STAFF_ROLES
        )
    return False
