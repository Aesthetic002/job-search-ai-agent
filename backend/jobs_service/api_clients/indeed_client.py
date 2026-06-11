"""
Indeed India Scraper Client
============================
Uses the Indeed Job Search Publisher API (free, no credit card required).
Publisher API endpoint: https://api.indeed.com/ads/apisearch

To use this client you need an Indeed Publisher ID (free at
https://ads.indeed.com/jobroll/xmlfeed). Set it as INDEED_PUBLISHER_ID
in your .env file.

Fallback: if no publisher ID is configured, the client returns an empty list
so the rest of the search pipeline continues without errors.
"""

import httpx
import asyncio
import xml.etree.ElementTree as ET
import uuid
from datetime import datetime, timezone
from typing import Optional
from .base import JobListing, JobSearchParams, format_salary_lpa
import os

_INDEED_API = "https://api.indeed.com/ads/apisearch"


class IndeedClient:
    """Async scraper for Indeed India via the Publisher API."""

    SOURCE = "indeed"

    def __init__(self):
        self._publisher_id = os.getenv("INDEED_PUBLISHER_ID", "")

    async def search(self, params: JobSearchParams) -> list[JobListing]:
        """
        Fetch jobs from Indeed India matching the given params.

        If INDEED_PUBLISHER_ID is not set, returns an empty list gracefully.
        """
        if not self._publisher_id:
            return []

        results: list[JobListing] = []
        start = 0
        batch = min(params.limit, 25)  # Indeed Publisher API max is 25

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            while len(results) < params.limit:
                query_params = self._build_query(params, start, batch)
                try:
                    resp = await client.get(_INDEED_API, params=query_params)
                    if resp.status_code != 200:
                        break
                    jobs_raw = self._parse_xml(resp.text)
                except Exception:
                    break

                if not jobs_raw:
                    break

                for raw in jobs_raw:
                    listing = self._map_job(raw)
                    if listing:
                        results.append(listing)

                if len(jobs_raw) < batch:
                    break  # no more pages

                start += batch
                await asyncio.sleep(0.5)

        return results[: params.limit]

    # ──────────────────────────────────────────────────────────────────────────

    def _build_query(
        self, params: JobSearchParams, start: int, limit: int
    ) -> dict:
        q: dict = {
            "publisher": self._publisher_id,
            "q": params.query,
            "co": "in",           # country = India
            "l": params.location or "India",
            "sort": "relevance",
            "radius": 50,
            "st": "",
            "jt": "fulltime",
            "start": start,
            "limit": limit,
            "fromage": 30,        # posted in last 30 days
            "highlight": 0,
            "filter": 1,
            "latlong": 1,
            "v": 2,
        }
        if params.work_mode == "remote":
            q["remotejob"] = 1
        return q

    def _parse_xml(self, xml_text: str) -> list[dict]:
        """Parse the XML response from Indeed Publisher API."""
        try:
            root = ET.fromstring(xml_text)
            jobs = []
            for result in root.findall(".//result"):
                jobs.append({child.tag: child.text for child in result})
            return jobs
        except ET.ParseError:
            return []

    def _map_job(self, raw: dict) -> Optional[JobListing]:
        """Map a raw Indeed XML result dict to our JobListing schema."""
        try:
            job_id = raw.get("jobkey", str(uuid.uuid4()))

            # Build tags from snippet keywords (crude but functional)
            snippet = raw.get("snippet", "")
            tags = self._extract_tags(snippet, raw.get("jobtitle", ""))

            # Indeed salary field is often absent for India
            salary_str = format_salary_lpa(raw.get("formattedRelativeTime", ""))

            posted = raw.get("date", "")

            return JobListing(
                id=f"indeed-{job_id}",
                source="indeed",
                title=(raw.get("jobtitle") or "").strip(),
                company=(raw.get("company") or "").strip(),
                location=(raw.get("formattedLocation") or "India").strip(),
                salary=None,
                description=snippet.strip(),
                url=raw.get("url", f"https://in.indeed.com/viewjob?jk={job_id}"),
                tags=tags,
                posted_at=self._parse_date(posted),
                work_mode=self._infer_work_mode(raw),
                experience_required="",
            )
        except Exception:
            return None

    def _extract_tags(self, snippet: str, title: str) -> list[str]:
        """Crude keyword extractor — looks for common tech terms."""
        common_skills = [
            "Python", "Java", "React", "Node.js", "SQL", "AWS", "GCP",
            "Azure", "Docker", "Kubernetes", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "FastAPI", "Django", "Spring Boot",
            "TypeScript", "JavaScript", "MongoDB", "PostgreSQL", "Redis",
            "DevOps", "CI/CD", "Agile", "Scrum", "REST API", "GraphQL",
        ]
        combined = (snippet + " " + title).lower()
        return [s for s in common_skills if s.lower() in combined][:6]

    def _parse_date(self, date_str: str) -> str:
        """Parse Indeed's date string into ISO 8601."""
        try:
            # Indeed returns RFC 2822: "Tue, 28 May 2024 12:00:00 GMT"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

    def _infer_work_mode(self, raw: dict) -> str:
        text = ((raw.get("jobtitle") or "") + " " + (raw.get("snippet") or "")).lower()
        if "remote" in text:
            return "remote"
        if "hybrid" in text:
            return "hybrid"
        return "onsite"
