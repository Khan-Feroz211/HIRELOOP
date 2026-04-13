"""
Claude AI Service — all LLM calls go through here.
Never call Anthropic directly from a route handler.

Models used:
  - claude-haiku: ghost scoring (cheap, runs on every app daily)
  - claude-sonnet: interview prep + follow-up emails (smart, user-triggered)
"""

import json
import logging
from typing import Any, Dict, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Shared Anthropic client (re-used across requests)
_client: Optional[anthropic.AsyncAnthropic] = None


def get_client() -> anthropic.AsyncAnthropic:
    """Lazy-init the Anthropic async client."""
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


SYSTEM_PROMPT = """You are HireLoop AI — a helpful job application intelligence assistant 
built specifically for Pakistani university students and fresh graduates.

Always return valid JSON unless explicitly told otherwise.
Never hallucinate company data. If information is unknown, flag it explicitly.
Keep tone warm and professional — like a helpful senior batchmate.

Pakistan job market context you must always apply:
- Major platforms: LinkedIn, Rozee.pk, Mustakbil.com
- Ghosting window: 7–14 days after confirmation email is common
- Remote roles often claim remote but require in-person presence
- Female users face real safety concerns with in-person roles
- Internship stipends range PKR 8,000–35,000/month
- Top hiring cities: Karachi, Lahore, Islamabad
- Common scam signals: WhatsApp-only HR, no company website, cash payment, "training fee" required"""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def _call_claude(
    prompt: str,
    model: str,
    max_tokens: int = 1024,
) -> str:
    """Raw Claude call with retry logic. Returns the text response."""
    client = get_client()
    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def _call_claude_json(
    prompt: str,
    model: str,
    max_tokens: int = 1024,
    fallback: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Call Claude and parse the response as JSON. Returns fallback on error."""
    try:
        raw = await _call_claude(prompt, model, max_tokens)
        # Strip markdown code fences if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception as e:
        logger.error(f"Claude call failed: {e}")
        if fallback is not None:
            return fallback
        raise


# ─── Ghost Risk Scorer ────────────────────────────────────────────────────────

GHOST_FALLBACK = {
    "ghost_score": 50,
    "risk_level": "medium",
    "reason": "Unable to analyze at this time. Please try again later.",
    "recommended_action": "Follow up with a polite email to check your application status.",
}


async def score_ghost_risk(
    company_name: str,
    industry: str,
    days_since_contact: int,
    app_volume: str = "medium",
) -> Dict[str, Any]:
    """
    Use Claude Haiku to score the ghost risk for a single application.
    Cheap model — safe to run on every application daily.
    """
    prompt = f"""Score the ghost risk for this job application in Pakistan:

Company: {company_name}
Industry: {industry or "Unknown"}
Days since last contact: {days_since_contact}
Company application volume: {app_volume}

Return ONLY valid JSON matching this exact schema:
{{
  "ghost_score": <integer 0-100>,
  "risk_level": "<low|medium|high>",
  "reason": "<one sentence explaining the score>",
  "recommended_action": "<specific action the applicant should take right now>"
}}"""

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_haiku_model,
        fallback=GHOST_FALLBACK,
    )


# ─── Follow-Up Email Generator ────────────────────────────────────────────────

async def generate_followup_emails(
    applicant_name: str,
    company: str,
    job_title: str,
    days_since_applied: int,
    prior_contact: bool,
) -> Dict[str, Any]:
    """
    Use Claude Sonnet to generate 3 follow-up email variants.
    Smart model — user-triggered, not run in bulk.
    """
    contact_note = "The applicant has previously contacted HR." if prior_contact else "No prior follow-up contact."

    prompt = f"""Generate 3 professional follow-up email variants for a Pakistani job applicant.

Applicant name: {applicant_name}
Company: {company}
Job title: {job_title}
Days since applying: {days_since_applied}
Prior contact: {contact_note}

Return ONLY valid JSON matching this exact schema:
{{
  "variant_a": {{
    "subject": "<email subject>",
    "body": "<full email body>",
    "tone": "polite"
  }},
  "variant_b": {{
    "subject": "<email subject>",
    "body": "<full email body>",
    "tone": "value-add"
  }},
  "variant_c": {{
    "subject": "<email subject>",
    "body": "<full email body>",
    "tone": "final-nudge"
  }}
}}

Guidelines:
- variant_a: Polite status check, respectful of their time
- variant_b: Mentions a recent relevant skill or project to add value  
- variant_c: Friendly final nudge, mentions moving on if no response
- All emails should be in English, professional but warm
- Keep each email under 150 words
- Sign off as {applicant_name}"""

    fallback = {
        "variant_a": {
            "subject": f"Following up on my {job_title} application",
            "body": f"Dear Hiring Team,\n\nI hope this email finds you well. I'm writing to follow up on my application for the {job_title} position at {company}, submitted {days_since_applied} days ago.\n\nI remain very interested in this opportunity and would love to discuss how I can contribute to your team.\n\nThank you for your time.\n\nBest regards,\n{applicant_name}",
            "tone": "polite",
        },
        "variant_b": {
            "subject": f"Still excited about {job_title} at {company}",
            "body": f"Dear Hiring Team,\n\nI wanted to follow up on my {job_title} application. Since applying, I've been actively working on relevant projects and would love the chance to share how my skills align with your needs.\n\nI'm very enthusiastic about the opportunity to join {company}.\n\nBest regards,\n{applicant_name}",
            "tone": "value-add",
        },
        "variant_c": {
            "subject": f"Final follow-up: {job_title} Application",
            "body": f"Dear Hiring Team,\n\nThis is my final follow-up regarding my {job_title} application. I understand you're very busy, but a quick update on the status would be greatly appreciated.\n\nI remain interested in joining {company} and hope to hear from you soon.\n\nThank you,\n{applicant_name}",
            "tone": "final-nudge",
        },
    }

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_sonnet_model,
        max_tokens=2048,
        fallback=fallback,
    )


# ─── Interview Prep ───────────────────────────────────────────────────────────

async def generate_interview_prep(job_description: str) -> Dict[str, Any]:
    """
    Use Claude Sonnet to generate role-specific interview prep.
    Returns 10 questions, 10 answers, weak areas, and tips.
    """
    prompt = f"""Analyze this job description and create comprehensive interview preparation for a Pakistani fresh graduate:

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON matching this exact schema:
{{
  "role_summary": "<2-3 sentence summary of the role and what they're looking for>",
  "likely_questions": ["<question 1>", "<question 2>", ..., "<question 10>"],
  "suggested_answers": ["<answer 1>", "<answer 2>", ..., "<answer 10>"],
  "weak_areas": ["<potential weakness 1>", "<potential weakness 2>", "<potential weakness 3>"],
  "preparation_tips": "<specific tips for this role including Pakistan market context>"
}}

Make answers STAR-format (Situation, Task, Action, Result) where applicable.
Focus on skills Pakistani fresh graduates typically have.
Answers should be 3-4 sentences each."""

    fallback = {
        "role_summary": "Unable to analyze the job description at this time.",
        "likely_questions": [
            "Tell me about yourself.",
            "Why do you want to work here?",
            "What are your greatest strengths?",
        ],
        "suggested_answers": [
            "Briefly describe your education and relevant skills.",
            "Explain your genuine interest in the company and role.",
            "Highlight 2-3 relevant technical or soft skills.",
        ],
        "weak_areas": ["Technical depth", "Industry experience"],
        "preparation_tips": "Research the company thoroughly and prepare specific examples from your projects.",
    }

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_sonnet_model,
        max_tokens=3000,
        fallback=fallback,
    )


# ─── Company Safety Scorer ────────────────────────────────────────────────────

async def score_company_safety(
    company_name: str,
    job_type: str,
    claimed_location: str,
    job_description: str,
) -> Dict[str, Any]:
    """
    Use Claude Haiku to assess a company's safety and legitimacy.
    Especially important for female job seekers and remote claims.
    """
    prompt = f"""Evaluate this company and job posting for safety in the Pakistani job market:

Company: {company_name}
Job type: {job_type}
Claimed location: {claimed_location}
Job description excerpt:
{job_description[:1000]}

Assess for:
1. Whether remote work claims seem genuine
2. Overall safety for in-person meetings
3. Female-friendliness indicators
4. Scam signals (WhatsApp-only HR, training fees, no website, cash payment, etc.)

Return ONLY valid JSON matching this exact schema:
{{
  "remote_verified": <true|false>,
  "safety_score": <integer 1-10>,
  "female_friendly_score": <integer 1-10>,
  "flags": ["<flag 1>", "<flag 2>", ...],
  "recommendation": "<Safe|Proceed with caution|Avoid>"
}}"""

    fallback = {
        "remote_verified": False,
        "safety_score": 5,
        "female_friendly_score": 5,
        "flags": ["Unable to analyze — please research independently"],
        "recommendation": "Proceed with caution",
    }

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_haiku_model,
        fallback=fallback,
    )


# ─── Weekly Summary ───────────────────────────────────────────────────────────

async def generate_weekly_summary(applications: list) -> Dict[str, Any]:
    """
    Use Claude Haiku to summarize the user's job search week.
    Runs on demand (user-triggered from dashboard).
    """
    # Build a compact summary to avoid token overuse
    summary_data = [
        {
            "company": a.get("company_name", "Unknown"),
            "status": a.get("status", "applied"),
            "days_since_contact": a.get("days_since_contact", 0),
            "ghost_score": a.get("ghost_score", 0),
        }
        for a in applications[:50]  # Cap at 50 to control token usage
    ]

    prompt = f"""Analyze this Pakistani student's job search data and provide a weekly summary:

Applications data:
{json.dumps(summary_data, indent=2)}

Return ONLY valid JSON matching this exact schema:
{{
  "summary_paragraph": "<2-3 sentence overview of their job search week>",
  "response_rate_percent": <float 0-100>,
  "fastest_responding_industry": "<industry name or 'N/A'>",
  "top_actions_this_week": ["<action 1>", "<action 2>", "<action 3>"],
  "motivational_line": "<one encouraging sentence tailored to their situation>"
}}

Be honest but encouraging. Use Pakistani context (acknowledge market realities)."""

    fallback = {
        "summary_paragraph": "You've been actively applying — keep it up! The Pakistani job market is competitive but your persistence will pay off.",
        "response_rate_percent": 0.0,
        "fastest_responding_industry": "N/A",
        "top_actions_this_week": [
            "Follow up on applications older than 7 days",
            "Update your LinkedIn profile",
            "Apply to 3 new positions today",
        ],
        "motivational_line": "Every rejection is one step closer to your yes — keep going!",
    }

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_haiku_model,
        fallback=fallback,
    )


# ─── Email Parser ─────────────────────────────────────────────────────────────

async def parse_recruitment_email(
    email_subject: str,
    email_body: str,
) -> Dict[str, Any]:
    """
    Use Claude Haiku to extract structured data from a recruitment email.
    Called by the n8n webhook when Gmail receives an application email.
    """
    prompt = f"""Extract structured data from this recruitment/job application email:

Subject: {email_subject}
Body:
{email_body[:2000]}

Return ONLY valid JSON:
{{
  "company_name": "<company name or null>",
  "application_status": "<applied|confirmed|interview|offer|rejected|unknown>",
  "interview_date": "<ISO 8601 datetime or null>",
  "contact_person": "<name or null>",
  "key_info": "<one sentence summary>"
}}"""

    fallback = {
        "company_name": None,
        "application_status": "unknown",
        "interview_date": None,
        "contact_person": None,
        "key_info": "Could not parse email automatically",
    }

    return await _call_claude_json(
        prompt=prompt,
        model=settings.claude_haiku_model,
        fallback=fallback,
    )
