"""Import every model so Alembic and metadata discovery see the full schema."""

from app.models.assignment import ComplaintAssignment
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.complaint import Complaint
from app.models.complaint_status_history import ComplaintStatusHistory
from app.models.department import Department
from app.models.human_review import HumanReview
from app.models.model_prediction import ModelPrediction
from app.models.notification import Notification
from app.models.user import User

__all__ = [
    "AuditLog",
    "Base",
    "Complaint",
    "ComplaintAssignment",
    "ComplaintStatusHistory",
    "Department",
    "HumanReview",
    "ModelPrediction",
    "Notification",
    "User",
]
