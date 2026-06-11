# 📋 Remaining Work — Job Search AI Agent

Last updated: June 2026

---

## ✅ Completed

Everything below was completed across the project sprints:

### Core AI Layer
- **Unified LLM Provider (`agent/llm_provider.py`)**: 5-provider fallback chain (Groq → OpenRouter → NVIDIA NIM → Gemini → Cohere). Zero cost for dev/demo.
- **Resume Parser (`agent/resume_parser.py`)**: Structured extraction via Pydantic output schemas — pulls contact, education, experience, and skills.
- **ATS Scoring Engine (`agent/ats_scoring.py`)**: Keyword match (0–50), experience relevance (0–30), formatting quality (0–20). Includes course recommendations for skill gaps.
- **Interview Evaluator (`agent/interview_evaluator.py`)**: STAR methodology compliance grader with ideal answer summary and communication feedback.

### Backend Microservices
- **Auth Service (:8001)**: JWT register/login + user CRUD + full Applications CRUD API (Firestore-backed Kanban persistence).
- **Jobs Service (:8002)**: Live scrapers for Naukri, Indeed, LinkedIn with Indian-specific filters (LPA salary range, notice period, work mode). 30-minute Firestore cache. AI insights: salary benchmarking + company research routes.
- **Resume Service (:8003)**: Azure Blob upload, PyMuPDF/python-docx text extraction, AI parsing, ATS scoring.
- **Interview Service (:8004)**: AI question generation, answer evaluation, + salary negotiation chatbot (live HR roleplay).
- **Analytics Service (:8005)**: Dashboard endpoint, weekly trends, success/response rate metrics.

### Frontend (Next.js 14)
- **Onboarding flow**: First-visit resume upload gate (wired to `localStorage` flag).
- **Dashboard**: Live stats from Analytics Service + recommended job feed from Jobs Service.
- **Jobs Feed**: Search with Indian filters (LPA, notice period, work mode) + AI insights panel (salary + company research).
- **Resume Page**: Upload + AI parse + ATS score analysis with keyword visualization.
- **Kanban Board**: Drag-and-drop application tracker wired to Applications API.
- **Interview Simulator**: Question generation → timed answer → AI evaluation with STAR scoring.
- **Salary Negotiation**: AI HR chatbot in the Interview section.

### Infrastructure
- **Frontend → Backend API wiring**: Next.js API rewrites proxy all `/api/*` calls to the correct microservice (no CORS issues, service URLs not exposed to browser).
- **CI/CD**: GitHub Actions CI (Python syntax check + Next.js build). CD stub ready for Render/Railway.
- **Email Notifications**: Celery task `send_notification_task` implemented with real SMTP/SendGrid support. Gracefully skips when `SMTP_PASSWORD` not set.

---

## ⏳ Pending (Excluded from Scope: Hosting & Azure Credentials)

### 🔴 Required for Production Submission

- [ ] **Azure Blob Storage** — Create Storage Account + generate Connection String → add to `.env`
- [ ] **Firebase Production Service Account** — Generate and add JSON to deployment environment
- [ ] **Deploy 5 microservices** — Render / Railway / Azure App Service
- [ ] **Deploy frontend to Vercel** — Update `.github/workflows/cd.yml` with real deployment tokens
- [ ] **`cd.yml` production secrets** — Add `VERCEL_TOKEN`, `RENDER_API_KEY` etc. as GitHub secrets

### 🟡 Medium Priority (Max Marks)

- [ ] **Career Roadmap Engine** — Generate step-by-step career path from current role → target role (goes beyond single course recommendations)
- [ ] **Job Alert Emails** — Trigger `send_notification_task` weekly with top job matches per user (Celery beat schedule)

### 🟢 Low Priority / Nice to Have

- [ ] **Google Calendar integration** — Allow users to book mock interview sessions into their calendar
- [ ] **LinkedIn Profile Optimizer** — Feed parsed resume data → output actionable LinkedIn profile suggestions
- [ ] **Git release tag** — Run `git tag v1.0` after final merge for submission

---

## 📦 Submission Checklist

- [ ] Demo video (8–10 mins showing full flow: onboarding → jobs → Kanban → resume ATS → interview)
- [ ] Production deployment link (Vercel URL)
- [ ] API documentation (FastAPI `/docs` auto-generated at each service port)
- [ ] Git release tag `v1.0` on final merge
