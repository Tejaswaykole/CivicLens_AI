"""Aggregate the versioned API routes."""

from fastapi import APIRouter

from app.api.routes import (
    assignments,
    audit_logs,
    auth,
    complaints,
    departments,
    health,
    notifications,
    reviews,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(departments.router)
api_router.include_router(complaints.router)
api_router.include_router(assignments.router)
api_router.include_router(reviews.router)
api_router.include_router(audit_logs.router)
api_router.include_router(notifications.router)
