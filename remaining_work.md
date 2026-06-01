# 📋 Remaining Work — Job Search AI Agent

This document tracks all the pending tasks required to complete the **Job Search AI Agent (Track B - Advanced)** project for the final submission. It has been updated to reflect the work completed so far (such as the frontend API wiring, AI mock interview answer evaluator, and the 5-provider fallback system).

---

## 🛠️ Completed in the Latest Sprint
- **Unified LLM Provider (`agent/llm_provider.py`)**: Built a 5-provider fallback chain (Groq LLaMA 3.3 70B → OpenRouter Gemini Free → NVIDIA NIM LLaMA 3.3 → Gemini 2.0 Flash → Cohere Command-R) ensuring the system always runs on free-tier models without failure.
- **Mock Interview Evaluator (`agent/interview_evaluator.py`)**: Implemented answer evaluation using STAR methodology compliance and sentiment analysis.
- **Frontend API Wiring (`frontend/nextjs-app/src/lib/api.ts`)**: Replaced all mock/stub data with real backend `fetch` requests, complete with automatic JWT token injection.
- **Resume & Interview Integration**: Fully wired the frontend Resume Page and Mock Interview Simulator page to the live backend services (`POST /resumes/{id}/analyze`, `POST /resumes/{id}/score`, and `POST /interview/evaluate`).
- **Next.js Proxy Rewrites (`next.config.ts`)**: Configured proxy rewrites to bypass CORS and route all frontend requests clean to the 5 backend microservices.

---

## 🔴 High Priority — Core Requirements (Next Sprint)

### 1. Job Scrapers & Indian Platforms Integration
The project brief requires integration with active Indian job boards and location/salary filters.
- [ ] **Naukri.com Scraper Client** (`backend/jobs_service/api_clients/naukri.py`)
  - *Owner:* **Aaryan**
  - Implement a web scraper or search client matching Indian job listings.
- [ ] **Indeed India Scraper Client** (`backend/jobs_service/api_clients/indeed.py`)
  - *Owner:* **Aaryan**
  - Implement Indeed search client.
- [ ] **LinkedIn Jobs Scraper Client** (`backend/jobs_service/api_clients/linkedin.py`)
  - *Owner:* **Aaryan**
  - Extract basic details from public listings or a mock scraper payload.
- [ ] **Indian-Specific Filters**
  - *Owner:* **Aaryan / Rohith**
  - Support filters: CTC/Salary in LPA (Lakhs Per Annum), Notice Period (e.g., Immediate, 15 days, 30 days, 90 days), Metro/Tier-2 locations, Work from Home (WFH) / Hybrid / On-site.
- [ ] **Firestore Caching**
  - *Owner:* **Hemanth / Aaryan**
  - Cache results in Firestore so duplicate queries do not trigger repeated scraping calls.

### 2. CI/CD Pipeline
- [ ] **Automated Testing & Build Pipeline** (`.github/workflows/ci.yml`)
  - *Owner:* **Aaryan / Hemanth**
  - Run pytest for microservices and build the Next.js app on every Pull Request or push.
- [ ] **Deployment Workflow** (`.github/workflows/cd.yml`)
  - *Owner:* **Aaryan / Hemanth**
  - Automated deployment of services to a cloud provider (e.g., Azure or Render) on merging to `master`.

### 3. Production Deployment & Orchestration
- [ ] **Production-Ready Docker Compose**
  - *Owner:* **Hemanth**
  - Optimize `docker-compose.yml` for production, ensuring environment variables are securely injected and Redis/Celery scales properly.
- [ ] **Host Configuration**
  - *Owner:* **Hemanth**
  - Deploy the 5 microservices + Next.js frontend to a cloud platform, setting up correct domain/subdomain routing.

---

## 🟡 Medium Priority — Enhancements for Maximum Marks

### 4. Salary Benchmarking & Negotiation
- [ ] **LPA Salary Benchmarking Service**
  - *Owner:* **Kaisen / Hemanth**
  - Extract salary insights for specific roles, tech stacks, and locations in India (LPA format).
- [ ] **Salary Negotiation AI Chatbot**
  - *Owner:* **Kaisen**
  - Interactive LLM-powered chat interface to help candidates negotiate offers.

### 5. Company Research Tool
- [ ] **Company Profile lookup**
  - *Owner:* **Kaisen**
  - LLM-powered summary engine that aggregates company culture, standard interview rounds, ratings, and common questions.

### 6. Career Path & Skills Gap Course Recommendations
- [ ] **Career Roadmap Engine**
  - *Owner:* **Kaisen**
  - Generate step-by-step career path roadmaps based on current vs target job profiles.
- [ ] **Course Recommendations**
  - *Owner:* **Kaisen**
  - Map missing skills (from ATS report) to recommended Coursera, Udemy, or Youtube learning resources.

### 7. Job Alert Notification System
- [ ] **Email Alerts**
  - *Owner:* **Aaryan**
  - Integrate SendGrid or standard SMTP setup in the Celery task runner to email matching jobs to the user weekly or daily.

---

## 🟢 Low Priority & Polish

### 8. Calendar Integration
- [ ] **Interview Scheduling**
  - *Owner:* **Rohith / Hemanth**
  - Allow users to link their Google Calendar or Outlook Calendar to book/log mock interview schedules.

### 9. LinkedIn Profile Optimizer
- [ ] **Profile Review Engine**
  - *Owner:* **Kaisen**
  - Feed resume data and output actionable suggestions to optimize the candidate's LinkedIn profile.

---

## 📦 Project Submission Checklist
- [ ] **Demo Video** (8-10 mins duration showing full flow)
- [ ] **Production deployment link**
- [ ] **API Documentation** (Fully documented FastAPI endpoints)
- [ ] **Git release tag** (`git tag v1.0` on final merge)
