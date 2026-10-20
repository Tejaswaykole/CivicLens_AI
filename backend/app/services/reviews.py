"""Record a human priority decision without inventing a model prediction."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.domain.enums import AuditAction, ComplaintStatus, NotificationType, SuggestionOrigin
from app.domain.workflow import REVIEWABLE_STATUSES
from app.models.human_review import HumanReview
from app.repositories.complaints import get_complaint_for_update, latest_prediction
from app.schemas.complaint import HumanReviewRead
from app.schemas.mappers import review_to_read
from app.schemas.review import HumanReviewCreate
from app.services.audit import record_audit
from app.services.complaints import _append_status, _detail
from app.services.lookups import require_active_user
from app.services.notifications import notify


def _justification_ok(justification: str | None) -> bool:
    return justification is not None and len(justification.strip()) >= 10


def create_review(
    db: Session,
    complaint_id: uuid.UUID,
    payload: HumanReviewCreate,
) -> HumanReviewRead:
    complaint = get_complaint_for_update(db, complaint_id)
    if complaint is None:
        raise AppError("not_found", "Complaint not found.", 404)
    if complaint.status not in REVIEWABLE_STATUSES:
        raise AppError(
            "invalid_status_transition",
            f"A complaint in status {complaint.status.value} is not open for human review.",
            409,
        )

    reviewer = require_active_user(db, payload.reviewer_user_id)
    prediction = latest_prediction(db, complaint.id)
    stored_priority = prediction.suggested_priority if prediction is not None else None

    if stored_priority is not None:
        if payload.suggested_priority is not None and payload.suggested_priority != stored_priority:
            raise AppError(
                "suggestion_mismatch",
                "suggested_priority does not match the stored model prediction.",
                409,
            )
        suggested = stored_priority
        origin = SuggestionOrigin.stored_prediction
    elif payload.suggested_priority is not None:
        suggested = payload.suggested_priority
        origin = SuggestionOrigin.client_supplied
    else:
        suggested = None
        origin = SuggestionOrigin.none

    if suggested is not None and suggested != payload.confirmed_priority and not _justification_ok(
        payload.justification
    ):
        raise AppError(
            "validation_error",
            "A justification of at least 10 characters is required when the confirmed "
            "priority differs from the suggested priority.",
            422,
        )

    if suggested is None:
        action = AuditAction.HUMAN_REVIEW
    elif suggested == payload.confirmed_priority:
        action = AuditAction.CONCURRENCE
    else:
        action = AuditAction.HITL_OVERRIDE

    review = HumanReview(
        complaint_id=complaint.id,
        reviewer_user_id=reviewer.id,
        suggested_priority=suggested,
        confirmed_priority=payload.confirmed_priority,
        suggestion_origin=origin,
        justification=payload.justification,
    )
    db.add(review)

    status_changed = False
    if complaint.status in {ComplaintStatus.submitted, ComplaintStatus.in_review}:
        _append_status(
            db,
            complaint,
            new_status=ComplaintStatus.triaged,
            note=payload.justification or "Human review recorded.",
            actor_user_id=reviewer.id,
            actor_label=None,
        )
        status_changed = True

    record_audit(
        db,
        action=action,
        entity_type="complaint",
        entity_id=complaint.id,
        actor_user_id=reviewer.id,
        summary=f"Human review recorded for {complaint.public_reference}.",
        event_metadata={
            "public_reference": complaint.public_reference,
            "suggestion_origin": origin.value,
            "confirmed_priority": payload.confirmed_priority.value,
            "suggested_priority": suggested.value if suggested is not None else None,
            "status_changed": status_changed,
            "status": complaint.status.value,
        },
    )
    notify(
        db,
        recipient_user_id=complaint.citizen_id,
        notification_type=NotificationType.info,
        title=f"Review recorded for {complaint.public_reference}",
        message="A human priority review was recorded.",
        link="/app/citizen/my-complaints",
    )
    db.flush()
    db.refresh(review)
    review.reviewer = reviewer
    _detail(db, complaint.id)
    return review_to_read(review, complaint_status=complaint.status)
