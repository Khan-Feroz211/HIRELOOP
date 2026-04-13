"""
HireLoop PK — FastAPI Application Entry Point
Pakistan's first AI-powered job application intelligence platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.middleware.rate_limit import limiter
from app.routers import auth, applications, ai, jobs, webhooks, payments

settings = get_settings()

# ─── App Init ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="HireLoop PK API",
    description="Pakistan's first AI-powered job application intelligence platform. "
                "Stop getting ghosted. Start getting hired.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter state to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(ai.router)
app.include_router(jobs.router)
app.include_router(webhooks.router)
app.include_router(payments.router)


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/", tags=["health"])
async def root():
    return {
        "product": "HireLoop PK",
        "tagline": "Stop getting ghosted. Start getting hired.",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
