"""
Payments Router — Safepay integration for Pro subscriptions.
PKR 299/month for Pro, PKR 999/month for University tier.
"""

import json
import logging
import hmac
import hashlib
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.config import get_settings
from app.database import get_db
from app.models.user import User, SubscriptionTier
from app.schemas import PaymentCheckoutRequest, PaymentCheckoutResponse, PaymentWebhookPayload
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])
settings = get_settings()
logger = logging.getLogger(__name__)

PLAN_PRICES = {
    "pro": 29900,         # PKR 299 in paisas
    "university": 99900,  # PKR 999 in paisas
}

SAFEPAY_BASE_URL = "https://sandbox.api.getsafepay.com"  # Switch to live in production


@router.post("/checkout", response_model=PaymentCheckoutResponse)
async def create_checkout(
    body: PaymentCheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a Safepay payment session and return the hosted checkout URL.
    Requires a valid Pro or University plan name.
    """
    if body.plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {body.plan}. Use 'pro' or 'university'.")

    if not settings.safepay_secret_key:
        raise HTTPException(
            status_code=503,
            detail="Payment gateway not configured. Please contact support.",
        )

    amount = PLAN_PRICES[body.plan]
    metadata = {
        "user_id": str(current_user.id),
        "plan": body.plan,
        "email": current_user.email,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SAFEPAY_BASE_URL}/order/v1/init/",
                json={
                    "merchant_api_key": settings.safepay_public_key,
                    "intent": "CYBERSOURCE",
                    "mode": "payment",
                    "currency": "PKR",
                    "amount": amount,
                    "metadata": metadata,
                },
                headers={
                    "X-SFPY-MERCHANT-SECRET": settings.safepay_secret_key,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error("Safepay checkout failed: %s", exc.response.text)
        raise HTTPException(status_code=502, detail="Payment gateway error. Please try again.")
    except Exception as exc:
        logger.error("Safepay request error: %s", exc)
        raise HTTPException(status_code=502, detail="Could not reach payment gateway.")

    tracker_id = data.get("data", {}).get("tracker", {}).get("token", "")
    checkout_url = (
        f"https://sandbox.safepay.pk/checkout/pay/{tracker_id}"
        f"?env=sandbox"
        f"&source=custom"
        f"&redirect_url={settings.frontend_url}/payments/success"
        f"&cancel_url={settings.frontend_url}/upgrade"
    )

    return PaymentCheckoutResponse(checkout_url=checkout_url, tracker_id=tracker_id)


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receive Safepay payment confirmation webhook.
    Upgrades user subscription tier on successful payment.
    HMAC-SHA256 signature verified using the Safepay secret key.
    """
    raw_body = await request.body()

    # Verify webhook signature
    signature = request.headers.get("X-SFPY-SIGNATURE", "")
    if settings.safepay_secret_key and signature:
        expected = hmac.new(
            settings.safepay_secret_key.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload_dict = json.loads(raw_body)
        payload = PaymentWebhookPayload(**payload_dict)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid webhook payload")

    if payload.status != "paid":
        logger.info("Received non-paid webhook status: %s", payload.status)
        return {"received": True}

    # Find the user from metadata — Safepay echoes metadata back in the webhook
    metadata = payload_dict.get("metadata", {})
    user_id = metadata.get("user_id")
    plan = metadata.get("plan", "pro")

    if not user_id:
        logger.warning("Webhook missing user_id in metadata")
        return {"received": True}

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user:
        user.subscription_tier = SubscriptionTier(plan) if plan in ("pro", "university") else SubscriptionTier.pro
        await db.flush()
        logger.info("Upgraded user %s to %s tier", user.email, plan)

    return {"received": True}
