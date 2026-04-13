"""
Jobs Router — paginated job listings with filtering.
Public endpoint (no auth required for browsing).
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.job_listing import JobListing
from app.schemas import JobListingOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobListingOut])
async def list_jobs(
    remote: Optional[bool] = Query(None, description="Filter to remote-only roles"),
    paid: Optional[bool] = Query(None, description="Filter to paid/stipend roles"),
    domain: Optional[str] = Query(None, description="Filter by domain e.g. 'AI', 'Marketing'"),
    city: Optional[str] = Query(None, description="Filter by city e.g. 'Islamabad'"),
    source: Optional[str] = Query(None, description="Filter by source: rozee|linkedin|mustakbil"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Return paginated job listings from the scraped job board.
    All filters are optional and can be combined.
    """
    query = select(JobListing)
    filters = []

    if remote is not None:
        filters.append(JobListing.remote == remote)
    if paid is not None:
        filters.append(JobListing.paid == paid)
    if domain:
        filters.append(JobListing.domain.ilike(f"%{domain}%"))
    if city:
        filters.append(JobListing.location.ilike(f"%{city}%"))
    if source:
        filters.append(JobListing.source == source)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(JobListing.scraped_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
