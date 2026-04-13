"""
AI Router — all Claude-powered endpoints.
Rate limited: 10 req/min (free) | 50 req/min (pro).
Requires JWT auth on every route.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.application import Application
from app.schemas import (
    GhostScoreRequest, GhostScoreResponse,
    FollowUpRequest, FollowUpResponse,
    InterviewPrepRequest, InterviewPrepResponse,
    CompanySafetyRequest, CompanySafetyResponse,
    WeeklySummaryRequest, WeeklySummaryResponse,
)
from app.middleware.auth import get_current_user
from app.services import claude

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ghost-score", response_model=GhostScoreResponse)
async def ghost_score(
    body: GhostScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Score ghost risk for a specific application.
    If application_id provided, syncs the score back to the DB.
    """
    result = await claude.score_ghost_risk(
        company_name=body.company_name,
        industry=body.industry or "",
        days_since_contact=body.days_since_contact,
        app_volume=body.app_volume or "medium",
    )

    # Sync score back to the application record if ID provided
    if body.application_id:
        app_result = await db.execute(
            select(Application).where(
                Application.id == body.application_id,
                Application.user_id == current_user.id,
            )
        )
        app = app_result.scalar_one_or_none()
        if app:
            app.ghost_score = result.get("ghost_score", 0)
            app.days_since_contact = body.days_since_contact
            await db.flush()

    return GhostScoreResponse(**result)


@router.post("/followup-email", response_model=FollowUpResponse)
async def followup_email(
    body: FollowUpRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate 3 follow-up email variants for a stalled application.
    Uses Claude Sonnet — available to all tiers (3 calls free/day).
    """
    result = await claude.generate_followup_emails(
        applicant_name=body.applicant_name,
        company=body.company,
        job_title=body.job_title,
        days_since_applied=body.days_since_applied,
        prior_contact=body.prior_contact,
    )
    return FollowUpResponse(**result)


@router.post("/interview-prep", response_model=InterviewPrepResponse)
async def interview_prep(
    body: InterviewPrepRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate 10 interview Q&A pairs and weak area analysis.
    Uses Claude Sonnet — higher quality for high-stakes prep.
    """
    result = await claude.generate_interview_prep(
        job_description=body.job_description
    )
    return InterviewPrepResponse(**result)


@router.post("/company-safety", response_model=CompanySafetyResponse)
async def company_safety(
    body: CompanySafetyRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Score a company's safety and legitimacy.
    Especially useful for female job seekers and remote role verification.
    """
    result = await claude.score_company_safety(
        company_name=body.company_name,
        job_type=body.job_type,
        claimed_location=body.claimed_location,
        job_description=body.job_description,
    )
    return CompanySafetyResponse(**result)


@router.post("/weekly-summary", response_model=WeeklySummaryResponse)
async def weekly_summary(
    body: WeeklySummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Summarize the user's job search week with actionable insights.
    If body.applications is empty, fetches from DB automatically.
    """
    apps = body.applications

    # Auto-fetch from DB if no applications provided in request
    if not apps:
        result = await db.execute(
            select(Application).where(Application.user_id == current_user.id)
        )
        db_apps = result.scalars().all()
        apps = [
            {
                "company_name": a.company_name,
                "status": a.status,
                "days_since_contact": a.days_since_contact,
                "ghost_score": a.ghost_score,
            }
            for a in db_apps
        ]

    result = await claude.generate_weekly_summary(apps)
    return WeeklySummaryResponse(**result)
