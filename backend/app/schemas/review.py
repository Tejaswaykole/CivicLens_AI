"""Human-review requests. A user id in the body is not an authentication proof."""

import uuid

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums import ComplaintPriority


class HumanReviewCreate(BaseModel):
    reviewer_user_id: uuid.UUID
    suggested_priority: ComplaintPriority | None = None
    confirmed_priority: ComplaintPriority
    justification: str | None = Field(default=None, max_length=2000)

    @field_validator("justification", mode="before")
    @classmethod
    def strip_justification(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def override_requires_justification(self) -> "HumanReviewCreate":
        if (
            self.suggested_priority is not None
            and self.suggested_priority != self.confirmed_priority
            and (self.justification is None or len(self.justification) < 10)
        ):
            raise ValueError(
                "A justification of at least 10 characters is required when the "
                "confirmed priority differs from the suggested priority."
            )
        return self
