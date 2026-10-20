"""Complaint creation, retrieval, and validated status changes."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import AuditAction, ComplaintStatus, NotificationType, UserRole
from app.domain.workflow import can_transition, format_public_reference, status_history_title
from app.models.complaint import Complaint
from app.models.complaint_status_history import ComplaintStatusHistory
from app.models.user import User
from app.repositories.complaints import (
    get_complaint_detail,
    get_complaint_for_update,
    latest_confirmed_priority,
    list_complaints,
)
from app.schemas.common import Page, PageParams
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintDetail,
    ComplaintRead,
    ComplaintStatusUpdate,
)
from app.schemas.mappers import complaint_to_detail, complaint_to_read
from app.services.audit import record_audit
from app.services.authorization import (
    ensure_can_change_status,
    ensure_can_create_complaint,
    ensure_can_view_complaint,
    require_same_actor,
    scope_complaint_filters,
)
from app.services.lookups import require_active_department, require_active_user
from app.services.notifications import notify


def allocate_public_reference(db: Session, *, year: int | None = None) -> str:
    sequence = db.execute(text("SELECT nextval('complaint_reference_seq')")).scalar_one()
    reference_year = year if year is not None else datetime.now(UTC).year
    return format_public_reference(reference_year, int(sequence))


def _detail(db: Session, complaint_id: uuid.UUID) -> ComplaintDetail:
    existing = db.get(Complaint, complaint_id)
    if existing is not None:
        db.expire(existing)
    complaint = get_complaint_detail(db, complaint_id)
    if complaint is None:
        raise AppError("not_found", "Complaint not found.", 404)
    return complaint_to_detail(
        complaint,
        confirmed_priority=latest_confirmed_priority(db, complaint.id),
    )


def list_all(
    db: Session,
    params: PageParams,
    actor: User,
    **filters,
) -> Page[ComplaintRead]:
    filters = scope_complaint_filters(actor, filters)
    rows, total = list_complaints(db, params, **filters)
    items = [
        complaint_to_read(complaint, confirmed_priority=priority) for complaint, priority in rows
    ]
    return Page(items=items, page=params.page, page_size=params.page_size, total=total)


def get_one(db: Session, complaint_id: uuid.UUID, actor: User) -> ComplaintDetail:
    complaint = get_complaint_detail(db, complaint_id)
    if complaint is None:
        raise AppError("not_found", "Complaint not found.", 404)
    ensure_can_view_complaint(actor, complaint)
    return complaint_to_detail(
        complaint,
        confirmed_priority=latest_confirmed_priority(db, complaint.id),
    )


def _append_status(
    db: Session,
    complaint: Complaint,
    *,
    new_status: ComplaintStatus,
    note: str | None,
    actor_user_id: uuid.UUID | None,
    actor_label: str | None,
) -> ComplaintStatus:
    previous = complaint.status
    if not can_transition(previous, new_status):
        raise AppError(
            "invalid_status_transition",
            f"Cannot change status from {previous.value} to {new_status.value}.",
            409,
        )
    complaint.status = new_status
    if new_status == ComplaintStatus.resolved:
        complaint.resolution_notes = note
    db.add(
        ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=previous,
            new_status=new_status,
            actor_user_id=actor_user_id,
            actor_label=actor_label,
            title=status_history_title(previous, new_status),
            note=note,
        )
    )
    return previous


def create_complaint(db: Session, payload: ComplaintCreate, actor: User) -> ComplaintDetail:
    ensure_can_create_complaint(actor, payload.citizen_id)
    citizen = require_active_user(db, payload.citizen_id)
    if payload.requested_department_id is not None:
        require_active_department(db, payload.requested_department_id)

    complaint = Complaint(
        public_reference=allocate_public_reference(db),
        citizen_id=citizen.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        location_address=payload.location_address,
        ward_zone=payload.ward_zone,
        requested_department_id=payload.requested_department_id,
        status=ComplaintStatus.submitted,
    )
    db.add(complaint)
    db.flush()
    db.add(
        ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status=ComplaintStatus.submitted,
            actor_user_id=citizen.id,
            actor_label=None,
            title=status_history_title(None, ComplaintStatus.submitted),
            note="Complaint registered.",
        )
    )
    record_audit(
        db,
        action=AuditAction.COMPLAINT_CREATED,
        entity_type="complaint",
        entity_id=complaint.id,
        actor_user_id=citizen.id,
        summary=f"Complaint {complaint.public_reference} registered.",
        event_metadata={
            "public_reference": complaint.public_reference,
            "category": complaint.category,
            "status": ComplaintStatus.submitted.value,
        },
    )
    ward = payload.ward_zone or "unspecified ward"
    notify(
        db,
        recipient_role=UserRole.grievance_officer,
        notification_type=NotificationType.info,
        title=f"New grievance {complaint.public_reference}",
        message=f"{payload.category} logged for {ward}.",
        link="/app/officer/inbox",
    )

    # Invoke AI inference safely. Does not overwrite officer-confirmed fields or fail transaction.
    from app.models.model_prediction import ModelPrediction
    from app.services.ai_inference import run_complaint_inference

    prediction_data = run_complaint_inference(payload.title, payload.description)
    if prediction_data is not None:
        prediction = ModelPrediction(
            complaint_id=complaint.id,
            model_identifier=prediction_data["model_identifier"],
            model_version=prediction_data["model_version"],
            predicted_category=prediction_data["predicted_category"],
            suggested_priority=prediction_data["suggested_priority"],
            confidence=prediction_data["confidence"],
            explanation=prediction_data["explanation"],
        )
        db.add(prediction)

    db.flush()
    return _detail(db, complaint.id)


def change_status(
    db: Session,
    complaint_id: uuid.UUID,
    payload: ComplaintStatusUpdate,
    actor: User,
) -> ComplaintDetail:
    complaint = get_complaint_for_update(db, complaint_id)
    if complaint is None:
        raise AppError("not_found", "Complaint not found.", 404)
    ensure_can_view_complaint(actor, complaint)
    ensure_can_change_status(actor, complaint, payload.status)
    require_same_actor(payload.actor_user_id, actor, "actor_user_id")
    actor_id = actor.id
    previous = _append_status(
        db,
        complaint,
        new_status=payload.status,
        note=payload.note,
        actor_user_id=actor_id,
        actor_label=payload.actor_label,
    )
    record_audit(
        db,
        action=AuditAction.STATUS_CHANGE,
        entity_type="complaint",
        entity_id=complaint.id,
        actor_user_id=actor_id,
        summary=(
            f"Complaint {complaint.public_reference} changed from "
            f"{previous.value} to {payload.status.value}."
        ),
        event_metadata={
            "public_reference": complaint.public_reference,
            "from_status": previous.value,
            "to_status": payload.status.value,
        },
    )
    notify(
        db,
        recipient_user_id=complaint.citizen_id,
        notification_type=(
            NotificationType.success
            if payload.status == ComplaintStatus.resolved
            else NotificationType.info
        ),
        title=f"Update for {complaint.public_reference}",
        message=f"Status is now {payload.status.value}.",
        link="/app/citizen/my-complaints",
    )
    db.flush()
    return _detail(db, complaint.id)
