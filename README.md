# Job Search AI Agent

## Project Idea

The Job Search AI Agent is an AI-powered platform that streamlines the entire job search process for candidates. It combines intelligent automation with multi-source job aggregation to give users a competitive edge.

**Core capabilities:**
- **AI-powered job matching** — Matches user profiles and resumes to relevant job listings using semantic similarity and skill gap analysis
- **Resume analysis** — Parses uploaded resumes to extract skills, experience, and keywords
- **ATS scoring** — Scores resumes against specific job descriptions to maximize applicant tracking system pass rates
- **Mock interview practice** — AI-driven interview simulation with feedback on answers
- **Application tracking** — Kanban-style board to track application statuses across all jobs
- **Multi-source job aggregation** — Pulls listings from Naukri, Indeed, LinkedIn, and other platforms into a single unified feed

---

## Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd job-search-ai-agent
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in real values for `DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `NAUKRI_API_KEY`, and `JWT_SECRET`.

3. **Start all services with Docker**
   ```bash
   docker-compose up
   ```
   This starts PostgreSQL, Redis, and all 5 FastAPI backend services.

4. **Run the frontend**
   ```bash
   cd frontend/nextjs-app
   npm install
   npm run dev
   ```

5. **Access the app**
   Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Architecture

### Microservices — 5 FastAPI Services

| Service | Port | Responsibility |
|---|---|---|
| `auth_service` | 8001 | User registration, login, JWT authentication |
| `jobs_service` | 8002 | Job aggregation, search, and filtering |
| `resume_service` | 8003 | Resume upload, parsing, and storage |
| `interview_service` | 8004 | Mock interview sessions and feedback |
| `analytics_service` | 8005 | Application stats, metrics, and insights |

Each service is independently deployable and communicates via REST APIs.

### LangGraph Agent Workflow

```
Job Search Agent
      │
      ▼
Resume Agent  ──→  ATS Scoring
      │
      ▼
Interview Agent
      │
      ▼
Career Advisor
```

The multi-agent pipeline is orchestrated with LangGraph, enabling stateful, multi-step AI workflows across agent nodes.

### Database

- **PostgreSQL** — Primary relational database storing users, jobs, applications, resumes, and interviews
- **Redis** — Caching layer for session tokens, job search results, and rate limiting

### Frontend

- **Next.js** (TypeScript) communicates with backend microservices via REST APIs
- Server-side rendering for fast initial page loads
- Connects to the API gateway or individual services depending on the feature
