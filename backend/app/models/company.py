"""Company model — aggregated ghost/safety data for Pakistani companies."""

from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)

    # 1–10: how reliably they offer remote work
    remote_score = Column(Float, default=5.0)

    # 0–100: percentage of applicants who got ghosted
    ghost_rate = Column(Float, default=50.0)

    # 1–10: overall safety for in-person visits
    safety_score = Column(Float, default=5.0)

    # True if remote claims are verified through real data
    verified_remote = Column(Boolean, default=False)

    # True if the company has female-friendly policies
    female_friendly = Column(Boolean, default=False)

    # JSON array of string flags e.g. ["WhatsApp-only HR", "no website"]
    flags = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
