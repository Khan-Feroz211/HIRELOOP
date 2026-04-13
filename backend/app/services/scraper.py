"""
Job Scraper Service — fetches live job listings from multiple sources.
Sources: Apify LinkedIn Scraper, SerpAPI Google Jobs
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def scrape_google_jobs(
    query: str,
    location: str = "Pakistan",
    num_results: int = 20,
) -> List[Dict]:
    """
    Fetch job listings from Google Jobs via SerpAPI.
    Free tier: 100 searches/month.
    """
    if not settings.serpapi_key:
        logger.warning("SerpAPI key not configured — skipping Google Jobs scrape")
        return []

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": settings.serpapi_key,
        "num": num_results,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://serpapi.com/search", params=params)
            resp.raise_for_status()
            data = resp.json()

        jobs_results = data.get("jobs_results", [])
        normalized = []

        for job in jobs_results:
            normalized.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "posted_at": job.get("detected_extensions", {}).get("posted_at"),
                "source": "linkedin",  # Google Jobs aggregates LinkedIn & others
            })

        return normalized

    except Exception as e:
        logger.error(f"SerpAPI scrape failed: {e}")
        return []


async def scrape_apify_linkedin(
    keywords: List[str],
    location: str = "Pakistan",
    max_items: int = 50,
) -> List[Dict]:
    """
    Trigger an Apify LinkedIn Jobs actor run and wait for results.
    Uses Apify free tier (limited monthly runs).
    """
    if not settings.apify_api_token:
        logger.warning("Apify token not configured — skipping LinkedIn scrape")
        return []

    actor_id = "hKByXhkbQaYgQFBMh"  # Apify LinkedIn Jobs scraper actor
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

    payload = {
        "keywords": keywords,
        "location": location,
        "maxItems": max_items,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                run_url,
                json=payload,
                params={"token": settings.apify_api_token},
            )
            resp.raise_for_status()
            items = resp.json()

        normalized = []
        for item in items:
            normalized.append({
                "title": item.get("title", ""),
                "company": item.get("companyName", ""),
                "location": item.get("location", ""),
                "description": item.get("description", ""),
                "url": item.get("jobUrl", ""),
                "posted_at": item.get("postedAt"),
                "source": "linkedin",
            })

        return normalized

    except Exception as e:
        logger.error(f"Apify LinkedIn scrape failed: {e}")
        return []


def normalize_job_for_db(raw_job: Dict) -> Dict:
    """
    Convert a raw scraped job dict into the shape expected by the JobListing model.
    Detects remote/paid status and estimates domain from title keywords.
    """
    title = raw_job.get("title", "").lower()
    description = raw_job.get("description", "").lower()
    location = raw_job.get("location", "")

    # Detect remote
    is_remote = any(kw in title + description + location.lower() for kw in [
        "remote", "work from home", "wfh", "fully remote",
    ])

    # Detect if paid (internships often say "stipend" or "paid")
    is_paid = not any(kw in description for kw in [
        "unpaid", "no stipend", "volunteer",
    ])

    # Rough domain detection from job title
    domain_keywords = {
        "AI": ["ai", "machine learning", "ml", "data science", "nlp", "deep learning"],
        "Engineering": ["software", "backend", "frontend", "fullstack", "devops", "developer"],
        "Design": ["design", "ui/ux", "graphic", "figma"],
        "Marketing": ["marketing", "social media", "content", "seo", "digital marketing"],
        "Finance": ["finance", "accounting", "audit", "tax"],
        "HR": ["human resources", "hr", "talent", "recruitment"],
        "Sales": ["sales", "business development", "account manager"],
    }
    domain = None
    for d, keywords in domain_keywords.items():
        if any(kw in title for kw in keywords):
            domain = d
            break

    # Extract stipend (look for PKR amounts in description)
    import re
    stipend = None
    pkr_match = re.search(r"(?:PKR|Rs\.?|₨)\s*([\d,]+)", description, re.IGNORECASE)
    if pkr_match:
        try:
            stipend = int(pkr_match.group(1).replace(",", ""))
        except ValueError:
            pass

    return {
        "title": raw_job.get("title", "")[:255],
        "company": raw_job.get("company", "")[:255],
        "location": location[:255] if location else None,
        "remote": is_remote,
        "paid": is_paid,
        "stipend_pkr": stipend,
        "domain": domain,
        "source": raw_job.get("source", "linkedin"),
        "posted_at": raw_job.get("posted_at"),
    }
