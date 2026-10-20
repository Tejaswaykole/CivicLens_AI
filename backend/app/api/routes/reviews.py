"""Human review records. Submitting a user id does not authorize the review."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.complaint import HumanReviewRead
from app.schemas.review import HumanReviewCreate
from app.services import reviews as review_service

router = APIRouter(
    prefix="/complaints",
    tags=["reviews"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/{complaint_id}/reviews",
    response_model=HumanReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    complaint_id: uuid.UUID,
    payload: HumanReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HumanReviewRead:
    return review_service.create_review(db, complaint_id, payload, current_user)
