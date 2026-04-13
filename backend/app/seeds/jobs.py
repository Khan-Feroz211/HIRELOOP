"""
Job Board Seed Script
Run: python -m app.seeds.jobs (from the backend/ directory with DB running)

Inserts 45 realistic Pakistani internship/job listings so the job board
is never blank during a demo, even without live scraping API keys.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random

from app.models.job_listing import JobListing, JobSource


SEED_JOBS = [
    # ── AI / Data ──────────────────────────────────────────────────────────
    {"title": "AI Engineer Intern", "company": "Netsol Technologies", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 25000, "domain": "AI", "source": JobSource.rozee, "safety_score": 9.0},
    {"title": "Machine Learning Intern", "company": "10Pearls", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 30000, "domain": "AI", "source": JobSource.linkedin, "safety_score": 9.2},
    {"title": "Data Science Intern", "company": "Arbisoft", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 28000, "domain": "AI", "source": JobSource.rozee, "safety_score": 9.1},
    {"title": "NLP Research Intern", "company": "LUMS AI Lab", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "AI", "source": JobSource.mustakbil, "safety_score": 9.5},
    {"title": "Computer Vision Intern", "company": "Invo Technology", "location": "Islamabad, ICT", "remote": True, "paid": True, "stipend_pkr": 22000, "domain": "AI", "source": JobSource.linkedin, "safety_score": 8.5},
    {"title": "Data Analyst Intern", "company": "Systems Limited", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 18000, "domain": "AI", "source": JobSource.rozee, "safety_score": 8.8},
    {"title": "AI Research Intern", "company": "PRAL", "location": "Islamabad, ICT", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "AI", "source": JobSource.mustakbil, "safety_score": 8.3},

    # ── Engineering / Backend ──────────────────────────────────────────────
    {"title": "Backend Developer Intern (Python)", "company": "Confiz", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 25000, "domain": "Engineering", "source": JobSource.linkedin, "safety_score": 9.0},
    {"title": "Full Stack Intern (MERN)", "company": "Contour Software", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "Engineering", "source": JobSource.rozee, "safety_score": 8.9},
    {"title": "Node.js Intern", "company": "Navicosoft", "location": "Rawalpindi, Punjab", "remote": False, "paid": True, "stipend_pkr": 15000, "domain": "Engineering", "source": JobSource.mustakbil, "safety_score": 7.5},
    {"title": "React Developer Intern", "company": "VentureDive", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 30000, "domain": "Engineering", "source": JobSource.linkedin, "safety_score": 9.3},
    {"title": "DevOps Intern", "company": "Cloud9", "location": "Islamabad, ICT", "remote": True, "paid": True, "stipend_pkr": 22000, "domain": "Engineering", "source": JobSource.rozee, "safety_score": 8.4},
    {"title": "Mobile App Developer Intern (Flutter)", "company": "PakWheels", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "Engineering", "source": JobSource.rozee, "safety_score": 9.0},
    {"title": "QA Engineer Intern", "company": "Folio3", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 18000, "domain": "Engineering", "source": JobSource.linkedin, "safety_score": 8.7},
    {"title": "iOS Developer Intern", "company": "Macrosoft", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "Engineering", "source": JobSource.mustakbil, "safety_score": 7.8},

    # ── Design / UX ───────────────────────────────────────────────────────
    {"title": "UI/UX Designer Intern", "company": "Bramerz", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 15000, "domain": "Design", "source": JobSource.linkedin, "safety_score": 8.5},
    {"title": "Product Designer Intern", "company": "Ideate Digital", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 18000, "domain": "Design", "source": JobSource.rozee, "safety_score": 8.2},
    {"title": "Graphic Designer Intern", "company": "Omni Lab", "location": "Islamabad, ICT", "remote": False, "paid": True, "stipend_pkr": 12000, "domain": "Design", "source": JobSource.mustakbil, "safety_score": 7.6},
    {"title": "Motion Graphics Intern", "company": "DotEight", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 10000, "domain": "Design", "source": JobSource.rozee, "safety_score": 7.4},

    # ── Marketing / Growth ─────────────────────────────────────────────────
    {"title": "Digital Marketing Intern", "company": "Techlogix", "location": "Islamabad, ICT", "remote": True, "paid": True, "stipend_pkr": 12000, "domain": "Marketing", "source": JobSource.linkedin, "safety_score": 8.8},
    {"title": "SEO Specialist Intern", "company": "W3 Solutions", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 10000, "domain": "Marketing", "source": JobSource.rozee, "safety_score": 8.0},
    {"title": "Social Media Manager Intern", "company": "Daraz.pk", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 15000, "domain": "Marketing", "source": JobSource.linkedin, "safety_score": 9.1},
    {"title": "Content Writer Intern", "company": "Bookme.pk", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 8000, "domain": "Marketing", "source": JobSource.mustakbil, "safety_score": 8.4},
    {"title": "Growth Hacker Intern", "company": "Seedstars Lahore", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 20000, "domain": "Marketing", "source": JobSource.linkedin, "safety_score": 8.6},

    # ── Finance / Business ─────────────────────────────────────────────────
    {"title": "Business Analyst Intern", "company": "MCB Bank", "location": "Karachi, Sindh", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "Finance", "source": JobSource.linkedin, "safety_score": 9.4},
    {"title": "Finance Intern", "company": "HBL Pakistan", "location": "Karachi, Sindh", "remote": False, "paid": True, "stipend_pkr": 22000, "domain": "Finance", "source": JobSource.rozee, "safety_score": 9.5},
    {"title": "Investment Banking Intern", "company": "United Bank Limited", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 25000, "domain": "Finance", "source": JobSource.linkedin, "safety_score": 9.3},
    {"title": "Fintech Product Intern", "company": "Easypaisa", "location": "Islamabad, ICT", "remote": False, "paid": True, "stipend_pkr": 28000, "domain": "Finance", "source": JobSource.linkedin, "safety_score": 9.0},

    # ── HR / Operations ────────────────────────────────────────────────────
    {"title": "HR Intern", "company": "Unilever Pakistan", "location": "Karachi, Sindh", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "HR", "source": JobSource.linkedin, "safety_score": 9.6},
    {"title": "Talent Acquisition Intern", "company": "P&G Pakistan", "location": "Karachi, Sindh", "remote": False, "paid": True, "stipend_pkr": 22000, "domain": "HR", "source": JobSource.linkedin, "safety_score": 9.7},
    {"title": "Operations Intern", "company": "Nestlé Pakistan", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "HR", "source": JobSource.rozee, "safety_score": 9.5},

    # ── Sales ──────────────────────────────────────────────────────────────
    {"title": "Sales Intern", "company": "Jazz Pakistan", "location": "Islamabad, ICT", "remote": False, "paid": True, "stipend_pkr": 15000, "domain": "Sales", "source": JobSource.rozee, "safety_score": 8.8},
    {"title": "Business Development Intern", "company": "Treet Corporation", "location": "Lahore, Punjab", "remote": False, "paid": True, "stipend_pkr": 18000, "domain": "Sales", "source": JobSource.mustakbil, "safety_score": 8.3},
    {"title": "Account Management Intern", "company": "Google Pakistan Ops", "location": "Karachi, Sindh", "remote": True, "paid": True, "stipend_pkr": 35000, "domain": "Sales", "source": JobSource.linkedin, "safety_score": 9.8},

    # ── Remote / Startups ──────────────────────────────────────────────────
    {"title": "Full Stack Developer (Remote)", "company": "Uptech Labs", "location": "Remote", "remote": True, "paid": True, "stipend_pkr": 40000, "domain": "Engineering", "source": JobSource.linkedin, "safety_score": 8.0},
    {"title": "AI Product Manager Intern", "company": "Airlift Alumni Ventures", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 30000, "domain": "AI", "source": JobSource.linkedin, "safety_score": 8.2},
    {"title": "Blockchain Developer Intern", "company": "Alchemy Technologies PK", "location": "Islamabad, ICT", "remote": True, "paid": True, "stipend_pkr": 25000, "domain": "Engineering", "source": JobSource.rozee, "safety_score": 7.2},
    {"title": "Research Intern (AI Policy)", "company": "Bytes for All", "location": "Islamabad, ICT", "remote": True, "paid": True, "stipend_pkr": 18000, "domain": "AI", "source": JobSource.mustakbil, "safety_score": 8.9},

    # ── Low/no stipend — clearly labeled ───────────────────────────────────
    {"title": "Software Engineering Intern (Unpaid)", "company": "StartupHub Peshawar", "location": "Peshawar, KPK", "remote": False, "paid": False, "stipend_pkr": None, "domain": "Engineering", "source": JobSource.mustakbil, "safety_score": 6.5},
    {"title": "Marketing Intern (Unpaid)", "company": "Local Brand Co.", "location": "Rawalpindi, Punjab", "remote": False, "paid": False, "stipend_pkr": None, "domain": "Marketing", "source": JobSource.rozee, "safety_score": 5.8},

    # ── Peshawar / other cities ────────────────────────────────────────────
    {"title": "Software Developer Intern", "company": "CECOS University Spin-off", "location": "Peshawar, KPK", "remote": False, "paid": True, "stipend_pkr": 12000, "domain": "Engineering", "source": JobSource.mustakbil, "safety_score": 7.8},
    {"title": "Cybersecurity Intern", "company": "NUST Innovation Center", "location": "Islamabad, ICT", "remote": False, "paid": True, "stipend_pkr": 20000, "domain": "Engineering", "source": JobSource.rozee, "safety_score": 9.2},
    {"title": "Cloud Intern (AWS)", "company": "Inbox Business Technologies", "location": "Lahore, Punjab", "remote": True, "paid": True, "stipend_pkr": 22000, "domain": "Engineering", "source": JobSource.linkedin, "safety_score": 8.7},
]


def _random_posted_at() -> datetime:
    """Return a random datetime within the last 30 days."""
    days_ago = random.randint(0, 30)
    return datetime.now(timezone.utc) - timedelta(days=days_ago)


async def seed_jobs() -> None:
    """Insert seed job listings, skipping any that would duplicate by title+company."""
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select as sa_select
        existing = await session.execute(
            sa_select(JobListing.title, JobListing.company)
        )
        existing_keys = {(r.title, r.company) for r in existing.all()}

        inserted = 0
        for job_data in SEED_JOBS:
            key = (job_data["title"], job_data["company"])
            if key in existing_keys:
                continue

            job = JobListing(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data.get("location"),
                remote=job_data.get("remote", False),
                paid=job_data.get("paid", True),
                stipend_pkr=job_data.get("stipend_pkr"),
                domain=job_data.get("domain"),
                source=job_data["source"],
                safety_score=job_data.get("safety_score", 5.0),
                posted_at=_random_posted_at(),
            )
            session.add(job)
            inserted += 1

        await session.commit()
        print(f"✅ Seeded {inserted} job listings ({len(existing_keys)} already existed).")


if __name__ == "__main__":
    asyncio.run(seed_jobs())
