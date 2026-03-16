# Branch Guide — Job Search AI Agent

---

## 1. What is in Main Branch

Main is a **clean skeleton only** — no logic, no real features.

| Folder/File | What it contains |
|---|---|
| `backend/*/main.py` | 5 FastAPI apps, each with one `GET /` route that returns a status message |
| `frontend/nextjs-app/app/page.tsx` | One line — renders `<h1>Job Search AI Agent</h1>` |
| `agent/resume_parser.py` | Empty — just a comment |
| `agent/ats_scoring.py` | Empty — just a comment |
| `agent/langgraph_workflows/` | Empty folder |
| `database/schema.sql` | 5 tables defined — users, jobs, applications, resumes, interviews |
| `docker-compose.yml` | Wires up postgres, redis, and all 5 services |
| `requirements.txt` | 11 pinned Python dependencies |
| `.env.example` | Env variable template |
| `.gitignore` | Keeps `.env` out of git |
| `README.md` | Project idea, setup steps, architecture overview |

**No business logic. No API integrations. No AI code. No UI components.**

---

## 2. What Features Go in Each Branch

### `feature/langgraph-agent` — Hemanth
- LangGraph multi-agent workflow (Job Search Agent → Resume Agent → Interview Agent → Career Advisor)
- Job matching engine using embeddings/semantic similarity
- Celery tasks for background processing
- `auth_service` — JWT login, registration, password hashing
- `analytics_service` — application stats and metrics endpoints

### `feature/frontend-dashboard` — Rohith
> **Starts in Phase 2** — after Hemanth and Kaisen have published `docs/API_CONTRACTS.md`

- Job search page with filters
- Kanban board for application tracking
- Resume upload UI
- Dark mode toggle
- Routing between pages
- REST API calls to backend services using agreed contracts

### `feature/resume-parser` — Kaisen
- PDF parsing logic in `agent/resume_parser.py`
- ATS scoring logic in `agent/ats_scoring.py`
- NLP pipeline for skill/keyword extraction
- Mock interview session flow in `interview_service`
- Resume scoring against job descriptions

### `feature/job-api-integrations` — Aaryan
> **Starts in Phase 3** — after auth_service and jobs_service endpoints are defined and working

- `naukri_client.py` — real Naukri API integration
- `indeed_client.py` — real Indeed API integration
- LinkedIn scraper/API client
- `jobs_service` endpoints for search, filter, aggregate
- CI/CD pipeline (GitHub Actions)
- Notifications (email/push)

---

## 3. Branch Order

There **is** a required order. The frontend cannot be built without knowing what the backend exposes.

```
Phase 1 — Backend contracts first (Hemanth + Kaisen work in parallel)
├── feature/langgraph-agent       ← defines auth + analytics API routes and schemas
└── feature/resume-parser         ← defines resume + interview API routes and schemas
      │
      └── Before Phase 2: Hemanth + Kaisen add API contracts to docs/API_CONTRACTS.md

Phase 2 — Frontend builds against known contracts (Rohith starts here)
└── feature/frontend-dashboard    ← builds UI using endpoint structure from Phase 1

Phase 3 — Integrations wrap the working system (Aaryan starts here)
└── feature/job-api-integrations  ← plugs real job data into jobs_service + adds CI/CD
```

**Why this order:**
- Rohith needs to know endpoint paths, request shapes, and JWT flow before wiring up `api.ts` and components
- Aaryan needs `auth_service` functional and `jobs_service` endpoints defined before integrating external APIs
- CI/CD should wrap a working system, not a skeleton

**The only hard rule:** everyone branches off `main` — never off someone else's feature branch. That keeps merge conflicts isolated.

---

## 3a. API Contracts Handoff

Before Rohith starts, Hemanth and Kaisen must document their endpoints in `docs/API_CONTRACTS.md`.

Minimum required contracts:

| Method | Endpoint | Request | Response |
|---|---|---|---|
| `POST` | `/auth/register` | `{ email, password }` | `{ user_id }` |
| `POST` | `/auth/login` | `{ email, password }` | `{ access_token }` |
| `GET` | `/jobs/search` | `?title=&location=` | `[ job list ]` |
| `POST` | `/resume/upload` | multipart file | `{ resume_id }` |
| `GET` | `/resume/{id}/score` | — | `{ ats_score }` |
| `GET` | `/interviews/start` | — | `{ session_id }` |
| `GET` | `/applications/` | — | `[ application list ]` |
| `GET` | `/analytics/summary` | — | `{ stats }` |

Rohith builds the frontend against these contracts. Even if the backend isn't fully working yet, the shapes are known — so all UI wiring is correct from the start.

---

## 4. Files Per Branch

---

### `feature/langgraph-agent` — Hemanth

**New files to create:**
```
backend/auth_service/
├── routes/
│   ├── auth.py
│   └── users.py
├── models.py
├── schemas.py
├── dependencies.py
└── Dockerfile

backend/analytics_service/
├── routes/
│   └── analytics.py
├── models.py
└── Dockerfile

agent/langgraph_workflows/
├── job_search_agent.py
├── resume_agent.py
├── interview_agent.py
└── career_advisor.py

celery_worker.py
celery_config.py
```

**Modify existing:**
```
backend/auth_service/main.py        ← add routers
backend/analytics_service/main.py  ← add routers
requirements.txt                    ← add celery, bcrypt, etc.
```

---

### `feature/frontend-dashboard` — Rohith
> **Phase 2 — Do not start until `docs/API_CONTRACTS.md` is published by Hemanth and Kaisen**

**New files to create:**
```
frontend/nextjs-app/
├── app/
│   ├── dashboard/
│   │   └── page.tsx
│   ├── jobs/
│   │   └── page.tsx
│   ├── resume/
│   │   └── page.tsx
│   ├── applications/
│   │   └── page.tsx
│   └── layout.tsx
├── components/
│   ├── Navbar.tsx
│   ├── JobCard.tsx
│   ├── KanbanBoard.tsx
│   └── ResumeUpload.tsx
├── lib/
│   └── api.ts              ← API call helpers
├── styles/
│   └── globals.css
├── package.json
└── tsconfig.json
```

**Modify existing:**
```
frontend/nextjs-app/app/page.tsx    ← update landing page
```

---

### `feature/resume-parser` — Kaisen

**New files to create:**
```
agent/
├── resume_parser.py        ← PDF parsing + NLP logic (replaces placeholder)
├── ats_scoring.py          ← scoring logic (replaces placeholder)
└── utils/
    ├── pdf_extractor.py
    └── keyword_matcher.py

backend/resume_service/
├── routes/
│   └── resume.py
├── models.py
├── schemas.py
└── Dockerfile

backend/interview_service/
├── routes/
│   └── interview.py
├── models.py
├── schemas.py
└── Dockerfile
```

**Modify existing:**
```
backend/resume_service/main.py      ← add routers
backend/interview_service/main.py   ← add routers
requirements.txt                    ← add pdfplumber, spacy, etc.
```

---

### `feature/job-api-integrations` — Aaryan
> **Phase 3 — Do not start until auth_service and jobs_service endpoints are merged to main**

**New files to create:**
```
backend/jobs_service/
├── api_clients/
│   ├── naukri_client.py    ← real integration (replaces placeholder)
│   ├── indeed_client.py    ← real integration (replaces placeholder)
│   └── linkedin_client.py
├── routes/
│   └── jobs.py
├── models.py
├── schemas.py
└── Dockerfile

.github/
└── workflows/
    ├── ci.yml
    └── cd.yml

notifications/
├── email_service.py
└── push_service.py
```

**Modify existing:**
```
backend/jobs_service/main.py        ← add routers
docker-compose.yml                  ← add build contexts if needed
.env.example                        ← add any new API keys
requirements.txt                    ← add httpx, sendgrid, etc.
```

---

## 5. Ownership Summary

| File/Folder | Hemanth | Rohith | Kaisen | Aaryan |
|---|:---:|:---:|:---:|:---:|
| `backend/auth_service/` | **owns** | | | |
| `backend/analytics_service/` | **owns** | | | |
| `backend/resume_service/` | | | **owns** | |
| `backend/interview_service/` | | | **owns** | |
| `backend/jobs_service/` | | | | **owns** |
| `agent/langgraph_workflows/` | **owns** | | | |
| `agent/resume_parser.py` | | | **owns** | |
| `agent/ats_scoring.py` | | | **owns** | |
| `frontend/` | | **owns** | | |
| `.github/workflows/` | | | | **owns** |

No two members own the same folder — merge conflicts are minimal by design.
