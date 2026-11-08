# Studio Growth OS v2.0

> AI-powered customer acquisition, conversational selling, revenue conversion, and business growth platform for photography studios.

## 🏗️ Architecture

```
studio-growth-os/
├── apps/
│   ├── web/          # Next.js 14 (App Router) - Public site + Admin dashboard
│   └── api/          # FastAPI - AI Agent, Connectors, Webhooks, Payments
├── packages/
│   ├── prisma/       # Shared database schema + migrations + seed
│   ├── ui/           # Shared shadcn/ui components
│   └── config/       # Shared TypeScript/Python config
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Accounts: Meta Developer, Google Cloud, Razorpay

### 1. Clone & Configure
```bash
cd studio-growth-os
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Local Development
```bash
# Start all services (PostgreSQL, Redis, MinIO, Web, API, Worker)
docker-compose up -d

# Or start individually:
# Terminal 1: docker-compose up postgres redis minio
# Terminal 2: cd apps/web && npm run dev
# Terminal 3: cd apps/api && uvicorn main:app --reload
# Terminal 4: cd apps/api && python -m workers.main
```

### 3. Initialize Database
```bash
cd packages/prisma
npm install
npx prisma generate
npx prisma migrate dev --name init
npx tsx seed.ts
```

### 4. Access Applications
- **Public Site**: http://localhost:3000 (or studiox.rungrow.in via /etc/hosts)
- **Admin Dashboard**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## 🔧 Environment Variables

See `.env.example` for all required variables. Key categories:

| Category | Variables |
|----------|-----------|
| **Database** | `DATABASE_URL` |
| **Redis** | `REDIS_URL` |
| **Auth** | `SECRET_KEY`, `JWT_SECRET` |
| **Meta/WhatsApp** | `META_APP_ID`, `META_APP_SECRET`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` |
| **YouTube** | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_API_KEY` |
| **Google Business Profile** | `GBP_CLIENT_ID`, `GBP_CLIENT_SECRET` |
| **Razorpay** | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` |
| **AI** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` |
| **Storage (R2/S3)** | `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL` |

## 📦 Key Features

### Public Studio Site (`/`)
- Hero with tagline, CTA, trust indicators
- Occasion-based package showcase (Birthday, Maternity, Baby Shower, Marriage, Full Marriage)
- Service areas, contact info, social links
- SEO/GEO schema markup (LocalBusiness, Service, FAQPage, Review)
- WhatsApp handoff, click-to-call, estimator

### Admin Dashboard (`/admin`)
- **Today**: Shoots, prep tasks, unresponded leads, pending approvals
- **Tomorrow**: Upcoming shoots, prep checklist, confirmations needed
- **This Week**: Calendar heatmap, pipeline value, utilization %
- **This Month / Past Months**: Trends (leads, revenue, conversion, CAC, LTV)
- Time grain selector: today / tomorrow / 7d / 30d / 90d / custom
- Drill-through to filtered lists with URL-deep-linkable state
- Role-based visibility (owner/manager/sales/editor/viewer)

### AI Sales Agent (`/api/v1/agent`)
- **Tools**: check_availability, calculate_quote, compare_packages, hold_slot, release_slot, send_quote, create_payment_link, request_owner_approval, handoff_to_human
- **Policy Engine**: Margin floors, discount ceilings, approval thresholds
- **Governance**: Execution traces, prompt-injection detection, kill switch, evaluation harness
- **Conversation**: Multi-turn, context-aware, tool-call logging

### Connectors (`/api/v1/connectors`)
- **Instagram**: Comment-to-DM, DM intake, lead forms, Click-to-WhatsApp campaigns
- **YouTube**: Comment monitoring, video analytics, channel insights
- **WhatsApp**: Session messages, templates, catalog, interactive messages
- **Google Business Profile**: Posts, photos, reviews, Q&A, insights
- Health monitoring, capability reporting, manual sync trigger

### Payments (`/api/v1/payments`)
- Razorpay integration (orders, payments, refunds, webhooks)
- Idempotent processing, signature verification
- Payment → booking state transition
- Daily reconciliation job

### Webhooks (`/api/v1/webhooks`)
- Instagram, WhatsApp, YouTube, Razorpay, Generic
- Signature verification, idempotency, dead-letter queue
- Background processing with retry/backoff

## 🗄️ Database Schema (Prisma)

Key models:
- **Tenant, User, Membership** - Multi-tenant auth with RBAC
- **Contact, Lead, InboundEvent** - Lead capture & identity resolution
- **ServicePackage, PricingRule** - Versioned pricing with margin/discount controls
- **Quote, QuoteItem, Booking, SlotHold** - Commerce & scheduling
- **Payment** - Razorpay integration with reconciliation
- **Conversation, Message, AgentTrace** - AI agent conversations
- **AttributionEvent, PredictiveScore, BenchmarkAggregate** - Analytics
- **ConnectorConfig, ConnectorHealth** - External integrations
- **Media, ContentPage, FaqEntry** - CMS
- **AuditEvent, ConsentEvent** - Compliance

## 🧪 Testing

```bash
# Unit tests
cd apps/web && npm test
cd apps/api && pytest

# Integration tests
cd apps/api && pytest tests/integration/

# E2E tests
cd apps/web && npm run test:e2e
```

## 📦 Deployment

### Vercel (Web)
```bash
cd apps/web
vercel --prod
```

### Railway/Render/Fly.io (API)
```bash
# Build Docker image
docker build -t studio-growth-os-api ./apps/api
# Push to registry and deploy
```

### Database
- Use managed PostgreSQL (Neon, Supabase, RDS, Cloud SQL)
- Run migrations: `npx prisma migrate deploy`

## 🔐 Security

- JWT auth with short expiry + refresh rotation
- RBAC at API + DB level (RLS policies)
- Webhook signature verification (HMAC)
- Idempotency keys on all mutating operations
- Prompt-injection detection on AI agent
- Rate limiting per endpoint
- PII masking in logs

## 📊 Monitoring

- **Health**: `/health` endpoint
- **Metrics**: Prometheus format (webhook age, queue depth, error rates)
- **Logs**: Structured JSON (structlog)
- **Traces**: Agent execution traces in DB
- **Alerts**: Anomaly rules on metrics

## 📁 Project Structure

```
studio-growth-os/
├── apps/
│   ├── web/                      # Next.js 14 App Router
│   │   ├── src/
│   │   │   ├── app/              # Pages (public + admin)
│   │   │   │   ├── admin/        # Dashboard, leads, bookings, quotes, etc.
│   │   │   │   ├── api/          # Next.js API routes (proxied to FastAPI)
│   │   │   │   ├── page.tsx      # Public homepage
│   │   │   │   ├── layout.tsx    # Root layout
│   │   │   │   └── globals.css   # Tailwind + CSS variables
│   │   │   ├── components/       # React components
│   │   │   │   ├── ui/           # shadcn/ui components
│   │   │   │   └── providers.tsx # Session, QueryClient, Theme
│   │   │   ├── lib/              # Utilities (cn, date helpers, etc.)
│   │   │   └── hooks/            # Custom React hooks
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.ts
│   │   └── tsconfig.json
│   │
│   └── api/                      # FastAPI backend
│       ├── main.py               # App entry point + lifespan
│       ├── core/
│       │   ├── config.py         # Pydantic settings
│       │   ├── database.py       # Prisma client
│       │   └── logging.py        # Structlog setup
│       ├── api/v1/
│       │   ├── router.py         # Main router
│       │   └── endpoints/        # All API endpoints
│       │       ├── auth.py
│       │       ├── leads.py
│       │       ├── quotes.py
│       │       ├── bookings.py
│       │       ├── conversations.py
│       │       ├── analytics.py
│       │       ├── webhooks.py
│       │       ├── connectors.py
│       │       ├── agent.py
│       │       ├── payments.py
│       │       ├── media.py
│       │       └── settings.py
│       ├── workers/
│       │   └── main.py           # Background job worker
│       ├── pyproject.toml
│       └── Dockerfile.dev
│
├── packages/
│   └── prisma/
│       ├── schema.prisma         # Complete database schema
│       ├── seed.ts               # Studiox demo data
│       └── package.json
│
├── docker-compose.yml
├── package.json                  # Root workspace (Turbo)
├── .env.example
└── README.md
```

## 🎯 Demo Scenario (8-Step Acceptance)

The seed data (`packages/prisma/seed.ts`) includes a complete demo scenario:

1. **Lead Entry**: Instagram comment-to-DM → deduplicated lead with attribution
2. **Identity Resolution**: Contact matched by phone/email within tenant
3. **AI Qualification**: Conversational agent gathers event details, checks availability
4. **Quote Generation**: Pricing engine produces 2 valid package options (Marriage ₹21,999 / Full Marriage ₹1,25,000)
5. **Slot Hold**: Atomic temporary hold on photographer + videographer (30min TTL)
6. **Payment**: Customer pays ₹1,25,000 via Razorpay UPI → webhook confirms
7. **Booking Confirmed**: Payment → booking state transition, slot holds converted
8. **Attribution**: Multi-touch (first-touch Instagram, last-touch DM) recorded in CRM

## 📋 License

Proprietary - Studio Growth OS v2.0

---

**Built for**: Studiox Photography (Madhu Padishala, Dilsukhnagar, Hyderabad)
**Contact**: support@rungrow.in | +91 72859 88958