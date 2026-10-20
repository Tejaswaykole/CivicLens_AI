"""Complaint requests and responses."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import ComplaintPriority, ComplaintStatus, SuggestionOrigin
from app.domain.workflow import COMPLAINT_CATEGORIES
from app.schemas.user import DepartmentBrief, UserSummary


class ComplaintCreate(BaseModel):
    citizen_id: uuid.UUID
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    category: str
    location_address: str = Field(min_length=3, max_length=500)
    ward_zone: str | None = Field(default=None, max_length=200)
    requested_department_id: uuid.UUID | None = None

    @field_validator("title", "description", "location_address", "ward_zone", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    @field_validator("category")
    @classmethod
    def known_category(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned not in COMPLAINT_CATEGORIES:
            allowed = ", ".join(COMPLAINT_CATEGORIES)
            raise ValueError(f"category must be one of: {allowed}")
        return cleaned


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus
    note: str = Field(min_length=3, max_length=2000)
    actor_user_id: uuid.UUID | None = None
    actor_label: str | None = Field(default=None, max_length=200)

    @field_validator("note", "actor_label", mode="before")
    @classmethod
    def strip_optional(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None


class StatusHistoryRead(BaseModel):
    id: uuid.UUID
    previous_status: ComplaintStatus | None
    new_status: ComplaintStatus
    title: str
    note: str | None
    actor_user_id: uuid.UUID | None
    actor_display_name: str | None
    actor_label: str | None
    actor_verified: bool = False
    created_at: datetime


class AssignmentRead(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    department: DepartmentBrief
    assigned_officer: UserSummary | None
    assigned_crew_unit: str | None
    note: str | None
    is_current: bool
    assigned_at: datetime
    complaint_status: ComplaintStatus | None = None


class ModelPredictionRead(BaseModel):
    id: uuid.UUID
    model_identifier: str
    model_version: str
    predicted_category: str | None
    suggested_priority: ComplaintPriority | None
    confidence: float | None
    explanation: dict[str, Any] | None
    predicted_at: datetime


class HumanReviewRead(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    reviewer: UserSummary
    suggested_priority: ComplaintPriority | None
    confirmed_priority: ComplaintPriority
    suggestion_origin: SuggestionOrigin
    justification: str | None
    reviewed_at: datetime
    complaint_status: ComplaintStatus | None = None


class ComplaintRead(BaseModel):
    id: uuid.UUID
    public_reference: str
    title: str
    description: str
    category: str
    ward_zone: str | None
    location_address: str
    status: ComplaintStatus
    citizen: UserSummary
    requested_department: DepartmentBrief | None
    department: DepartmentBrief | None
    confirmed_priority: ComplaintPriority | None
    resolution_notes: str | None
    resolution_due_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ComplaintDetail(ComplaintRead):
    status_history: list[StatusHistoryRead]
    assignments: list[AssignmentRead]
    reviews: list[HumanReviewRead]
    predictions: list[ModelPredictionRead]
