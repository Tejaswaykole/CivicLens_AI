"""Rules that do not need a database."""

import pytest

from app.domain.enums import ComplaintStatus
from app.domain.workflow import (
    COMPLAINT_CATEGORIES,
    can_transition,
    format_public_reference,
)


def test_public_reference_hides_database_identity() -> None:
    assert format_public_reference(2026, 42) == "DEL-2026-000042"


def test_categories_match_the_citizen_form() -> None:
    assert COMPLAINT_CATEGORIES == (
        "Road Infrastructure",
        "Water & Sewage",
        "Electrical Hazard",
        "Sanitation & Solid Waste",
        "Street Lighting",
        "Public Health",
    )


@pytest.mark.parametrize(
    ("current", "new", "allowed"),
    [
        (ComplaintStatus.submitted, ComplaintStatus.triaged, True),
        (ComplaintStatus.submitted, ComplaintStatus.resolved, False),
        (ComplaintStatus.triaged, ComplaintStatus.assigned, True),
        (ComplaintStatus.assigned, ComplaintStatus.in_progress, True),
        (ComplaintStatus.assigned, ComplaintStatus.resolved, True),
        (ComplaintStatus.in_progress, ComplaintStatus.assigned, True),
        (ComplaintStatus.resolved, ComplaintStatus.in_progress, False),
        (ComplaintStatus.rejected, ComplaintStatus.submitted, False),
    ],
)
def test_status_transitions(current: ComplaintStatus, new: ComplaintStatus, allowed: bool) -> None:
    assert can_transition(current, new) is allowed
