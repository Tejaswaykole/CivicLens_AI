"""Assignment requests."""

import uuid

from pydantic import BaseModel, Field, field_validator


class AssignmentCreate(BaseModel):
    department_id: uuid.UUID
    assigned_officer_id: uuid.UUID | None = None
    assigned_crew_unit: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    actor_user_id: uuid.UUID | None = None
    actor_label: str | None = Field(default=None, max_length=200)

    @field_validator("assigned_crew_unit", "note", "actor_label", mode="before")
    @classmethod
    def strip_optional(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None
