"""Process and database health. Database status is checked, not assumed."""

from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.database import check_database

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable", "not_configured"]
    version: str
    authenticated: bool = Field(
        default=False,
        description="Phase 3 does not authenticate requests.",
    )


@router.get("/health", response_model=HealthResponse)
def health() -> JSONResponse:
    database = check_database()
    payload = HealthResponse(
        status="ok" if database == "ok" else "degraded",
        database=database,
        version=get_settings().app_version,
    )
    status_code = 200 if database == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload.model_dump())
