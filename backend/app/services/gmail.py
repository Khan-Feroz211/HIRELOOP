"""
Gmail Service — reads recruitment emails from the user's Gmail inbox.
Uses Gmail API with OAuth2 (Google credentials).
The n8n workflow handles polling; this service handles direct API calls.
"""

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Keywords that identify recruitment-related emails
RECRUITMENT_KEYWORDS = [
    "application received",
    "thank you for applying",
    "we received your application",
    "your application for",
    "application confirmation",
    "interview invitation",
    "interview request",
    "job offer",
    "offer letter",
    "regret to inform",
    "unfortunately",
    "not moving forward",
]


def get_gmail_service(oauth_token_json: str):
    """
    Build the Gmail API service from a stored OAuth token.
    oauth_token_json: JSON string of the Google OAuth token dict.
    """
    token_data = json.loads(oauth_token_json)
    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    return build("gmail", "v1", credentials=creds)


def _decode_email_body(payload: dict) -> str:
    """Recursively decode email body from Gmail message payload."""
    import base64

    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            elif "parts" in part:
                body += _decode_email_body(part)
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return body


def fetch_recruitment_emails(
    oauth_token_json: str,
    max_results: int = 20,
) -> List[Dict]:
    """
    Fetch recent recruitment-related emails from the user's Gmail.
    Returns list of dicts with subject, body, received_at.
    """
    try:
        service = get_gmail_service(oauth_token_json)

        # Build the Gmail search query
        query = " OR ".join(f'"{kw}"' for kw in RECRUITMENT_KEYWORDS[:5])

        result = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()

        messages = result.get("messages", [])
        emails = []

        for msg_ref in messages:
            try:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="full",
                ).execute()

                headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
                subject = headers.get("Subject", "")
                date_str = headers.get("Date", "")
                body = _decode_email_body(msg["payload"])

                emails.append({
                    "gmail_id": msg_ref["id"],
                    "subject": subject,
                    "body": body,
                    "received_at": date_str,
                })

            except HttpError as e:
                logger.error(f"Failed to fetch message {msg_ref['id']}: {e}")
                continue

        return emails

    except Exception as e:
        logger.error(f"Gmail service error: {e}")
        return []
