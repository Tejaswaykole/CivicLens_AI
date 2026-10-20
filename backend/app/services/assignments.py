"""Preserve assignment history and keep one current assignment per complaint."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import AuditAction, ComplaintStatus, NotificationType, UserRole
from app.domain.workflow import ASSIGNABLE_STATUSES
from app.models.assignment import ComplaintAssignment
from app.repositories.complaints import get_complaint_for_update
from app.schemas.assignment import AssignmentCreate
from app.schemas.complaint import AssignmentRead
from app.services.audit import record_audit
from app.services.complaints import _append_status, _detail
from app.services.lookups import require_active_department, require_active_user, require_user
from app.services.notifications import notify


def create_assignment(
    db: Session,
    complaint_id: uuid.UUID,
    payload: AssignmentCreate,
) -> AssignmentRead:
    complaint = get_complaint_for_update(db, complaint_id)
    if complaint is None:
        raise AppError("not_found", "Complaint not found.", 404)
    if complaint.status not in ASSIGNABLE_STATUSES:
        raise AppError(
            "invalid_status_transition",
            f"A complaint in status {complaint.status.value} cannot be assigned.",
            409,
        )

    department = require_active_department(db, payload.department_id)
    officer = None
    if payload.assigned_officer_id is not None:
        officer = require_active_user(db, payload.assigned_officer_id)
        if officer.role != UserRole.department_officer:
            raise AppError(
                "invalid_officer",
                "The assigned officer must have the department_officer role.",
                409,
            )
        if officer.department_id is not None and officer.department_id != department.id:
            raise AppError(
                "invalid_officer",
                "The officer is associated with a different department.",
                409,
            )

    actor_id = None
    if payload.actor_user_id is not None:
        actor_id = require_user(db, payload.actor_user_id).id

    db.execute(
        update(ComplaintAssignment)
        .where(
            ComplaintAssignment.complaint_id == complaint.id,
            ComplaintAssignment.is_current.is_(True),
        )
        .values(is_current=False)
    )
    db.flush()

    assigned_at = datetime.now(UTC)
    assignment = ComplaintAssignment(
        complaint_id=complaint.id,
        department_id=department.id,
        assigned_officer_id=officer.id if officer is not None else None,
        assigned_crew_unit=payload.assigned_crew_unit,
        note=payload.note,
        is_current=True,
        assigned_at=assigned_at,
    )
    db.add(assignment)
    complaint.department_id = department.id
    complaint.resolution_due_at = assigned_at + timedelta(hours=department.sla_target_hours)

    status_changed = False
    if complaint.status == ComplaintStatus.triaged:
        _append_status(
            db,
            complaint,
            new_status=ComplaintStatus.assigned,
            note=payload.note or f"Assigned to {department.code}.",
            actor_user_id=actor_id,
            actor_label=payload.actor_label,
        )
        status_changed = True

    db.flush()
    record_audit(
        db,
        action=AuditAction.ASSIGNMENT_CREATED,
        entity_type="complaint",
        entity_id=complaint.id,
        actor_user_id=actor_id,
        summary=f"Complaint {complaint.public_reference} assigned to {department.code}.",
        event_metadata={
            "public_reference": complaint.public_reference,
            "department_code": department.code,
            "status": complaint.status.value,
            "status_changed": status_changed,
        },
    )
    if officer is not None:
        notify(
            db,
            recipient_user_id=officer.id,
            notification_type=NotificationType.urgent,
            title=f"Assignment {complaint.public_reference}",
            message=f"Assigned to {department.code}.",
            link="/app/department/complaints",
        )
    db.flush()
    db.refresh(assignment)
    loaded = _detail(db, complaint.id)
    current = next(item for item in loaded.assignments if item.id == assignment.id)
    return current.model_copy(update={"complaint_status": complaint.status})
