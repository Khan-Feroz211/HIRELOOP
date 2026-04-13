"""EmailLog model — records every parsed recruitment email."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)

    email_subject = Column(Text, nullable=True)
    email_body = Column(Text, nullable=True)

    # Fields extracted by Claude from the email body
    parsed_company = Column(String(255), nullable=True)
    parsed_status = Column(String(100), nullable=True)
    parsed_interview_date = Column(DateTime(timezone=True), nullable=True)

    received_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="email_logs")
    application = relationship("Application", back_populates="email_logs")
