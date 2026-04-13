# 🔁 HireLoop PK

**Pakistan's first AI-powered job application intelligence platform.**

> *Stop getting ghosted. Start getting hired.*

Built for Pakistani university students and fresh graduates who apply on LinkedIn, get confirmation emails, then complete silence — ghosting. HireLoop gives you the tools to track, follow up, and score your applications intelligently.

---

## 🎯 Features

| Feature | Description |
|---|---|
| **Kanban Tracker** | Visual board: Applied → Confirmed → Interview → Offer |
| **Ghost Risk Scorer** | AI scores 0-100 ghost risk for each application daily |
| **Follow-Up Email Generator** | 3 tailored email variants with Claude AI |
| **Interview Prep AI** | 10 questions + STAR-format answers from any job description |
| **Company Safety Scorer** | Scam detection + female-friendly scoring |
| **Gmail Auto-Parser** | Connect Gmail — statuses update automatically |
| **Job Board** | Scraped listings from Rozee.pk, LinkedIn, Mustakbil |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy async + Alembic |
| Frontend | Next.js 14 + Tailwind CSS + React Query |
| AI | Claude API (Haiku for bulk, Sonnet for smart features) |
| Automation | n8n (self-hosted) |
| Database | PostgreSQL (Supabase free tier in dev) |
| Cache | Redis (Upstash free tier in dev) |
| Deployment | Hetzner CX11 VPS + Docker Compose |
| Frontend Host | Vercel (free tier) |

---

## 🚀 Quick Start

### 1. Configure

```bash
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY
```

### 2. Run with Docker

```bash
docker compose up
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |

---

## 📁 Structure

```
├── backend/           # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/    # User, Application, Company, EmailLog, JobListing
│   │   ├── routers/   # auth, applications, ai, jobs, webhooks
│   │   ├── services/  # claude, gmail, scraper, ghost_scorer
│   │   └── schemas/   # Pydantic v2 schemas
│   └── alembic/       # DB migrations
├── frontend/          # Next.js 14
│   ├── app/
│   │   ├── dashboard/ # Stats + weekly AI summary
│   │   ├── tracker/   # Kanban board
│   │   ├── jobs/      # Job board
│   │   └── prep/      # Interview prep AI
│   └── lib/api.ts     # Axios client
├── automation/        # n8n workflow JSONs
├── ai/prompts/        # Claude prompt templates
├── infra/             # Nginx + production Docker Compose
└── docker-compose.yml
```

---

## 💰 Pricing

| Tier | Price | Features |
|---|---|---|
| Free | PKR 0/forever | 5 apps, basic tracker |
| Student Pro | PKR 299/month | Unlimited + all AI features |
| University | PKR 15,000–25,000/month | Bulk accounts + analytics |

---

## 👨‍💻 Developer

**Feroz Khan** · AI Engineering student @ NUTECH, Islamabad · [@Khan-Feroz211](https://github.com/Khan-Feroz211)
