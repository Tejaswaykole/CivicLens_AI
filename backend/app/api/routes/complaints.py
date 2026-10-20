"""Complaint creation, retrieval, and status changes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, pagination_params
from app.core.database import get_db
from app.domain.enums import ComplaintStatus
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintDetail,
    ComplaintRead,
    ComplaintStatusUpdate,
)
from app.services import complaints as complaint_service

router = APIRouter(
    prefix="/complaints",
    tags=["complaints"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=Page[ComplaintRead])
def list_complaints(
    status_filter: ComplaintStatus | None = Query(default=None, alias="status"),
    category: str | None = Query(default=None, max_length=80),
    department_id: uuid.UUID | None = None,
    citizen_id: uuid.UUID | None = None,
    reference: str | None = Query(default=None, max_length=32),
    q: str | None = Query(default=None, max_length=200),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[ComplaintRead]:
    return complaint_service.list_all(
        db,
        params,
        current_user,
        status=status_filter,
        category=category,
        department_id=department_id,
        citizen_id=citizen_id,
        reference=reference,
        query=q,
        created_from=created_from,
        created_to=created_to,
    )


@router.get("/{complaint_id}", response_model=ComplaintDetail)
def get_complaint(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintDetail:
    return complaint_service.get_one(db, complaint_id, current_user)


@router.post("", response_model=ComplaintDetail, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintDetail:
    return complaint_service.create_complaint(db, payload, current_user)


@router.patch("/{complaint_id}/status", response_model=ComplaintDetail)
def update_status(
    complaint_id: uuid.UUID,
    payload: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintDetail:
    return complaint_service.change_status(db, complaint_id, payload, current_user)
