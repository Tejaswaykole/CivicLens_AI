"""Server-side access rules. A user id in a request body is never authority."""

import uuid

from app.core.errors import AppError
from app.domain.enums import ComplaintStatus, UserRole
from app.models.complaint import Complaint
from app.models.user import User

STAFF_ROLES = (
    UserRole.system_admin,
    UserRole.grievance_officer,
    UserRole.department_officer,
)
FIELD_STATUS_TARGETS = frozenset(
    {ComplaintStatus.assigned, ComplaintStatus.in_progress, ComplaintStatus.resolved}
)
TRIAGE_STATUS_TARGETS = frozenset(
    {ComplaintStatus.in_review, ComplaintStatus.triaged, ComplaintStatus.rejected}
)


def forbid(message: str) -> AppError:
    return AppError("forbidden", message, 403)


def hidden() -> AppError:
    return AppError("not_found", "Complaint not found.", 404)


def require_same_actor(claimed_user_id: uuid.UUID | None, actor: User, field_name: str) -> None:
    if claimed_user_id is not None and claimed_user_id != actor.id:
        raise forbid(f"{field_name} does not match the authenticated user.")


def scope_complaint_filters(actor: User, filters: dict) -> dict:
    scoped = dict(filters)
    if actor.role == UserRole.citizen:
        requested = scoped.get("citizen_id")
        if requested is not None and requested != actor.id:
            raise forbid("You can only list your own complaints.")
        scoped["citizen_id"] = actor.id
        return scoped
    if actor.role == UserRole.department_officer:
        if actor.department_id is None:
            raise forbid("Your account is not assigned to a department.")
        requested = scoped.get("department_id")
        if requested is not None and requested != actor.department_id:
            raise forbid("You can only list complaints for your department.")
        scoped["department_id"] = actor.department_id
        return scoped
    if actor.role in {UserRole.grievance_officer, UserRole.system_admin}:
        return scoped
    raise forbid("You do not have permission to list complaints.")


def ensure_can_view_complaint(actor: User, complaint: Complaint) -> None:
    if actor.role in {UserRole.grievance_officer, UserRole.system_admin}:
        return
    if actor.role == UserRole.citizen:
        if complaint.citizen_id != actor.id:
            raise hidden()
        return
    if actor.role == UserRole.department_officer:
        if actor.department_id is None or complaint.department_id != actor.department_id:
            raise hidden()
        return
    raise hidden()


def ensure_can_create_complaint(actor: User, citizen_id: uuid.UUID) -> None:
    if actor.role != UserRole.citizen:
        raise forbid("Only a citizen can register a complaint.")
    if citizen_id != actor.id:
        raise forbid("You can only register a complaint for your own account.")
    if not actor.email_verified:
        raise AppError(
            "email_unverified",
            "Verify your email before submitting a complaint.",
            403,
        )


def ensure_can_change_status(
    actor: User,
    complaint: Complaint,
    new_status: ComplaintStatus,
) -> None:
    if actor.role == UserRole.system_admin:
        return
    if actor.role == UserRole.grievance_officer:
        if new_status not in TRIAGE_STATUS_TARGETS:
            raise forbid("Grievance officers can record triage decisions only.")
        return
    if actor.role == UserRole.department_officer:
        if actor.department_id is None or complaint.department_id != actor.department_id:
            raise hidden()
        if new_status not in FIELD_STATUS_TARGETS:
            raise forbid("Department officers can update field progress only.")
        return
    raise forbid("You do not have permission to change this complaint.")


def ensure_can_assign(actor: User, complaint: Complaint, department_id: uuid.UUID) -> None:
    if actor.role in {UserRole.system_admin, UserRole.grievance_officer}:
        return
    if actor.role == UserRole.department_officer:
        if actor.department_id is None or complaint.department_id != actor.department_id:
            raise hidden()
        if department_id != actor.department_id:
            raise forbid("You cannot move a complaint to another department.")
        return
    raise forbid("You do not have permission to assign this complaint.")


def ensure_can_review(actor: User) -> None:
    if actor.role not in {UserRole.system_admin, UserRole.grievance_officer}:
        raise forbid("You do not have permission to review complaints.")


def ensure_can_read_audit(actor: User) -> None:
    if actor.role != UserRole.system_admin:
        raise forbid("Only a system administrator can read audit logs.")
