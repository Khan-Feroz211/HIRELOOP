"""
Applications Router — full CRUD for job application tracking.
Free users: max 5 active applications.
Pro users: unlimited.
"""

from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])

FREE_TIER_APP_LIMIT = 5


async def _count_user_applications(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(Application).where(Application.user_id == user_id)
    )
    return result.scalar_one()


# ─── Create ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    body: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new job application to the tracker."""
    # Enforce free-tier limit
    if current_user.subscription_tier == "free":
        count = await _count_user_applications(db, current_user.id)
        if count >= FREE_TIER_APP_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Free tier limit reached ({FREE_TIER_APP_LIMIT} applications). "
                       "Upgrade to Pro at PKR 299/month for unlimited tracking.",
            )

    app = Application(
        user_id=current_user.id,
        company_name=body.company_name,
        job_title=body.job_title,
        linkedin_url=body.linkedin_url,
        status=body.status or ApplicationStatus.applied,
        applied_at=body.applied_at or datetime.now(timezone.utc),
        notes=body.notes,
    )
    db.add(app)
    await db.flush()
    return app


# ─── List ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[ApplicationOut])
async def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all applications for the authenticated user, optionally filtered by status."""
    query = select(Application).where(Application.user_id == current_user.id)

    if status_filter:
        try:
            query = query.where(Application.status == ApplicationStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# ─── Get by ID ────────────────────────────────────────────────────────────────

@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single application by ID — must belong to the current user."""
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


# ─── Update ───────────────────────────────────────────────────────────────────

@router.patch("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: UUID,
    body: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update an application (e.g., change status to 'interview')."""
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    # Auto-update last_contact_at when status changes to interview/offer/confirmed
    if body.status in ("interview", "offer", "confirmed"):
        app.last_contact_at = datetime.now(timezone.utc)

    await db.flush()
    return app


# ─── Delete ───────────────────────────────────────────────────────────────────

@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete an application."""
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(app)
