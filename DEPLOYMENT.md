# HireLoop PK — Deployment Guide

This guide walks you through deploying HireLoop PK on a Hetzner VPS with Docker Compose, Nginx + SSL, and a Vercel frontend.

---

## Prerequisites

- A Hetzner Cloud VPS (CX21 or higher — 2 vCPU, 4 GB RAM recommended)
- A domain pointing to your VPS IP (`api.hireloop.pk`)
- A Vercel account for the Next.js frontend
- API keys: Anthropic Claude, Google OAuth, Safepay, Resend

---

## 1. Server Setup (Hetzner VPS)

```bash
# SSH into your new server
ssh root@YOUR_VPS_IP

# Update packages
apt update && apt upgrade -y

# Install Docker + Docker Compose
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Create a non-root user
adduser deploy
usermod -aG docker deploy
su - deploy
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/Khan-Feroz211/HIRELOOP.git
cd HIRELOOP
```

---

## 3. Configure Environment Variables

```bash
# Copy the example and fill in all values
cp .env.example .env
nano .env
```

**Required variables to set:**
```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@db:5432/hireloop
SYNC_DATABASE_URL=postgresql://postgres:yourpassword@db:5432/hireloop
REDIS_URL=redis://redis:6379

ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://api.hireloop.pk/auth/google/callback

RESEND_API_KEY=re_...
FROM_EMAIL=noreply@hireloop.pk

SAFEPAY_PUBLIC_KEY=...
SAFEPAY_SECRET_KEY=...

FRONTEND_URL=https://hireloop.pk
CORS_ORIGINS=https://hireloop.pk

WEBHOOK_SECRET=<generate a strong random string>
APP_ENV=production
```

---

## 4. Launch Backend with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, FastAPI)
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Seed the job board (first time only)
docker compose exec backend python -m app.seeds.jobs

# Check logs
docker compose logs -f backend
```

---

## 5. Configure Nginx + SSL

```bash
# Install Nginx and Certbot
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config for the API
nano /etc/nginx/sites-available/hireloop-api
```

Paste this config:
```nginx
server {
    server_name api.hireloop.pk;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable the site
ln -s /etc/nginx/sites-available/hireloop-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get SSL certificate
certbot --nginx -d api.hireloop.pk

# Certbot will auto-add SSL config — verify with:
certbot renew --dry-run
```

---

## 6. Deploy Frontend to Vercel

```bash
# From your local machine, in the frontend/ directory:
npm install -g vercel
cd frontend
vercel

# Set these environment variables in the Vercel dashboard:
# NEXT_PUBLIC_API_URL = https://api.hireloop.pk
```

Or connect your GitHub repo to Vercel for automatic deployments on push.

**Vercel Project Settings:**
- Framework: Next.js
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `.next`

---

## 7. Set Up Google OAuth Redirect URIs

In the Google Cloud Console:
1. Go to **APIs & Services → Credentials → Your OAuth 2.0 Client**
2. Add to **Authorized redirect URIs**: `https://api.hireloop.pk/auth/google/callback`
3. Add to **Authorized JavaScript origins**: `https://hireloop.pk`

---

## 8. Configure n8n Automation Workflows

### Start n8n

Add to your `docker-compose.yml`:
```yaml
n8n:
  image: n8nio/n8n
  restart: always
  ports:
    - "5678:5678"
  environment:
    - N8N_HOST=n8n.hireloop.pk
    - WEBHOOK_URL=https://n8n.hireloop.pk
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=admin
    - N8N_BASIC_AUTH_PASSWORD=<strong_password>
  volumes:
    - n8n_data:/home/node/.n8n
```

### Import Workflows

1. Open `https://n8n.hireloop.pk` in your browser
2. Go to **Workflows → Import from File**
3. Import each JSON file from `automation/workflows/`:
   - `gmail_parser.json` — Gmail trigger → parse email → update application status
   - `daily_ghost_scan.json` — Daily cron → run ghost scores on all stale applications

### Configure Workflow Credentials

In n8n, add:
- **Gmail OAuth2** credential (use the same Google OAuth app)
- **HTTP Header Auth** for the HireLoop webhook:
  - Header: `X-Webhook-Secret`
  - Value: your `WEBHOOK_SECRET` from `.env`

### Workflow: Gmail Auto-Parser

**Trigger:** Gmail node — watches for emails matching "application|interview|offer|rejected"  
**Flow:** Gmail → HTTP Request (POST `https://api.hireloop.pk/webhooks/gmail-parse`) → done  
**Payload sent:**
```json
{
  "user_email": "{{ $json.from }}",
  "email_subject": "{{ $json.subject }}",
  "email_body": "{{ $json.text }}",
  "received_at": "{{ $json.date }}"
}
```

---

## 9. Safepay Payment Webhook

In the Safepay dashboard:
1. Go to **Developer → Webhooks**
2. Add webhook URL: `https://api.hireloop.pk/payments/webhook`
3. Subscribe to event: `payment.paid`
4. Copy the webhook signing secret and add it to your `.env` as `SAFEPAY_SECRET_KEY`

---

## 10. Maintenance

```bash
# Update the backend
git pull
docker compose build backend
docker compose up -d backend
docker compose exec backend alembic upgrade head

# View logs
docker compose logs -f backend

# Backup the database
docker compose exec db pg_dump -U postgres hireloop > backup_$(date +%Y%m%d).sql

# Renew SSL certificate (auto-renews via cron, but manual check:)
certbot renew
```

---

## Architecture Diagram

```
                      ┌──────────────┐
                      │   Vercel     │
                      │  (Next.js)   │
                      │ hireloop.pk  │
                      └──────┬───────┘
                             │ HTTPS
                      ┌──────▼───────┐
                      │    Nginx     │
                      │ api.hireloop │
                      └──────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌────▼────┐  ┌─────▼─────┐
        │  FastAPI  │  │  Redis  │  │   n8n     │
        │  :8000    │  │  :6379  │  │  :5678    │
        └─────┬─────┘  └─────────┘  └─────┬─────┘
              │                           │
        ┌─────▼──────┐             ┌──────▼──────┐
        │ PostgreSQL │             │   Gmail     │
        │  :5432     │             │   OAuth     │
        └────────────┘             └─────────────┘
```
