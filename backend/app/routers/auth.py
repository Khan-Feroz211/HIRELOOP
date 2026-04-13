"""
Auth Router — register, login, profile and Google OAuth.
All routes under /auth are public (no JWT required).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from passlib.context import CryptContext
import httpx

from app.config import get_settings
from app.database import get_db
from app.models.user import User, UserRole, SubscriptionTier
from app.schemas import UserRegister, UserLogin, Token, UserOut, OnboardingComplete
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT for the given user ID."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def _send_verification_email(email: str, name: str, token: str) -> None:
    """Send a verification email via Resend. Silently fails if not configured."""
    if not settings.resend_api_key:
        logger.info("Resend not configured — skipping verification email for %s", email)
        return

    verification_url = f"{settings.frontend_url}/auth/verify?token={token}"
    payload = {
        "from": settings.from_email,
        "to": email,
        "subject": "Verify your HireLoop PK account",
        "html": f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
          <h2 style="color:#2563eb;">🔁 Welcome to HireLoop PK, {name}!</h2>
          <p>Click the button below to verify your email address and activate your account.</p>
          <a href="{verification_url}"
             style="display:inline-block;background:#2563eb;color:#fff;padding:12px 24px;
                    border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">
            Verify Email
          </a>
          <p style="color:#6b7280;font-size:13px;">
            This link expires in 24 hours. If you didn't create an account, you can safely ignore this email.
          </p>
        </div>
        """,
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                timeout=10,
            )
    except Exception as exc:
        logger.warning("Failed to send verification email to %s: %s", email, exc)


# ─── Register ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    """Create a new student account with email + password."""
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password),
        role=UserRole.student,
        subscription_tier=SubscriptionTier.free,
        email_verified=False,
        onboarded=False,
    )
    db.add(user)
    await db.flush()

    # Issue a short-lived token for email verification (re-use access token logic)
    verification_token = create_access_token(str(user.id), expires_delta=timedelta(hours=24))
    await _send_verification_email(user.email, user.name, verification_token)

    token = create_access_token(str(user.id))
    return Token(access_token=token)


# ─── Verify Email ─────────────────────────────────────────────────────────────

@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Mark a user's email as verified from the link sent in the verification email."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired verification link",
    )
    try:
        from jose import JWTError
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception

    user.email_verified = True
    await db.flush()
    return RedirectResponse(url=f"{settings.frontend_url}/dashboard?verified=1")


# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate with email + password, returns JWT."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(str(user.id))
    return Token(access_token=token)


# ─── Me ──────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user


# ─── Onboarding ───────────────────────────────────────────────────────────────

@router.post("/onboarding-complete", response_model=UserOut)
async def complete_onboarding(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark the user's onboarding as completed."""
    current_user.onboarded = True
    await db.flush()
    return current_user


# ─── Google OAuth ─────────────────────────────────────────────────────────────

@router.get("/google")
async def google_login():
    """Redirect the browser to Google's OAuth consent screen."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Google redirects here after consent.
    Exchange the code for tokens, fetch profile, upsert user, return JWT.
    """
    async with httpx.AsyncClient() as client:
        # Exchange authorization code for access + refresh tokens
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google code")

        tokens = token_resp.json()

        # Fetch the user's Google profile
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google profile")

        profile = userinfo_resp.json()

    email = profile.get("email")
    name = profile.get("name", email)

    # Upsert: find existing user or create new one
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=name,
            role=UserRole.student,
            subscription_tier=SubscriptionTier.free,
            google_oauth_token=json.dumps(tokens),
            email_verified=True,  # Google accounts are pre-verified
            onboarded=False,
        )
        db.add(user)
    else:
        user.google_oauth_token = json.dumps(tokens)
        user.email_verified = True  # Mark verified on each Google login

    await db.flush()

    token = create_access_token(str(user.id))
    # Redirect to frontend callback page — token is stored in localStorage there
    return RedirectResponse(url=f"{settings.frontend_url}/auth/callback?token={token}")
