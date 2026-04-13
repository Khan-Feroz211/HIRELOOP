"""
Models package — import all models here so Alembic can discover them.
"""

from app.models.user import User, UserRole, SubscriptionTier
from app.models.application import Application, ApplicationStatus
from app.models.company import Company
from app.models.email_log import EmailLog
from app.models.job_listing import JobListing, JobSource

__all__ = [
    "User",
    "UserRole",
    "SubscriptionTier",
    "Application",
    "ApplicationStatus",
    "Company",
    "EmailLog",
    "JobListing",
    "JobSource",
]
