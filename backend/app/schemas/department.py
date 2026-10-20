"""Department responses, including counts derived from complaints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None
    nodal_officer_name: str | None
    contact_email: str | None
    sla_target_hours: int
    is_active: bool
    active_cases_count: int
    resolved_count: int
    created_at: datetime
    updated_at: datetime
