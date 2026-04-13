"""User model — stores auth credentials and subscription info."""

from sqlalchemy import Column, String, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class SubscriptionTier(str, enum.Enum):
    free = "free"
    pro = "pro"
    university = "university"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth-only users
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    google_oauth_token = Column(Text, nullable=True)  # JSON-encoded token dict
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.free, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    applications = relationship("Application", back_populates="user", lazy="select")
    email_logs = relationship("EmailLog", back_populates="user", lazy="select")
