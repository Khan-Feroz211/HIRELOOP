"""Application model — tracks a single job application's lifecycle."""

from sqlalchemy import Column, String, Enum, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    confirmed = "confirmed"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"
    ghosted = "ghosted"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    linkedin_url = Column(Text, nullable=True)

    status = Column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.applied,
        nullable=False,
        index=True,
    )

    applied_at = Column(DateTime(timezone=True), nullable=True)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)

    # AI-computed ghost risk (0–100). Updated daily by n8n + Claude.
    ghost_score = Column(Float, default=0.0)
    days_since_contact = Column(Integer, default=0)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    email_logs = relationship("EmailLog", back_populates="application", lazy="select")
