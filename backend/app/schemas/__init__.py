"""
Pydantic v2 schemas for all API request/response shapes.
Separated from ORM models to keep validation logic clean.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
import enum


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    subscription_tier: str
    email_verified: bool
    onboarded: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Application Schemas ─────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    linkedin_url: Optional[str] = None
    status: Optional[str] = "applied"
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None
    applied_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    notes: Optional[str] = None
    ghost_score: Optional[float] = None
    days_since_contact: Optional[int] = None


class ApplicationOut(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    job_title: str
    linkedin_url: Optional[str]
    status: str
    applied_at: Optional[datetime]
    last_contact_at: Optional[datetime]
    ghost_score: float
    days_since_contact: int
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── AI Feature Schemas ───────────────────────────────────────────────────────

class GhostScoreRequest(BaseModel):
    application_id: Optional[UUID] = None
    company_name: str
    industry: Optional[str] = ""
    days_since_contact: int = Field(..., ge=0)
    app_volume: Optional[str] = "medium"  # low | medium | high


class GhostScoreResponse(BaseModel):
    ghost_score: int
    risk_level: str
    reason: str
    recommended_action: str


class FollowUpRequest(BaseModel):
    application_id: Optional[UUID] = None
    applicant_name: str
    company: str
    job_title: str
    days_since_applied: int = Field(..., ge=0)
    prior_contact: bool = False


class EmailVariant(BaseModel):
    subject: str
    body: str
    tone: str


class FollowUpResponse(BaseModel):
    variant_a: EmailVariant
    variant_b: EmailVariant
    variant_c: EmailVariant


class InterviewPrepRequest(BaseModel):
    job_description: str = Field(..., min_length=50)


class InterviewPrepResponse(BaseModel):
    role_summary: str
    likely_questions: List[str]
    suggested_answers: List[str]
    weak_areas: List[str]
    preparation_tips: str


class CompanySafetyRequest(BaseModel):
    company_name: str
    job_type: str
    claimed_location: str
    job_description: str


class CompanySafetyResponse(BaseModel):
    remote_verified: bool
    safety_score: int
    female_friendly_score: int
    flags: List[str]
    recommendation: str


class WeeklySummaryRequest(BaseModel):
    # Accepts the user's full application list as JSON
    applications: List[Any]


class WeeklySummaryResponse(BaseModel):
    summary_paragraph: str
    response_rate_percent: float
    fastest_responding_industry: str
    top_actions_this_week: List[str]
    motivational_line: str


# ─── Job Listing Schemas ──────────────────────────────────────────────────────

class JobListingOut(BaseModel):
    id: UUID
    title: str
    company: str
    location: Optional[str]
    remote: bool
    paid: bool
    stipend_pkr: Optional[int]
    domain: Optional[str]
    source: str
    safety_score: float
    posted_at: Optional[datetime]
    scraped_at: datetime

    model_config = {"from_attributes": True}


# ─── Webhook Schemas ──────────────────────────────────────────────────────────

class EmailParsedWebhook(BaseModel):
    user_email: str
    email_subject: str
    email_body: str
    received_at: Optional[datetime] = None


class DailyScanWebhook(BaseModel):
    # Optional secret to authenticate n8n requests
    secret: Optional[str] = None


# ─── Payment Schemas ──────────────────────────────────────────────────────────

class PaymentCheckoutRequest(BaseModel):
    plan: str = "pro"  # "pro" or "university"


class PaymentCheckoutResponse(BaseModel):
    checkout_url: str
    tracker_id: str


class PaymentWebhookPayload(BaseModel):
    tracker_id: str
    status: str  # "paid" | "failed" | "refunded"
    amount: Optional[int] = None
    currency: str = "PKR"


# ─── Onboarding Schema ────────────────────────────────────────────────────────

class OnboardingComplete(BaseModel):
    onboarded: bool = True
