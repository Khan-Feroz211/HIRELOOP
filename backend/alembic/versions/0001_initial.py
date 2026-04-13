"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ───────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("student", "admin", name="userrole"),
            nullable=False,
            server_default="student",
        ),
        sa.Column("google_oauth_token", sa.Text, nullable=True),
        sa.Column(
            "subscription_tier",
            sa.Enum("free", "pro", "university", name="subscriptiontier"),
            nullable=False,
            server_default="free",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── companies ────────────────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("remote_score", sa.Float, server_default="5.0"),
        sa.Column("ghost_rate", sa.Float, server_default="50.0"),
        sa.Column("safety_score", sa.Float, server_default="5.0"),
        sa.Column("verified_remote", sa.Boolean, server_default="false"),
        sa.Column("female_friendly", sa.Boolean, server_default="false"),
        sa.Column("flags", postgresql.JSON, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_companies_name", "companies", ["name"], unique=True)

    # ── applications ─────────────────────────────────────────────────────────
    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("linkedin_url", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "applied", "confirmed", "interview", "offer", "rejected", "ghosted",
                name="applicationstatus",
            ),
            nullable=False,
            server_default="applied",
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ghost_score", sa.Float, server_default="0.0"),
        sa.Column("days_since_contact", sa.Integer, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    # ── email_logs ────────────────────────────────────────────────────────────
    op.create_table(
        "email_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("email_subject", sa.Text, nullable=True),
        sa.Column("email_body", sa.Text, nullable=True),
        sa.Column("parsed_company", sa.String(255), nullable=True),
        sa.Column("parsed_status", sa.String(100), nullable=True),
        sa.Column("parsed_interview_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_email_logs_user_id", "email_logs", ["user_id"])

    # ── job_listings ──────────────────────────────────────────────────────────
    op.create_table(
        "job_listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote", sa.Boolean, server_default="false"),
        sa.Column("paid", sa.Boolean, server_default="true"),
        sa.Column("stipend_pkr", sa.Integer, nullable=True),
        sa.Column("domain", sa.String(100), nullable=True),
        sa.Column(
            "source",
            sa.Enum("rozee", "linkedin", "mustakbil", name="jobsource"),
            nullable=False,
        ),
        sa.Column("safety_score", sa.Float, server_default="5.0"),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_job_listings_title", "job_listings", ["title"])
    op.create_index("ix_job_listings_company", "job_listings", ["company"])
    op.create_index("ix_job_listings_domain", "job_listings", ["domain"])


def downgrade() -> None:
    op.drop_table("job_listings")
    op.drop_table("email_logs")
    op.drop_table("applications")
    op.drop_table("companies")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS jobsource")
    op.execute("DROP TYPE IF EXISTS applicationstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontier")
    op.execute("DROP TYPE IF EXISTS userrole")
