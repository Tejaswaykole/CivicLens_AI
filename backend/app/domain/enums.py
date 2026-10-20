"""Values aligned with the existing frontend domain types."""

from enum import StrEnum


class UserRole(StrEnum):
    system_admin = "system_admin"
    grievance_officer = "grievance_officer"
    department_officer = "department_officer"
    citizen = "citizen"


class ComplaintStatus(StrEnum):
    submitted = "submitted"
    in_review = "in_review"
    triaged = "triaged"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


class ComplaintPriority(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class SuggestionOrigin(StrEnum):
    stored_prediction = "stored_prediction"
    client_supplied = "client_supplied"
    none = "none"


class AuditAction(StrEnum):
    COMPLAINT_CREATED = "COMPLAINT_CREATED"
    STATUS_CHANGE = "STATUS_CHANGE"
    ASSIGNMENT_CREATED = "ASSIGNMENT_CREATED"
    CONCURRENCE = "CONCURRENCE"
    HITL_OVERRIDE = "HITL_OVERRIDE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ROLE_CHANGED = "ROLE_CHANGED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"


class NotificationType(StrEnum):
    urgent = "urgent"
    info = "info"
    success = "success"
    alert = "alert"


OPEN_COMPLAINT_STATUSES = (
    ComplaintStatus.submitted,
    ComplaintStatus.in_review,
    ComplaintStatus.triaged,
    ComplaintStatus.assigned,
    ComplaintStatus.in_progress,
)
