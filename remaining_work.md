# 📋 Remaining Work — Job Search AI Agent

Last updated: June 2026

---

## ✅ Completed

Everything below was completed across the project sprints:

### Core AI Layer
- **Unified LLM Provider (`agent/llm_provider.py`)**: 5-provider fallback chain (Groq → OpenRouter → NVIDIA NIM → Gemini → Cohere). Zero cost for dev/demo.
- **Resume Parser (`agent/resume_parser.py`)**: Structured extraction via Pydantic output schemas — pulls contact, education, experience, and skills.
- **ATS Scoring Engine (`agent/ats_scoring.py`)**: Keyword match (0–50), experience relevance (0–30), formatting quality (0–20). Course recommendations for skill gaps.
- **Interview Evaluator (`agent/interview_evaluator.py`)**: STAR methodology compliance grader with ideal answer summary and communication feedback.
- **LangGraph Workflows (`agent/langgraph_workflows/`)**: CareerAdvisor, InterviewAgent, JobSearchAgent, ResumeAgent, and master workflow.

### Backend Microservices
- **Auth Service (:8001)**: JWT register/login + user CRUD + full Applications CRUD API (Firestore-backed Kanban persistence).
- **Jobs Service (:8002)**: Live scrapers for Naukri, Indeed, LinkedIn with Indian-specific filters (LPA, notice period, work mode). 30-min Firestore cache. AI insights: salary benchmarking + company research.
- **Resume Service (:8003)**: Azure Blob upload, PDF/DOCX text extraction, AI parsing, ATS scoring endpoints.
- **Interview Service (:8004)**: AI question generation, answer evaluation, + salary negotiation chatbot (live HR roleplay).
- **Analytics Service (:8005)**: Dashboard endpoint, weekly trends, success/response rate metrics.

### Frontend (Next.js 14)
- **Onboarding flow**: First-visit resume upload gate wired via `localStorage` flag.
- **Dashboard**: Live stats from Analytics Service + recommended job feed from Jobs Service.
- **Jobs Feed**: Search with Indian filters (LPA, notice period, work mode) + AI insights panel.
- **Resume Page**: Upload + AI parse + ATS score with keyword visualization.
- **Kanban Board**: Drag-and-drop application tracker wired to Applications API.
- **Interview Simulator**: Question generation → timed answer → AI evaluation with STAR scoring.
- **Salary Negotiation**: AI HR chatbot in the Interview section.

### Infrastructure
- **Frontend → Backend API wiring**: Next.js API rewrites proxy all `/api/*` calls to the correct microservice.
- **CI Pipeline**: GitHub Actions — Python syntax check for all 5 services + Next.js production build.
- **CD Stub**: `.github/workflows/cd.yml` ready for real deployment tokens.
- **Email Notifications**: Celery `send_notification_task` implemented with real SMTP/SendGrid support.
- **Celery Beat Schedule**: Periodic tasks configured in `celery_config.py` (daily analytics, hourly session cleanup).

---

## 🔴 High Priority — Required for Production / Submission

### 1. Hosting & Cloud Config (Excluded from code sprint but required for marks)

- [ ] **Azure Blob Storage**
  - Create an Azure Storage Account
  - Generate the Connection String
  - Add `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER` to `.env`
  - Verify `backend/resume_file_service.py` connects correctly

- [ ] **Firebase Production Service Account**
  - Create a production Firebase project (separate from dev)
  - Download the service account JSON
  - Set `FIREBASE_CREDENTIALS_PATH` in the deployment environment

- [ ] **Deploy 5 microservices**
  - Choose a platform: Render, Railway, or Azure App Service
  - Deploy each service on the appropriate port with env vars injected
  - Update `frontend/nextjs-app/.env.production` with the live service URLs

- [ ] **Deploy frontend to Vercel**
  - Run `vercel --prod` from `frontend/nextjs-app/`
  - Set `AUTH_SERVICE_URL`, `JOBS_SERVICE_URL` etc. as Vercel env vars
  - Update `.github/workflows/cd.yml` with `VERCEL_TOKEN` secret

- [ ] **Fill in `cd.yml` deployment steps**
  - Replace the `echo "Deployment simulated"` stubs with real Render/Vercel CLI commands
  - Add `VERCEL_TOKEN`, `RENDER_API_KEY`, `RENDER_SERVICE_ID_*` as GitHub repository secrets

### 2. OnboardingPage — Wire to Real Resume Upload API

- [ ] **File:** `frontend/nextjs-app/src/components/OnboardingPage.tsx` — line 67
  - Currently uses `await new Promise((r) => setTimeout(r, 900))` (simulated upload)
  - Replace with actual call:
    ```ts
    import { uploadResume, analyzeResume } from "@/lib/api";
    const { resumeId } = await uploadResume(file);
    await analyzeResume(resumeId);
    localStorage.setItem("resume_id", resumeId);
    onComplete(file.name);
    ```
  - Store `resumeId` in `localStorage` so `ResumePage` can load it without re-upload

### 3. Analytics Dashboard — Scope by User

- [ ] **File:** `backend/analytics_service/routes/analytics.py` — `get_dashboard_stats()`
  - Currently queries ALL applications globally (no user filtering)
  - Add JWT `get_current_user` dependency and filter `applications` by `user_id`
  - This requires the Analytics Service to share the Auth Service JWT secret (via env var)

### 4. DashboardPage — Toast Errors

- [ ] **File:** `frontend/nextjs-app/src/components/DashboardPage.tsx` — line 62
  - `// TODO: toast error` comment when `syncJobSources()` fails
  - Add a simple inline error banner (no library needed — just state + inline style)

---

## 🟡 Medium Priority — Enhancements for Maximum Marks

### 5. Celery Beat — Weekly Job Alert Emails

- [ ] **File:** `celery_config.py`
  - Add a weekly beat schedule entry that calls `send_notification_task` for every user
  - Requires: fetching all user emails from Firestore, building a personalised job match email using the Jobs Service `/recommended` endpoint
  - Example schedule addition:
    ```python
    "weekly-job-alerts": {
        "task": "celery_worker.send_weekly_job_alerts_task",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Every Monday 9 AM
    }
    ```
  - New task `send_weekly_job_alerts_task` to write in `celery_worker.py`

### 6. Career Roadmap Engine — HTTP Endpoint

- [ ] **Context:** `agent/langgraph_workflows/career_advisor.py` exists and has a `CareerAdvisor` class — but there is NO HTTP route exposing it to the frontend.
  - Add a route to the Interview Service (or create a new `/career` prefix route):
    ```
    POST /interview/career/roadmap
    Body: { current_role, target_role, skills, years_experience }
    Returns: { steps: [...], timeline, key_skills_to_learn, resources }
    ```
  - Wire the frontend: add a "Career Roadmap" tab or section to `InterviewPage.tsx`
  - Note: `career_advisor.py` currently uses `langchain_openai.ChatOpenAI` — replace with `get_llm_with_fallback()` from `agent/llm_provider.py` so free providers work

### 7. Aggregate Analytics Task — Real Implementation

- [ ] **File:** `celery_worker.py` — `aggregate_analytics_task()` (line 270)
  - Currently has `# TODO: Implement analytics aggregation logic`
  - Implement: query Firestore `applications` collection, compute daily/weekly counts, write aggregated stats back to a `analytics_cache` Firestore collection
  - The `/analytics/dashboard` endpoint can read from the cache for O(1) response times

### 8. Session Cleanup Task — Real Implementation

- [ ] **File:** `celery_worker.py` — `cleanup_sessions_task()` (line 288)
  - Currently has `# TODO: Implement session cleanup logic`
  - Implement: delete expired JWT sessions / invalidated tokens from Firestore (if a token blacklist is being maintained)
  - If no blacklist is implemented, document that this task is a no-op by design

### 9. Kanban — Native HTML5 Drag-and-Drop

- [ ] **File:** `frontend/nextjs-app/src/components/KanbanPage.tsx`
  - Currently stage changes are done via a `<select>` dropdown on each card — not true drag-and-drop
  - Add `draggable`, `onDragStart`, `onDragOver`, `onDrop` handlers on cards and columns
  - On drop: call `handleStageChange(draggedId, targetStage)` which already calls the API

---

## 🟢 Low Priority / Nice to Have

### 10. Google Calendar Integration

- [ ] Allow users to schedule mock interview sessions into their Google Calendar
  - Use the Google Calendar API with OAuth 2.0
  - Add a "Schedule Practice" button on `InterviewPage.tsx`
  - Create a new route `POST /interview/schedule` that creates a calendar event via the Google Calendar API

### 11. LinkedIn Profile Optimizer

- [ ] Feed parsed resume data → output actionable LinkedIn profile suggestions
  - Add a new LLM prompt in `agent/` that takes `ParsedResume` as input and outputs suggestions for headline, about section, and skills
  - Surface results in `ResumePage.tsx` as a new "LinkedIn Optimizer" tab

### 12. `.env.example` — Add Missing Variables

- [ ] **File:** `.env.example`
  - Missing SMTP variables used by `celery_worker.py`:
    ```
    SMTP_HOST=smtp.sendgrid.net
    SMTP_PORT=587
    SMTP_USER=apikey
    SMTP_PASSWORD=
    FROM_EMAIL=noreply@jobsearchai.app
    ```
  - Missing service URL overrides for production:
    ```
    AUTH_SERVICE_URL=http://localhost:8001
    JOBS_SERVICE_URL=http://localhost:8002
    RESUME_SERVICE_URL=http://localhost:8003
    INTERVIEW_SERVICE_URL=http://localhost:8004
    ANALYTICS_SERVICE_URL=http://localhost:8005
    ```

### 13. Tests Directory — Add Actual Test Files

- [ ] **Directory:** `tests/` — currently only contains `.gitkeep`
  - Write `tests/test_resume_parser.py` — unit test `parse_resume()` with a sample resume string
  - Write `tests/test_ats_scoring.py` — unit test `score_resume_against_jd()` with a sample JD
  - Write `tests/test_applications_api.py` — integration test the Applications CRUD routes
  - Add `pytest` to `requirements.txt` if not already present

### 14. CareerAdvisor — Replace OpenAI with Free LLM Provider

- [ ] **File:** `agent/langgraph_workflows/career_advisor.py` — line 13
  - Currently imports `from langchain_openai import ChatOpenAI` — requires a paid OpenAI key
  - Replace with `from agent.llm_provider import get_llm_with_fallback` to use the free provider chain

---

## 📦 Final Submission Checklist

- [ ] **Wire OnboardingPage to real API** (see item 2 above — highest UX impact)
- [ ] **All 5 services deployed** and accessible via public URLs
- [ ] **Demo video** (8–10 mins showing: onboarding → upload resume → ATS score → jobs feed → Kanban → interview simulator → negotiation chatbot)
- [ ] **Production deployment link** (Vercel URL for the frontend)
- [ ] **API documentation** (FastAPI `/docs` auto-generated — include links to each service in the README)
- [ ] **Git release tag** — run `git tag v1.0 && git push origin v1.0` after final merge
- [ ] **Update `README.md`** with the final deployed URLs replacing `localhost` references
