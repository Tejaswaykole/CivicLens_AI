"""Map ORM rows to response schemas without exposing sensitive columns."""

from decimal import Decimal

from app.models.assignment import ComplaintAssignment
from app.models.audit_log import AuditLog
from app.models.complaint import Complaint
from app.models.complaint_status_history import ComplaintStatusHistory
from app.models.department import Department
from app.models.human_review import HumanReview
from app.models.model_prediction import ModelPrediction
from app.models.notification import Notification
from app.models.user import User
from app.schemas.audit import AuditActor, AuditLogRead
from app.schemas.complaint import (
    AssignmentRead,
    ComplaintDetail,
    ComplaintRead,
    HumanReviewRead,
    ModelPredictionRead,
    StatusHistoryRead,
)
from app.schemas.department import DepartmentRead
from app.schemas.notification import NotificationRead
from app.schemas.user import DepartmentBrief, UserRead, UserSummary


def avatar_initials(display_name: str) -> str:
    parts = [part for part in display_name.split() if part]
    initials = "".join(part[0] for part in parts[:2]).upper()
    return initials or "CL"


def department_brief(department: Department | None) -> DepartmentBrief | None:
    if department is None:
        return None
    return DepartmentBrief(id=department.id, code=department.code, name=department.name)


def user_summary(user: User) -> UserSummary:
    return UserSummary(
        id=user.id,
        display_name=user.display_name,
        role=user.role,
        avatar_initials=avatar_initials(user.display_name),
    )


def user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        display_name=user.display_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        department_id=user.department_id,
        department=department_brief(user.department),
        designation=user.designation,
        ward_or_zone=user.ward_or_zone,
        avatar_initials=avatar_initials(user.display_name),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def department_to_read(
    department: Department,
    *,
    active_cases_count: int,
    resolved_count: int,
) -> DepartmentRead:
    return DepartmentRead(
        id=department.id,
        code=department.code,
        name=department.name,
        description=department.description,
        nodal_officer_name=department.nodal_officer_name,
        contact_email=department.contact_email,
        sla_target_hours=department.sla_target_hours,
        is_active=department.is_active,
        active_cases_count=active_cases_count,
        resolved_count=resolved_count,
        created_at=department.created_at,
        updated_at=department.updated_at,
    )


def history_to_read(item: ComplaintStatusHistory) -> StatusHistoryRead:
    actor_name = item.actor.display_name if item.actor is not None else None
    return StatusHistoryRead(
        id=item.id,
        previous_status=item.previous_status,
        new_status=item.new_status,
        title=item.title,
        note=item.note,
        actor_user_id=item.actor_user_id,
        actor_display_name=actor_name,
        actor_label=item.actor_label,
        actor_verified=False,
        created_at=item.created_at,
    )


def assignment_to_read(
    assignment: ComplaintAssignment,
    *,
    complaint_status=None,
) -> AssignmentRead:
    department = department_brief(assignment.department)
    if department is None:
        raise RuntimeError("Assignment is missing its department.")
    officer = (
        user_summary(assignment.assigned_officer)
        if assignment.assigned_officer is not None
        else None
    )
    return AssignmentRead(
        id=assignment.id,
        complaint_id=assignment.complaint_id,
        department=department,
        assigned_officer=officer,
        assigned_crew_unit=assignment.assigned_crew_unit,
        note=assignment.note,
        is_current=assignment.is_current,
        assigned_at=assignment.assigned_at,
        complaint_status=complaint_status,
    )


def prediction_to_read(prediction: ModelPrediction) -> ModelPredictionRead:
    confidence = None if prediction.confidence is None else float(Decimal(prediction.confidence))
    return ModelPredictionRead(
        id=prediction.id,
        model_identifier=prediction.model_identifier,
        model_version=prediction.model_version,
        predicted_category=prediction.predicted_category,
        suggested_priority=prediction.suggested_priority,
        confidence=confidence,
        explanation=prediction.explanation,
        predicted_at=prediction.predicted_at,
    )


def review_to_read(review: HumanReview, *, complaint_status=None) -> HumanReviewRead:
    return HumanReviewRead(
        id=review.id,
        complaint_id=review.complaint_id,
        reviewer=user_summary(review.reviewer),
        suggested_priority=review.suggested_priority,
        confirmed_priority=review.confirmed_priority,
        suggestion_origin=review.suggestion_origin,
        justification=review.justification,
        reviewed_at=review.reviewed_at,
        complaint_status=complaint_status,
    )


def complaint_to_read(
    complaint: Complaint,
    *,
    confirmed_priority=None,
) -> ComplaintRead:
    return ComplaintRead(
        id=complaint.id,
        public_reference=complaint.public_reference,
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        ward_zone=complaint.ward_zone,
        location_address=complaint.location_address,
        status=complaint.status,
        citizen=user_summary(complaint.citizen),
        requested_department=department_brief(complaint.requested_department),
        department=department_brief(complaint.department),
        confirmed_priority=confirmed_priority,
        resolution_notes=complaint.resolution_notes,
        resolution_due_at=complaint.resolution_due_at,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


def complaint_to_detail(complaint: Complaint, *, confirmed_priority=None) -> ComplaintDetail:
    base = complaint_to_read(complaint, confirmed_priority=confirmed_priority)
    return ComplaintDetail(
        **base.model_dump(),
        status_history=[history_to_read(item) for item in complaint.status_history],
        assignments=[assignment_to_read(item) for item in complaint.assignments],
        reviews=[review_to_read(item) for item in complaint.reviews],
        predictions=[prediction_to_read(item) for item in complaint.predictions],
    )


def audit_to_read(entry: AuditLog) -> AuditLogRead:
    actor = None
    if entry.actor is not None:
        actor = AuditActor(
            id=entry.actor.id,
            display_name=entry.actor.display_name,
            role=entry.actor.role,
        )
    return AuditLogRead(
        id=entry.id,
        action=entry.action,
        entity_type=entry.entity_type,
        entity_id=entry.entity_id,
        summary=entry.summary,
        event_metadata=entry.event_metadata,
        actor=actor,
        actor_verified=False,
        created_at=entry.created_at,
    )


def notification_to_read(notification: Notification) -> NotificationRead:
    return NotificationRead(
        id=notification.id,
        recipient_user_id=notification.recipient_user_id,
        recipient_role=notification.recipient_role,
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        link=notification.link,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )
