"""
Webhooks Router — receives events from n8n automation workflows.
Two webhooks:
  1. /webhooks/email-parsed — n8n sends parsed Gmail data here
  2. /webhooks/daily-scan   — n8n triggers daily ghost score recalculation
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.models.email_log import EmailLog
from app.schemas import EmailParsedWebhook, DailyScanWebhook
from app.services.claude import parse_recruitment_email
from app.services.ghost_scorer import recalculate_ghost_scores

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()
logger = logging.getLogger(__name__)


def _verify_webhook_secret(secret: Optional[str]) -> None:
    """Validate the webhook shared secret to prevent unauthorized triggers."""
    if settings.webhook_secret and secret != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


# ─── Email Parsed Webhook ─────────────────────────────────────────────────────

@router.post("/email-parsed")
async def email_parsed(
    body: EmailParsedWebhook,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives a recruitment email forwarded by n8n from the user's Gmail.
    Steps:
    1. Find the user by email
    2. Parse the email with Claude to extract company/status/date
    3. Update or create the corresponding Application record
    4. Log the email in EmailLog
    """
    # Find the user
    result = await db.execute(select(User).where(User.email == body.user_email))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning(f"Webhook: unknown user email {body.user_email}")
        return {"status": "user_not_found"}

    # Parse email content with Claude
    parsed = await parse_recruitment_email(
        email_subject=body.email_subject,
        email_body=body.email_body,
    )

    company_name = parsed.get("company_name")
    status_str = parsed.get("application_status", "unknown")
    interview_date = parsed.get("interview_date")

    # Try to match an existing application for this company
    app = None
    if company_name:
        app_result = await db.execute(
            select(Application).where(
                Application.user_id == user.id,
                Application.company_name.ilike(f"%{company_name}%"),
            )
        )
        app = app_result.scalars().first()

    # Map parsed status to ApplicationStatus enum
    status_map = {
        "confirmed": ApplicationStatus.confirmed,
        "interview": ApplicationStatus.interview,
        "offer": ApplicationStatus.offer,
        "rejected": ApplicationStatus.rejected,
        "applied": ApplicationStatus.applied,
    }
    new_status = status_map.get(status_str)

    if app and new_status:
        app.status = new_status
        app.last_contact_at = body.received_at or datetime.now(timezone.utc)

    # Log the email regardless
    email_log = EmailLog(
        user_id=user.id,
        application_id=app.id if app else None,
        email_subject=body.email_subject,
        email_body=body.email_body,
        parsed_company=company_name,
        parsed_status=status_str,
        parsed_interview_date=interview_date,
        received_at=body.received_at,
        processed_at=datetime.now(timezone.utc),
    )
    db.add(email_log)
    await db.flush()

    return {
        "status": "processed",
        "company_name": company_name,
        "parsed_status": status_str,
        "application_updated": app is not None,
    }


# ─── Daily Scan Webhook ───────────────────────────────────────────────────────

@router.post("/daily-scan")
async def daily_scan(
    body: DailyScanWebhook,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggered by n8n at 9am PKT every day.
    Re-scores ghost risk for all confirmed applications >= 7 days old.
    """
    _verify_webhook_secret(body.secret)

    summary = await recalculate_ghost_scores(db)
    logger.info(f"Daily scan complete: {summary}")

    return {"status": "success", **summary}
