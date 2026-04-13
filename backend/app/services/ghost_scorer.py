"""
Ghost Scorer Service — daily batch re-scoring of all active applications.
Called by the /webhooks/daily-scan endpoint triggered by n8n at 9am PKT.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.application import Application, ApplicationStatus
from app.services.claude import score_ghost_risk

logger = logging.getLogger(__name__)


async def recalculate_ghost_scores(db: AsyncSession) -> dict:
    """
    Fetch all applications with status=confirmed and days_since_contact >= 7,
    re-score each with Claude, update ghost_score in DB.
    Returns a summary dict for the webhook response.
    """
    now = datetime.now(timezone.utc)

    # Fetch all confirmed applications
    result = await db.execute(
        select(Application).where(
            Application.status == ApplicationStatus.confirmed
        )
    )
    applications = result.scalars().all()

    updated = 0
    high_risk = []

    for app in applications:
        try:
            # Calculate days since last contact
            reference_date = app.last_contact_at or app.applied_at
            if reference_date:
                # Ensure reference_date is timezone-aware
                if reference_date.tzinfo is None:
                    reference_date = reference_date.replace(tzinfo=timezone.utc)
                days = (now - reference_date).days
            else:
                days = 0

            app.days_since_contact = days

            # Only score if waiting 7+ days (in the ghost window)
            if days >= 7:
                score_data = await score_ghost_risk(
                    company_name=app.company_name,
                    industry="",
                    days_since_contact=days,
                    app_volume="medium",
                )
                app.ghost_score = score_data.get("ghost_score", 50)

                if app.ghost_score > 70:
                    high_risk.append({
                        "application_id": str(app.id),
                        "company": app.company_name,
                        "ghost_score": app.ghost_score,
                    })

            updated += 1

        except Exception as e:
            logger.error(f"Failed to score application {app.id}: {e}")
            continue

    await db.flush()

    return {
        "applications_scanned": len(applications),
        "applications_updated": updated,
        "high_risk_count": len(high_risk),
        "high_risk_applications": high_risk,
    }
