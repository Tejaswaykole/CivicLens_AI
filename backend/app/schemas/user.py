"""User responses. password_hash is intentionally absent."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import UserRole


class DepartmentBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    email: str
    role: UserRole
    is_active: bool
    department_id: uuid.UUID | None
    department: DepartmentBrief | None = None
    designation: str | None
    ward_or_zone: str | None
    avatar_initials: str
    created_at: datetime
    updated_at: datetime


class UserSummary(BaseModel):
    id: uuid.UUID
    display_name: str
    role: UserRole
    avatar_initials: str = Field(min_length=1, max_length=8)
