"""Request validation that can be checked without PostgreSQL."""

import uuid

import pytest
from pydantic import ValidationError

from app.domain.enums import ComplaintPriority, ComplaintStatus
from app.schemas.complaint import ComplaintCreate, ComplaintStatusUpdate
from app.schemas.review import HumanReviewCreate


def test_complaint_rejects_unknown_category() -> None:
    with pytest.raises(ValidationError):
        ComplaintCreate(
            citizen_id=uuid.uuid4(),
            title="Dark street",
            description="Four lights have been dark for several nights.",
            category="Other",
            location_address="Lane 7 near the park",
        )


def test_complaint_strips_and_rejects_short_title() -> None:
    with pytest.raises(ValidationError):
        ComplaintCreate(
            citizen_id=uuid.uuid4(),
            title="  ab ",
            description="Four lights have been dark for several nights.",
            category="Street Lighting",
            location_address="Lane 7 near the park",
        )


def test_status_update_requires_a_note() -> None:
    with pytest.raises(ValidationError):
        ComplaintStatusUpdate(status=ComplaintStatus.in_review, note="  ")


def test_override_without_justification_is_rejected() -> None:
    with pytest.raises(ValidationError) as caught:
        HumanReviewCreate(
            reviewer_user_id=uuid.uuid4(),
            suggested_priority=ComplaintPriority.low,
            confirmed_priority=ComplaintPriority.critical,
            justification="too short",
        )
    assert "justification" in str(caught.value)


def test_concurrence_allows_an_empty_justification() -> None:
    review = HumanReviewCreate(
        reviewer_user_id=uuid.uuid4(),
        suggested_priority=ComplaintPriority.high,
        confirmed_priority=ComplaintPriority.high,
    )
    assert review.justification is None


def test_confirmation_without_a_suggestion_is_allowed() -> None:
    review = HumanReviewCreate(
        reviewer_user_id=uuid.uuid4(),
        confirmed_priority=ComplaintPriority.medium,
    )
    assert review.suggested_priority is None
