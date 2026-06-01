"""
Naukri.com Scraper Client
=========================
Uses Naukri's internal JSON search API (same endpoint their web app calls).
No official API is publicly available, so we replicate the XHR search request
that the Naukri website itself makes. This is the standard approach used by
most Naukri scrapers in the open-source community.

Rate-limiting: built-in 1-second delay between paginated requests.
Caching: the jobs_routes layer caches results in Firestore for 30 minutes.
"""

import httpx
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional
from .base import JobListing, JobSearchParams, format_salary_lpa

# Naukri's internal search endpoint (same one their React SPA calls)
_SEARCH_URL = "https://www.naukri.com/jobapi/v3/search"

# Standard browser headers — required to avoid 403 from Naukri's CDN
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.naukri.com/",
    "appid": "109",
    "systemid": "Naukri",
}


class NaukriClient:
    """Async scraper client for Naukri.com job listings."""

    SOURCE = "naukri"

    async def search(self, params: JobSearchParams) -> list[JobListing]:
        """
        Fetch job listings from Naukri matching the given params.

        Args:
            params: Standardised search parameters (query, location, filters)

        Returns:
            List of JobListing objects ready to be stored in Firestore.
        """
        results: list[JobListing] = []
        page = 1
        per_page = min(params.limit, 20)  # Naukri max per-page is 20

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            while len(results) < params.limit:
                payload = self._build_query(params, page, per_page)
                try:
                    resp = await client.get(
                        _SEARCH_URL, params=payload, headers=_HEADERS
                    )
                    if resp.status_code != 200:
                        break
                    data = resp.json()
                except Exception:
                    break

                jobs_raw = data.get("jobDetails") or []
                if not jobs_raw:
                    break

                for raw in jobs_raw:
                    listing = self._parse_job(raw)
                    if listing:
                        results.append(listing)

                if len(jobs_raw) < per_page:
                    break  # no more pages

                page += 1
                await asyncio.sleep(1.0)  # respectful rate limit

        return results[: params.limit]

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _build_query(
        self, params: JobSearchParams, page: int, per_page: int
    ) -> dict:
        """Build the Naukri search query-string parameters."""
        q: dict = {
            "noOfResults": per_page,
            "urlType": "search_by_key_loc",
            "searchType": "adv",
            "keyword": params.query,
            "pageNo": page,
            "sort": "r",        # r = relevance, d = date
            "areaLabel": "",
            "k": params.query,
        }
        if params.location:
            q["location"] = params.location
            q["l"] = params.location
        if params.min_salary_lpa:
            # Naukri accepts salary in lakhs as integer (e.g., 5 = 5 LPA)
            q["salary"] = int(params.min_salary_lpa)
        if params.work_mode and params.work_mode != "any":
            mode_map = {"remote": "7", "hybrid": "9", "onsite": "6"}
            if params.work_mode in mode_map:
                q["wfhType"] = mode_map[params.work_mode]
        return q

    def _parse_job(self, raw: dict) -> Optional[JobListing]:
        """Map a raw Naukri JSON job object to our unified JobListing schema."""
        try:
            job_id = raw.get("jobId") or raw.get("jobid") or str(uuid.uuid4())

            # Salary — Naukri returns "Not Disclosed" or "X-Y Lakhs"
            salary_raw = raw.get("salary", "")
            salary_str = format_salary_lpa(salary_raw)

            # Skills/tags from placeholders list
            tags = [
                s.get("label", "")
                for s in (raw.get("tagsAndSkills") or [])
            ]
            tags = [t for t in tags if t][:8]

            # Notice period appears in job detail, not list — omit from card
            posted_raw = raw.get("footerPlaceholderLabel", "")

            return JobListing(
                id=f"naukri-{job_id}",
                source="naukri",
                title=raw.get("title", "").strip(),
                company=raw.get("companyName", "").strip(),
                location=raw.get("placeholders", [{}])[0].get("label", "India"),
                salary=salary_str,
                description=raw.get("jobDescription", raw.get("snippet", "")).strip(),
                url=raw.get("jdURL", f"https://www.naukri.com/{job_id}"),
                tags=tags,
                posted_at=self._parse_date(posted_raw),
                work_mode=self._infer_work_mode(raw),
                experience_required=raw.get("experienceText", ""),
            )
        except Exception:
            return None

    def _parse_date(self, label: str) -> str:
        """Convert Naukri relative date strings to ISO 8601."""
        now = datetime.now(timezone.utc)
        label = label.lower()
        if "today" in label or "just now" in label or "hour" in label:
            return now.isoformat()
        if "yesterday" in label:
            from datetime import timedelta
            return (now - timedelta(days=1)).isoformat()
        if "day" in label:
            try:
                days = int("".join(filter(str.isdigit, label)))
                from datetime import timedelta
                return (now - timedelta(days=days)).isoformat()
            except ValueError:
                pass
        return now.isoformat()

    def _infer_work_mode(self, raw: dict) -> str:
        """Infer work mode from tags/title since Naukri doesn't always surface it."""
        text = (raw.get("title", "") + " " + raw.get("jobDescription", "")).lower()
        if "remote" in text or "work from home" in text or "wfh" in text:
            return "remote"
        if "hybrid" in text:
            return "hybrid"
        return "onsite"
