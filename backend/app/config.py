"""
HireLoop PK — Application Configuration
Loads settings from environment variables / .env file
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App identity
    app_name: str = "HireLoop PK"
    app_env: str = "development"

    # JWT
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@db:5432/hireloop"
    sync_database_url: str = "postgresql://postgres:password@db:5432/hireloop"

    # Redis
    redis_url: str = "redis://redis:6379"

    # Claude AI models
    anthropic_api_key: str = ""
    claude_haiku_model: str = "claude-haiku-4-5-20251001"
    claude_sonnet_model: str = "claude-sonnet-4-6"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # Gmail
    gmail_credentials_file: str = "gmail_credentials.json"
    gmail_token_file: str = "gmail_token.json"

    # Job Scraping
    apify_api_token: str = ""
    serpapi_key: str = ""

    # Email sending (Resend.com)
    resend_api_key: str = ""
    from_email: str = "noreply@hireloop.pk"

    # Safepay Pakistan
    safepay_public_key: str = ""
    safepay_secret_key: str = ""

    # Frontend / CORS
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    # n8n webhook secret for payload validation
    webhook_secret: str = "changeme"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call get_settings() everywhere instead of Settings()."""
    return Settings()
