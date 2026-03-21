# Contribution Guide for Aaryan

## Job API Integrations Developer

**Branch:** `feature/job-api-integrations`
**Phase:** 3 (Start after auth_service is working)
**Owner of:** `backend/jobs_service/`, `.github/workflows/`, `notifications/`

---

## 1. Overview

You are responsible for integrating external job APIs (Naukri, Indeed, LinkedIn) and building the jobs_service backend. You'll also set up CI/CD pipelines and notification services.

**Your responsibilities:**
- Naukri API integration
- Indeed API integration
- LinkedIn API/scraper
- `jobs_service` endpoints for search, filter, aggregate
- CI/CD pipeline (GitHub Actions)
- Notifications (email/push)

---

## 2. Current Backend Status (What Hemanth Has Built)

Before you start, understand what's already in place:

### Database Architecture

Hemanth has migrated the project to:
- **Firestore** - NoSQL database for all data (users, jobs, applications)
- **Azure Blob Storage** - For file storage (resumes)

**Important:** User IDs and other IDs are **strings**, not integers.

### Authentication System (Port 8001)

Hemanth has built a complete JWT-based authentication system:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | Returns JWT token |
| `GET` | `/users/me` | Get current user (needs Bearer token) |

### How Authentication Works

1. User logs in via `/auth/login`
2. Backend returns JWT token: `{ "access_token": "eyJ...", "token_type": "bearer" }`
3. All subsequent requests include header: `Authorization: Bearer <token>`
4. Token contains user_id which identifies the user

---

## 3. How to Set Up Your Development Environment

### Step 1: Clone and Create Your Branch

```bash
git clone <repo-url>
cd job-search-ai-agent
git checkout main
git pull origin main
git checkout -b feature/job-api-integrations
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get API Keys

You'll need to obtain API keys for:
- **Naukri API** - Contact Naukri developer portal
- **Indeed API** - Apply at Indeed Publisher Program
- **LinkedIn API** - LinkedIn Developer Portal (or use scraping approach)

### Step 4: Environment Setup

Add your API keys to `.env`:

```env
# Job API Keys (add these)
NAUKRI_API_KEY=your-naukri-api-key
INDEED_API_KEY=your-indeed-api-key
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Email Notifications
SENDGRID_API_KEY=your-sendgrid-api-key
NOTIFICATION_EMAIL_FROM=noreply@yourapp.com
```

---

## 4. Files You Should Create

### Directory Structure

```
backend/jobs_service/
├── main.py                    # FastAPI app (modify existing)
├── routes/
│   └── jobs.py                # Job search endpoints
├── api_clients/
│   ├── __init__.py
│   ├── naukri_client.py       # Naukri API integration
│   ├── indeed_client.py       # Indeed API integration
│   └── linkedin_client.py     # LinkedIn integration
├── schemas.py                 # Pydantic models
├── dependencies.py            # Firestore helpers
└── Dockerfile

.github/
└── workflows/
    ├── ci.yml                 # Run tests on PR
    └── cd.yml                 # Deploy on merge to main

notifications/
├── __init__.py
├── email_service.py           # SendGrid email notifications
└── push_service.py            # Push notifications (optional)
```

---

## 5. Jobs Service Implementation

### schemas.py - Data Models

```python
# backend/jobs_service/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None  # full-time, part-time, contract
    experience_level: Optional[str] = None  # entry, mid, senior
    source: str  # naukri, indeed, linkedin

class JobCreate(JobBase):
    external_id: str  # ID from the source API

class JobResponse(JobBase):
    id: str
    external_id: str
    posted_at: datetime
    created_at: datetime

class JobSearchParams(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    page: int = 1
    limit: int = 20

class JobSearchResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    pages: int
```

### dependencies.py - Firestore Helpers

```python
# backend/jobs_service/dependencies.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Optional, Dict, Any, List

def get_db():
    """Get Firestore client."""
    return get_firestore_client()

def create_job(db, job_data: Dict[str, Any]) -> str:
    """Create a new job in Firestore."""
    from google.cloud import firestore

    job_data['created_at'] = firestore.SERVER_TIMESTAMP
    doc_ref = db.collection('jobs').document()
    doc_ref.set(job_data)
    return doc_ref.id

def get_job_by_external_id(db, source: str, external_id: str) -> Optional[Dict]:
    """Check if job already exists (to avoid duplicates)."""
    jobs_ref = db.collection('jobs')
    query = jobs_ref.where(filter=FieldFilter('source', '==', source))\
                   .where(filter=FieldFilter('external_id', '==', external_id))\
                   .limit(1)

    docs = list(query.stream())
    if docs:
        job = docs[0].to_dict()
        job['id'] = docs[0].id
        return job
    return None

def search_jobs(
    db,
    title: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """Search jobs with filters."""
    jobs_ref = db.collection('jobs')
    query = jobs_ref

    # Note: Firestore has limited query capabilities
    # For complex text search, consider using Algolia or Elasticsearch
    if location:
        query = query.where(filter=FieldFilter('location', '==', location))

    query = query.order_by('created_at', direction='DESCENDING')\
                .limit(limit)\
                .offset(offset)

    jobs = []
    for doc in query.stream():
        job = doc.to_dict()
        job['id'] = doc.id
        jobs.append(job)

    return jobs
```

### routes/jobs.py - API Endpoints

```python
# backend/jobs_service/routes/jobs.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ..schemas import JobSearchParams, JobSearchResponse, JobResponse
from ..dependencies import get_db, search_jobs
from ..api_clients import naukri_client, indeed_client

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/search", response_model=JobSearchResponse)
async def search_jobs_endpoint(
    title: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search jobs from all sources.
    """
    db = get_db()
    offset = (page - 1) * limit

    jobs = search_jobs(
        db,
        title=title,
        location=location,
        limit=limit,
        offset=offset
    )

    return JobSearchResponse(
        jobs=jobs,
        total=len(jobs),  # TODO: Get actual count
        page=page,
        pages=1  # TODO: Calculate pages
    )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get a specific job by ID."""
    db = get_db()
    doc = db.collection('jobs').document(job_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")

    job = doc.to_dict()
    job['id'] = doc.id
    return job

@router.post("/fetch-external")
async def fetch_external_jobs(
    source: str = Query(..., regex="^(naukri|indeed|linkedin)$"),
    title: Optional[str] = Query(None),
    location: Optional[str] = Query(None)
):
    """
    Fetch jobs from external API and store in Firestore.
    This should be called by a background task (Celery).
    """
    db = get_db()

    if source == "naukri":
        jobs = await naukri_client.search_jobs(title=title, location=location)
    elif source == "indeed":
        jobs = await indeed_client.search_jobs(title=title, location=location)
    else:
        raise HTTPException(status_code=400, detail=f"Source {source} not implemented")

    # Store jobs in Firestore
    stored = 0
    for job in jobs:
        # Check if already exists
        existing = get_job_by_external_id(db, source, job['external_id'])
        if not existing:
            create_job(db, job)
            stored += 1

    return {"message": f"Fetched {len(jobs)} jobs, stored {stored} new jobs"}
```

### api_clients/naukri_client.py - Example API Client

```python
# backend/jobs_service/api_clients/naukri_client.py
import os
import httpx
from typing import Optional, List, Dict
from datetime import datetime

NAUKRI_API_KEY = os.getenv("NAUKRI_API_KEY")
NAUKRI_BASE_URL = "https://api.naukri.com/v1"  # Example URL

async def search_jobs(
    title: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    Search jobs from Naukri API.

    NOTE: Replace this with actual Naukri API implementation.
    The structure below is an example.
    """
    if not NAUKRI_API_KEY:
        print("[WARN] NAUKRI_API_KEY not set, returning empty results")
        return []

    params = {
        "keyword": title,
        "location": location,
        "limit": limit
    }

    headers = {
        "Authorization": f"Bearer {NAUKRI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NAUKRI_BASE_URL}/jobs/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        # Transform to our schema
        jobs = []
        for item in data.get("jobs", []):
            jobs.append({
                "external_id": item["id"],
                "title": item["title"],
                "company": item["company"]["name"],
                "location": item["location"],
                "description": item["description"],
                "salary_min": item.get("salary", {}).get("min"),
                "salary_max": item.get("salary", {}).get("max"),
                "job_type": item.get("type"),
                "experience_level": item.get("experience"),
                "source": "naukri",
                "posted_at": datetime.fromisoformat(item["posted_date"])
            })

        return jobs

    except Exception as e:
        print(f"[ERROR] Naukri API error: {e}")
        return []
```

---

## 6. CI/CD Pipeline

### .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [main, feature/*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run tests
        run: |
          pytest tests/ -v
        env:
          # Use test/mock credentials
          FIREBASE_CREDENTIALS_PATH: tests/mock-credentials.json

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install linters
        run: |
          pip install flake8 black isort

      - name: Run flake8
        run: flake8 backend/ agent/ --max-line-length=100

      - name: Check formatting with black
        run: black --check backend/ agent/
```

### .github/workflows/cd.yml

```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker images
        run: |
          docker-compose build

      # Add deployment steps based on your hosting platform
      # Example for Azure Container Apps, AWS ECS, or Google Cloud Run
```

---

## 7. Integration with Auth Service

When users apply for jobs, you need to verify their authentication:

```python
# backend/jobs_service/dependencies.py (add this)
from fastapi import Header, HTTPException
import httpx

AUTH_SERVICE_URL = "http://localhost:8001"

async def get_current_user(authorization: str = Header(...)):
    """Verify user token with auth service."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    return response.json()
```

Use in endpoints:

```python
@router.post("/applications")
async def apply_to_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Apply to a job - requires authentication."""
    user_id = current_user["id"]
    # Create application in Firestore
    ...
```

---

## 8. Important Notes - Avoid Conflicts

### DO NOT Modify These Files

These files belong to other team members:
- `backend/auth_service/*` - Hemanth
- `backend/analytics_service/*` - Hemanth
- `backend/resume_service/*` - Kaisen
- `backend/interview_service/*` - Kaisen
- `frontend/*` - Rohith
- `agent/resume_parser.py` - Kaisen
- `agent/ats_scoring.py` - Kaisen
- `config.py` - Hemanth (but you can import from it)

### Files You Own

- `backend/jobs_service/*`
- `.github/workflows/*`
- `notifications/*`

### Shared Files (Coordinate Before Editing)

- `requirements.txt` - Add your deps at the end, don't modify existing
- `.env.example` - Add your env vars at the end
- `docker-compose.yml` - Add jobs_service section only

---

## 9. Firestore Collection for Jobs

Store jobs in the `jobs` collection:

```
jobs/
  {job_id}/
    - external_id: string (ID from source API)
    - title: string
    - company: string
    - location: string
    - description: string
    - salary_min: number (optional)
    - salary_max: number (optional)
    - job_type: string
    - experience_level: string
    - source: string (naukri, indeed, linkedin)
    - posted_at: timestamp
    - created_at: timestamp
```

---

## 10. Testing Your Code

### Run Jobs Service

```bash
cd job-search-ai-agent
python -m uvicorn backend.jobs_service.main:app --port 8002 --reload
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8002/health

# Search jobs
curl "http://localhost:8002/jobs/search?title=python&location=bangalore"

# Get specific job
curl http://localhost:8002/jobs/{job_id}
```

---

## 11. Git Workflow

### Before Starting Work

```bash
git checkout feature/job-api-integrations
git pull origin main
```

### Commits

```bash
git add .
git commit -m "Add Naukri API client"
git push origin feature/job-api-integrations
```

---

## 12. Questions?

- **Auth questions?** - Ask Hemanth
- **Frontend integration?** - Ask Rohith
- **Resume/Interview endpoints?** - Ask Kaisen

---

**Start Date:** After auth_service is working (Phase 3)
**Branch:** `feature/job-api-integrations`
**Your Focus:** Job APIs, CI/CD, notifications

Good luck!
