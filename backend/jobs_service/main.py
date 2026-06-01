"""
Jobs Service — FastAPI Router
================================
Exposes the following endpoints on Port 8002:

  GET  /jobs/search          — Search across all connected job sources
  GET  /jobs/recommended     — Recommended jobs based on user's resume profile
  POST /jobs/sync            — Trigger a fresh scrape + Firestore cache update
  GET  /jobs/health          — Health check

Firestore Caching Strategy:
  - Search results are cached in Firestore under `job_cache/{cache_key}`.
  - Cache TTL is 30 minutes. If a cached result exists and is fresh, the
    scrapers are NOT called — results return instantly.
  - POST /jobs/sync bypasses the cache and forces a fresh scrape, then
    re-populates the cache.

Indian-specific Filters (query params):
  - location        City name or region (e.g., "Bangalore", "Remote")
  - min_salary_lpa  Minimum salary in Lakhs Per Annum (e.g., 8.0)
  - max_salary_lpa  Maximum salary in LPA
  - work_mode       "remote" | "hybrid" | "onsite" | "any"
  - notice_period   "immediate" | "15days" | "30days" | "60days" | "90days" | "any"
"""

import asyncio
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from .api_clients.base import JobSearchParams
from .api_clients.naukri_client import NaukriClient
from .api_clients.indeed_client import IndeedClient
from .api_clients.linkedin_client import LinkedInClient

# ──────────────────────────────────────────────────────────────────────────────
# Firestore client (optional — falls back gracefully if Firebase not configured)
# ──────────────────────────────────────────────────────────────────────────────
try:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config import get_firestore_client
    _db = get_firestore_client()
    _FIRESTORE_AVAILABLE = True
except Exception:
    _db = None
    _FIRESTORE_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
CACHE_TTL_MINUTES = 30
CACHE_COLLECTION = "job_cache"
JOBS_COLLECTION = "jobs"
RESULTS_PER_SOURCE = 15  # how many results to request from each scraper

# ──────────────────────────────────────────────────────────────────────────────
# Router
# ──────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ──────────────────────────────────────────────────────────────────────────────
# Caching helpers
# ──────────────────────────────────────────────────────────────────────────────

def _cache_key(params: JobSearchParams, source: str = "all") -> str:
    """Generate a deterministic Firestore document ID from search params."""
    raw = json.dumps({
        "q": params.query,
        "loc": params.location,
        "src": source,
        "wm": params.work_mode,
        "np": params.notice_period,
        "min_sal": params.min_salary_lpa,
    }, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _read_cache(key: str) -> Optional[list[dict]]:
    """
    Read a cached result from Firestore.
    Returns None if cache is missing or expired.
    """
    if not _FIRESTORE_AVAILABLE:
        return None
    try:
        doc = _db.collection(CACHE_COLLECTION).document(key).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        cached_at = data.get("cached_at")
        if cached_at:
            age = datetime.now(timezone.utc) - cached_at.replace(tzinfo=timezone.utc)
            if age > timedelta(minutes=CACHE_TTL_MINUTES):
                return None  # expired
        return data.get("results", [])
    except Exception:
        return None


def _write_cache(key: str, results: list[dict]) -> None:
    """Store search results in Firestore with a timestamp."""
    if not _FIRESTORE_AVAILABLE:
        return
    try:
        _db.collection(CACHE_COLLECTION).document(key).set({
            "cached_at": datetime.now(timezone.utc),
            "results": results,
        })
    except Exception:
        pass  # caching failure should never break the response


# ──────────────────────────────────────────────────────────────────────────────
# Scraping helpers
# ──────────────────────────────────────────────────────────────────────────────

async def _run_scrapers(
    params: JobSearchParams, source_filter: str = ""
) -> list[dict]:
    """
    Run the appropriate scraper clients concurrently.

    Args:
        params: Normalised search parameters.
        source_filter: If non-empty, only run this specific scraper.

    Returns:
        Combined list of job dicts ready to be sent to the frontend.
    """
    naukri = NaukriClient()
    indeed = IndeedClient()
    linkedin = LinkedInClient()

    tasks = []
    if not source_filter or source_filter == "naukri":
        tasks.append(naukri.search(params))
    if not source_filter or source_filter == "indeed":
        tasks.append(indeed.search(params))
    if not source_filter or source_filter == "linkedin":
        tasks.append(linkedin.search(params))

    # Run all scrapers concurrently — a single slow scraper won't block others
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    combined: list[dict] = []
    for result in all_results:
        if isinstance(result, Exception):
            continue  # one scraper failing doesn't kill the response
        for job in result:
            combined.append(job.to_api_dict())

    # Deduplicate by job id
    seen: set[str] = set()
    unique = []
    for job in combined:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)

    return unique


def _apply_post_filters(jobs: list[dict], params: JobSearchParams) -> list[dict]:
    """
    Apply filters that cannot be expressed as scraper-level query params
    (e.g., LPA range filtering when the scraper returns salary as a string).
    """
    filtered = []
    for job in jobs:
        # Salary range filter (parse the "X-Y LPA" string back to numbers)
        if params.min_salary_lpa is not None or params.max_salary_lpa is not None:
            salary_str = job.get("salary") or ""
            lpa = _parse_lpa(salary_str)
            if lpa is not None:
                if params.min_salary_lpa and lpa < params.min_salary_lpa:
                    continue
                if params.max_salary_lpa and lpa > params.max_salary_lpa:
                    continue

        # Work mode filter (belt-and-suspenders after scraper-level filter)
        if params.work_mode and params.work_mode != "any":
            if job.get("workMode", "onsite") != params.work_mode:
                continue

        filtered.append(job)

    return filtered


def _parse_lpa(salary_str: str) -> Optional[float]:
    """Extract the lower bound of a salary string like '8-14 LPA' → 8.0."""
    import re
    m = re.search(r"(\d+(?:\.\d+)?)", salary_str)
    return float(m.group(1)) if m else None


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "jobs",
        "firestore_cache": _FIRESTORE_AVAILABLE,
        "scrapers": ["naukri", "indeed", "linkedin"],
    }


@router.get("/search")
async def search_jobs(
    query: str = Query("", description="Job title, skills, or company name"),
    location: str = Query("India", description="City or region (e.g. Bangalore, Remote)"),
    source: str = Query("", description="Filter by source: naukri | indeed | linkedin | (empty=all)"),
    min_salary_lpa: Optional[float] = Query(None, description="Minimum salary in Lakhs Per Annum"),
    max_salary_lpa: Optional[float] = Query(None, description="Maximum salary in LPA"),
    work_mode: str = Query("any", description="remote | hybrid | onsite | any"),
    notice_period: str = Query("any", description="immediate | 15days | 30days | 60days | 90days | any"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
):
    """
    Search for jobs across Naukri, Indeed, and LinkedIn.

    Results are cached in Firestore for 30 minutes. Repeated identical
    searches return instantly without hitting the scrapers again.
    """
    params = JobSearchParams(
        query=query or "Software Engineer",
        location=location,
        limit=RESULTS_PER_SOURCE,
        min_salary_lpa=min_salary_lpa,
        max_salary_lpa=max_salary_lpa,
        work_mode=work_mode,
        notice_period=notice_period,
    )

    # Try Firestore cache first
    key = _cache_key(params, source)
    cached = _read_cache(key)
    if cached is not None:
        start = (page - 1) * limit
        return cached[start: start + limit]

    # Cache miss — run scrapers
    results = await _run_scrapers(params, source_filter=source)

    # Apply post-filters (salary range, work mode double-check)
    results = _apply_post_filters(results, params)

    # Persist to Firestore cache
    _write_cache(key, results)

    # Also upsert individual job documents into the `jobs` collection so the
    # Kanban and Dashboard services can reference them by ID
    _upsert_jobs_to_firestore(results)

    start = (page - 1) * limit
    return results[start: start + limit]


@router.get("/recommended")
async def get_recommended_jobs(
    location: str = Query("India"),
    source: str = Query(""),
    work_mode: str = Query("any"),
    limit: int = Query(10, le=30),
):
    """
    Return a curated list of recommended jobs using popular Indian tech keywords.
    Used on the Dashboard page and Onboarding screen.
    """
    params = JobSearchParams(
        query="Software Engineer Python React",
        location=location,
        limit=RESULTS_PER_SOURCE,
        work_mode=work_mode,
    )

    key = _cache_key(params, source + "_recommended")
    cached = _read_cache(key)
    if cached is not None:
        return cached[:limit]

    results = await _run_scrapers(params, source_filter=source)
    _write_cache(key, results)
    return results[:limit]


@router.post("/sync")
async def sync_job_sources(
    query: str = Query("Software Engineer", description="Keyword to refresh"),
    location: str = Query("India"),
):
    """
    Bypass the cache and force a fresh scrape from all sources.
    Stores the updated results back into Firestore.

    Returns the count of freshly synced jobs per source.
    """
    params = JobSearchParams(
        query=query,
        location=location,
        limit=RESULTS_PER_SOURCE,
    )

    results = await _run_scrapers(params, source_filter="")

    # Re-populate cache
    key = _cache_key(params, "all")
    _write_cache(key, results)
    _upsert_jobs_to_firestore(results)

    by_source: dict[str, int] = {}
    for job in results:
        src = job.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    return {"synced": len(results), "by_source": by_source}


# ──────────────────────────────────────────────────────────────────────────────
# Firestore persistence
# ──────────────────────────────────────────────────────────────────────────────

def _upsert_jobs_to_firestore(jobs: list[dict]) -> None:
    """
    Persist/update individual job documents in the `jobs` Firestore collection.
    This is a fire-and-forget operation — errors are swallowed silently.
    """
    if not _FIRESTORE_AVAILABLE:
        return
    try:
        batch = _db.batch()
        for job in jobs[:400]:  # Firestore batch limit is 500
            ref = _db.collection(JOBS_COLLECTION).document(job["id"])
            batch.set(ref, {
                **job,
                "indexed_at": datetime.now(timezone.utc),
            }, merge=True)
        batch.commit()
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# FastAPI application (mounts the router)
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Jobs Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Jobs Service Running", "version": "1.0.0"}
