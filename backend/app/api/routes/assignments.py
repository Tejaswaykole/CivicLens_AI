"""Complaint assignment history."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assignment import AssignmentCreate
from app.schemas.complaint import AssignmentRead
from app.services import assignments as assignment_service

router = APIRouter(prefix="/complaints", tags=["assignments"])


@router.post(
    "/{complaint_id}/assignments",
    response_model=AssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    complaint_id: uuid.UUID,
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
) -> AssignmentRead:
    """Assign a department. The actor id in the body is not authenticated."""
    return assignment_service.create_assignment(db, complaint_id, payload)
