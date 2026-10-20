"""Complaint assignment history."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.assignment import AssignmentCreate
from app.schemas.complaint import AssignmentRead
from app.services import assignments as assignment_service

router = APIRouter(
    prefix="/complaints",
    tags=["assignments"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/{complaint_id}/assignments",
    response_model=AssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    complaint_id: uuid.UUID,
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssignmentRead:
    return assignment_service.create_assignment(db, complaint_id, payload, current_user)
