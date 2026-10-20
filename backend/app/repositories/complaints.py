"""Complaint queries."""

import uuid
from datetime import datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.domain.enums import ComplaintPriority, ComplaintStatus
from app.models.assignment import ComplaintAssignment
from app.models.complaint import Complaint
from app.models.complaint_status_history import ComplaintStatusHistory
from app.models.human_review import HumanReview
from app.models.model_prediction import ModelPrediction
from app.repositories.query import contains_pattern
from app.schemas.common import PageParams


def _latest_confirmed_priority():
    return (
        select(HumanReview.confirmed_priority)
        .where(HumanReview.complaint_id == Complaint.id)
        .order_by(HumanReview.reviewed_at.desc(), HumanReview.id.desc())
        .limit(1)
        .scalar_subquery()
    )


def complaint_filters(
    stmt: Select,
    *,
    status: ComplaintStatus | None,
    category: str | None,
    department_id: uuid.UUID | None,
    citizen_id: uuid.UUID | None,
    reference: str | None,
    query: str | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> Select:
    if status is not None:
        stmt = stmt.where(Complaint.status == status)
    if category:
        stmt = stmt.where(Complaint.category == category)
    if department_id is not None:
        stmt = stmt.where(Complaint.department_id == department_id)
    if citizen_id is not None:
        stmt = stmt.where(Complaint.citizen_id == citizen_id)
    if reference:
        stmt = stmt.where(Complaint.public_reference == reference.strip())
    if created_from is not None:
        stmt = stmt.where(Complaint.created_at >= created_from)
    if created_to is not None:
        stmt = stmt.where(Complaint.created_at <= created_to)
    if query:
        pattern = contains_pattern(query.strip())
        stmt = stmt.where(
            or_(
                Complaint.title.ilike(pattern, escape="\\"),
                Complaint.public_reference.ilike(pattern, escape="\\"),
                Complaint.location_address.ilike(pattern, escape="\\"),
                Complaint.ward_zone.ilike(pattern, escape="\\"),
            )
        )
    return stmt


def list_complaints(
    db: Session,
    params: PageParams,
    **filters,
) -> tuple[list[tuple[Complaint, ComplaintPriority | None]], int]:
    priority = _latest_confirmed_priority()
    filtered_ids = complaint_filters(select(Complaint.id), **filters)
    total = db.scalar(select(func.count()).select_from(filtered_ids.subquery())) or 0
    stmt = complaint_filters(
        select(Complaint, priority.label("confirmed_priority")).options(
            joinedload(Complaint.citizen),
            joinedload(Complaint.department),
            joinedload(Complaint.requested_department),
        ),
        **filters,
    )
    rows = db.execute(
        stmt.order_by(Complaint.created_at.desc()).offset(params.offset).limit(params.page_size)
    ).unique()
    return [(row[0], row[1]) for row in rows], int(total)


def get_complaint_for_update(db: Session, complaint_id: uuid.UUID) -> Complaint | None:
    return db.scalar(select(Complaint).where(Complaint.id == complaint_id).with_for_update())


def get_complaint_detail(db: Session, complaint_id: uuid.UUID) -> Complaint | None:
    stmt = (
        select(Complaint)
        .where(Complaint.id == complaint_id)
        .options(
            joinedload(Complaint.citizen),
            joinedload(Complaint.department),
            joinedload(Complaint.requested_department),
            selectinload(Complaint.status_history).joinedload(ComplaintStatusHistory.actor),
            selectinload(Complaint.assignments).joinedload(ComplaintAssignment.department),
            selectinload(Complaint.assignments).joinedload(ComplaintAssignment.assigned_officer),
            selectinload(Complaint.reviews).joinedload(HumanReview.reviewer),
            selectinload(Complaint.predictions),
        )
    )
    return db.scalar(stmt)


def latest_prediction(db: Session, complaint_id: uuid.UUID) -> ModelPrediction | None:
    return db.scalar(
        select(ModelPrediction)
        .where(ModelPrediction.complaint_id == complaint_id)
        .order_by(ModelPrediction.predicted_at.desc(), ModelPrediction.id.desc())
        .limit(1)
    )


def latest_confirmed_priority(db: Session, complaint_id: uuid.UUID) -> ComplaintPriority | None:
    return db.scalar(
        select(HumanReview.confirmed_priority)
        .where(HumanReview.complaint_id == complaint_id)
        .order_by(HumanReview.reviewed_at.desc(), HumanReview.id.desc())
        .limit(1)
    )
