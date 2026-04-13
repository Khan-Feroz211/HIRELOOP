"""
Rate Limiting Middleware using SlowAPI (wraps limits library).
Free users: 10 AI requests/minute
Pro users:  50 AI requests/minute
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Default key: remote IP — upgraded per route using user ID
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_for_user(request: Request) -> str:
    """
    Return the rate limit string based on the user's subscription tier.
    Falls back to free limits if user is not authenticated yet.
    """
    user = getattr(request.state, "user", None)
    if user and getattr(user, "subscription_tier", "free") in ("pro", "university"):
        return "50/minute"
    return "10/minute"
