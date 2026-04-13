"""JobListing model — scraped jobs from Rozee.pk, LinkedIn, Mustakbil."""

from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class JobSource(str, enum.Enum):
    rozee = "rozee"
    linkedin = "linkedin"
    mustakbil = "mustakbil"


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)

    remote = Column(Boolean, default=False)
    paid = Column(Boolean, default=True)

    # Monthly stipend in Pakistani Rupees (null if not disclosed)
    stipend_pkr = Column(Integer, nullable=True)

    # Functional domain e.g. "AI", "Marketing", "Finance"
    domain = Column(String(100), nullable=True, index=True)

    source = Column(Enum(JobSource), nullable=False)

    # AI-computed safety score for this listing (1–10)
    safety_score = Column(Float, default=5.0)

    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
