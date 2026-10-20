"""Complaint categories, reference numbers, and status transitions."""

from app.domain.enums import ComplaintStatus

# Option values from the citizen submission form.
COMPLAINT_CATEGORIES: tuple[str, ...] = (
    "Road Infrastructure",
    "Water & Sewage",
    "Electrical Hazard",
    "Sanitation & Solid Waste",
    "Street Lighting",
)

# The department work-order screen can close an assigned case or return an
# in-progress case to assigned. Other jumps, including submitted -> resolved,
# are rejected.
ALLOWED_STATUS_TRANSITIONS: dict[ComplaintStatus, frozenset[ComplaintStatus]] = {
    ComplaintStatus.submitted: frozenset(
        {ComplaintStatus.in_review, ComplaintStatus.triaged, ComplaintStatus.rejected}
    ),
    ComplaintStatus.in_review: frozenset({ComplaintStatus.triaged, ComplaintStatus.rejected}),
    ComplaintStatus.triaged: frozenset({ComplaintStatus.assigned, ComplaintStatus.rejected}),
    ComplaintStatus.assigned: frozenset(
        {ComplaintStatus.in_progress, ComplaintStatus.resolved, ComplaintStatus.rejected}
    ),
    ComplaintStatus.in_progress: frozenset({ComplaintStatus.resolved, ComplaintStatus.assigned}),
    ComplaintStatus.resolved: frozenset(),
    ComplaintStatus.rejected: frozenset(),
}

REVIEWABLE_STATUSES = frozenset(
    {ComplaintStatus.submitted, ComplaintStatus.in_review, ComplaintStatus.triaged}
)
ASSIGNABLE_STATUSES = frozenset(
    {ComplaintStatus.triaged, ComplaintStatus.assigned, ComplaintStatus.in_progress}
)


def can_transition(current: ComplaintStatus, new: ComplaintStatus) -> bool:
    return new in ALLOWED_STATUS_TRANSITIONS[current]


def format_public_reference(year: int, sequence: int) -> str:
    """Human-readable reference that does not expose the complaint UUID."""
    return f"DEL-{year:04d}-{sequence:06d}"


def status_history_title(previous: ComplaintStatus | None, new: ComplaintStatus) -> str:
    if previous is None:
        return f"Status set to {new.value}"
    return f"Status changed from {previous.value} to {new.value}"
