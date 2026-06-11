# Job Search AI Agent — Complete Project Documentation

> **Version:** 2.0.0  
> **Stack:** Next.js 14 · FastAPI (×5 microservices) · LangGraph · Firestore · Azure Blob Storage

---

## 🚀 What Is This?

A full-stack, AI-powered job search platform designed for the Indian market. Upload your resume once and the platform handles the rest:

- **AI Resume Parsing** — extracts skills, experience, and education from any PDF/DOCX
- **ATS Scoring** — scores your resume against any job description with a detailed keyword gap report
- **Job Aggregation** — scrapes Naukri, LinkedIn, and Indeed with Indian-specific filters (LPA, notice period, work mode)
- **Kanban Application Tracker** — drag-and-drop board to manage every stage of your job hunt
- **AI Interview Simulator** — generates role-specific questions + evaluates your answers with STAR scoring
- **Salary Negotiation Chatbot** — live AI HR roleplay to practice negotiation
- **AI Market Insights** — salary benchmarking by role/city and company culture deep-dives

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Next.js Frontend                           │
│  ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐  │
│  │Dashboard │ │JobFeed │ │Resume  │ │ Kanban   │ │  Interview  │  │
│  └────┬─────┘ └───┬────┘ └───┬────┘ └────┬─────┘ └──────┬──────┘  │
│       └────────────┴──────────┴───────────┴──────────────┘         │
│                         /api/* (Next.js rewrites)                   │
└─────────────────────────────────────────────────────────────────────┘
              │          │          │          │          │
         :8001       :8002      :8003      :8004      :8005
              │          │          │          │          │
┌─────────────┴──┐  ┌────┴───┐  ┌──┴────┐  ┌──┴─────┐  ┌──┴──────────┐
│  Auth Service  │  │  Jobs  │  │Resume │  │Interview│  │  Analytics  │
│  JWT + Apps   │  │Scrapers│  │Azure/ │  │Generate │  │  Dashboard  │
│  Firestore    │  │Cache   │  │AI Parse│  │Evaluate │  │  Firestore  │
└───────────────┘  └────────┘  └───────┘  └─────────┘  └─────────────┘
                         │          │
                    ┌────┴──────────┴────┐
                    │      AI Layer      │
                    │ agent/llm_provider │
                    │ Groq→OpenRouter→   │
                    │ NVIDIA NIM→Gemini  │
                    │      →Cohere       │
                    └────────────────────┘
```

### Service Port Map

| Service | Port | Responsibility |
|---|---|---|
| Auth Service | 8001 | JWT auth + user profiles + **Application CRUD** |
| Jobs Service | 8002 | Job scraping (Naukri/Indeed/LinkedIn) + Firestore cache + AI insights |
| Resume Service | 8003 | Azure Blob upload + PDF extraction + AI parsing + ATS scoring |
| Interview Service | 8004 | AI question generation + answer evaluation + salary negotiation chat |
| Analytics Service | 8005 | Dashboard stats + weekly trends + success/response rates |

---

## 📁 Directory Structure

```
job-search-ai-agent/
├── agent/                      # AI core — LangChain/LangGraph agents
│   ├── llm_provider.py         # 5-provider fallback chain (Groq→Gemini→Cohere…)
│   ├── resume_parser.py        # Structured resume extraction (Pydantic output)
│   ├── ats_scoring.py          # ATS keyword match + formatting scorer
│   ├── interview_evaluator.py  # STAR compliance + answer grader
│   └── langgraph_workflows/    # LangGraph state machine definitions
│
├── backend/
│   ├── auth_service/           # :8001 — JWT auth + user CRUD + applications API
│   │   └── routes/
│   │       ├── auth.py         # POST /auth/register, /auth/login
│   │       ├── users.py        # GET/PUT /users/me
│   │       └── applications.py # CRUD /applications — Kanban Firestore persistence ✨NEW
│   ├── jobs_service/           # :8002 — job scraping + Firestore cache
│   │   ├── main.py             # GET /jobs/search, /recommended, POST /jobs/sync
│   │   ├── insights_routes.py  # GET /jobs/insights/salary, /company
│   │   └── api_clients/        # Naukri / Indeed / LinkedIn scrapers
│   ├── resume_service/         # :8003 — resume storage & AI analysis
│   │   └── resume_routes.py    # Upload, parse, ATS score endpoints
│   ├── interview_service/      # :8004 — mock interview AI
│   │   ├── main.py             # Generate questions + evaluate answers
│   │   └── negotiation_routes.py # Salary negotiation chatbot
│   └── analytics_service/      # :8005 — metrics & dashboard
│       └── routes/analytics.py # GET /analytics/dashboard ✨NEW + summary, trends
│
├── frontend/nextjs-app/
│   ├── src/app/page.tsx        # App shell — OnboardingPage gate ✨WIRED
│   ├── src/components/
│   │   ├── OnboardingPage.tsx  # First-visit resume upload flow
│   │   ├── DashboardPage.tsx   # Stats + recommended job feed
│   │   ├── JobsFeedPage.tsx    # Search + filter + AI insights panel
│   │   ├── ResumePage.tsx      # Upload + ATS analysis UI
│   │   ├── KanbanPage.tsx      # Drag-and-drop application tracker
│   │   ├── InterviewPage.tsx   # Question generation + answer evaluation
│   │   └── Sidebar.tsx         # Navigation shell
│   ├── src/lib/api.ts          # Typed API client for all 5 services
│   ├── src/lib/types.ts        # Shared TypeScript interfaces
│   └── next.config.ts          # API rewrites → microservices
│
├── celery_worker.py            # Background tasks (email alerts ✨REAL SMTP, job sync)
├── celery_config.py            # Redis broker configuration
├── config.py                   # Firestore + Azure Blob init
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Local dev orchestration
└── .github/workflows/
    ├── ci.yml                  # Python syntax check + Next.js build
    └── cd.yml                  # Deployment stub (customize for your platform)
```

---

## ⚡ Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Redis (for Celery)
- Firebase service account JSON
- Groq API key (free at console.groq.com)

### 1. Clone & Install

```bash
git clone <your-repo>
cd job-search-ai-agent

# Python deps
pip install -r requirements.txt

# Frontend deps
cd frontend/nextjs-app && npm install
```

### 2. Configure Environment

Copy `.env.example` → `.env` and fill in the keys:

```env
# Required — at least one LLM key
GROQ_API_KEY=gsk_...

# Firebase (resume metadata, job cache, applications)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Azure (resume PDF/DOCX storage)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...

# Email notifications (optional — SMTP or SendGrid)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxx
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Start All Services

```bash
# Terminal 1 — Auth Service (port 8001)
uvicorn backend.auth_service.main:app --port 8001 --reload

# Terminal 2 — Jobs Service (port 8002)
uvicorn backend.jobs_service.main:app --port 8002 --reload

# Terminal 3 — Resume Service (port 8003)
uvicorn backend.resume_service.main:app --port 8003 --reload

# Terminal 4 — Interview Service (port 8004)
uvicorn backend.interview_service.main:app --port 8004 --reload

# Terminal 5 — Analytics Service (port 8005)
uvicorn backend.analytics_service.main:app --port 8005 --reload

# Terminal 6 — Next.js frontend (port 3000)
cd frontend/nextjs-app && npm run dev

# Terminal 7 — Celery worker (optional, for email alerts)
celery -A celery_worker worker --loglevel=info
```

Then open **http://localhost:3000** — you'll be greeted by the onboarding resume upload screen.

---

## 🤖 AI Features in Detail

### LLM Provider Fallback Chain (`agent/llm_provider.py`)

Automatically tries 5 free providers in order — if one is rate-limited, it falls back:
```
Groq (LLaMA 3.3 70B)
  ↓ fallback
OpenRouter (free tier)
  ↓ fallback
NVIDIA NIM (LLaMA 3.1 70B)
  ↓ fallback
Gemini (gemini-pro)
  ↓ fallback
Cohere (command-r)
```

### Resume ATS Scoring (`agent/ats_scoring.py`)

- **Keyword Match** (0–50 pts): detects exact and semantic keyword matches against the JD
- **Experience Relevance** (0–30 pts): evaluates how well past roles align with the JD
- **Formatting Quality** (0–20 pts): checks sections, action verbs, quantified achievements
- **Course Recommendations**: maps missing keywords to Coursera/YouTube search terms

### Interview Evaluator (`agent/interview_evaluator.py`)

- **STAR Compliance**: S/T/A/R components graded individually (0–25 pts each)
- **Communication Score**: clarity, structure, confidence
- **Verdict**: Excellent / Good / Average / Needs Improvement
- **Ideal Answer**: generates what the perfect answer would look like

---

## 📡 API Quick Reference

### Auth Service (:8001)
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login → returns JWT |
| GET | `/users/me` | Current user profile |
| GET | `/applications/` | List all applications |
| POST | `/applications/` | Create application |
| PATCH | `/applications/{id}/stage` | Move Kanban stage |
| DELETE | `/applications/{id}` | Delete application |

### Jobs Service (:8002)
| Method | Path | Description |
|---|---|---|
| GET | `/jobs/search` | Search across Naukri/Indeed/LinkedIn |
| GET | `/jobs/recommended` | Personalized recommendations |
| POST | `/jobs/sync` | Force-refresh job cache |
| GET | `/jobs/insights/salary` | AI salary benchmarking |
| GET | `/jobs/insights/company` | AI company research |

### Resume Service (:8003)
| Method | Path | Description |
|---|---|---|
| POST | `/resumes/upload` | Upload PDF/DOCX → Azure Blob |
| GET | `/resumes/{id}` | Fetch parsed resume data |
| POST | `/resumes/{id}/analyze` | Run AI resume parsing |
| POST | `/resumes/{id}/score` | Run ATS scoring vs JD |
| GET | `/resumes/{id}/download` | Download original file |
| DELETE | `/resumes/{id}` | Delete resume |

### Interview Service (:8004)
| Method | Path | Description |
|---|---|---|
| POST | `/interview/generate` | Generate tailored questions |
| POST | `/interview/evaluate` | Evaluate candidate answer |
| GET | `/interview/categories` | List question categories |
| POST | `/interview/negotiation/chat` | Salary negotiation chatbot |

### Analytics Service (:8005)
| Method | Path | Description |
|---|---|---|
| GET | `/analytics/dashboard` | Dashboard stats (total apps, interviews, ATS avg, offer rate) |
| GET | `/analytics/summary` | Full analytics summary |
| GET | `/analytics/trends/weekly` | Weekly application trends |
| GET | `/analytics/metrics/success-rate` | Success rate metric |

---

## 📧 Email Notifications (Celery)

Set `SMTP_PASSWORD` in `.env` to enable. Uses standard SMTP or SendGrid:

```python
from celery_worker import send_notification_task

send_notification_task.delay(
    user_id="user123",
    notification_type="job_alert",
    content={
        "to_email": "candidate@gmail.com",
        "subject": "5 new Python jobs in Bangalore",
        "body": "Here are this week's top matches for your profile...",
        "body_html": "<h2>Top Jobs for You</h2>...",
    }
)
```

---

## 🧪 Testing

```bash
# Python syntax check (all 5 services)
python -m py_compile backend/auth_service/main.py
python -m py_compile backend/jobs_service/main.py
python -m py_compile backend/resume_service/main.py
python -m py_compile backend/interview_service/main.py
python -m py_compile backend/analytics_service/main.py

# Component tests
python test_components.py

# Service integration tests
bash test_services.sh

# Frontend build
cd frontend/nextjs-app && npm run build
```

---

## 🔒 Credentials & Security

See `CREDENTIALS_SETUP.md` for the full setup guide.  
See `docs/FIRESTORE_AZURE_MIGRATION.md` for the database migration guide.  
See `docs/TESTING_GUIDE.md` for detailed testing procedures.

---

## 📈 Remaining / Future Work

| Priority | Feature | Status |
|---|---|---|
| ✅ Done | Onboarding flow with resume upload | Complete |
| ✅ Done | AI resume parsing + ATS scoring | Complete |
| ✅ Done | Job scrapers (Naukri/Indeed/LinkedIn) | Complete |
| ✅ Done | Kanban application tracker | Complete |
| ✅ Done | AI interview simulator + STAR grading | Complete |
| ✅ Done | Salary negotiation chatbot | Complete |
| ✅ Done | AI market insights (salary + company) | Complete |
| ✅ Done | Applications CRUD API | Complete |
| ✅ Done | Analytics dashboard endpoint | Complete |
| ✅ Done | Email notifications via SMTP/SendGrid | Complete |
| ⏳ Hosting | Deploy 5 microservices + Vercel frontend | Pending credentials |
| 🟡 Medium | Career roadmap engine | Future sprint |
| 🟢 Low | Google Calendar integration | Future sprint |
| 🟢 Low | LinkedIn profile optimizer | Future sprint |
