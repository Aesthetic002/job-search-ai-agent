"""
LinkedIn Jobs Scraper Client
=============================
LinkedIn does NOT have a public jobs API (their official APIs are restricted
to approved partners with NDAs). This client uses a well-known workaround:
LinkedIn's public job search page exposes a JSON endpoint used by their
"Jobs you may be interested in" widget that is accessible without authentication
for public job postings.

Endpoint: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search

This approach is widely documented and used in open-source projects. However,
LinkedIn can change this endpoint at any time — the client handles this
gracefully by returning an empty list on any error.

Note: This is for aggregation/demo purposes. In production, use the
LinkedIn Job Search API (requires partnership approval).
"""

import httpx
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from bs4 import BeautifulSoup
from .base import JobListing, JobSearchParams

_BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.linkedin.com/",
}

# LinkedIn f_WT filter values for work type
_WORK_TYPE_MAP = {
    "remote": "2",
    "hybrid": "3",
    "onsite": "1",
}


class LinkedInClient:
    """Async scraper for LinkedIn public job listings."""

    SOURCE = "linkedin"

    async def search(self, params: JobSearchParams) -> list[JobListing]:
        """
        Fetch jobs from LinkedIn matching the given params.

        Returns an empty list on any network/parse error — never raises.
        """
        results: list[JobListing] = []
        start = 0
        batch = 10  # LinkedIn returns 10 per page from this endpoint

        async with httpx.AsyncClient(
            timeout=15, follow_redirects=True, headers=_HEADERS
        ) as client:
            while len(results) < params.limit:
                query_params = self._build_query(params, start)
                try:
                    resp = await client.get(_BASE_URL, params=query_params)
                    if resp.status_code != 200:
                        break
                    jobs_raw = self._parse_html(resp.text)
                except Exception:
                    break

                if not jobs_raw:
                    break

                for raw in jobs_raw:
                    listing = self._map_job(raw)
                    if listing:
                        results.append(listing)

                if len(jobs_raw) < batch:
                    break  # end of results

                start += batch
                await asyncio.sleep(1.2)  # LinkedIn rate limits aggressively

        return results[: params.limit]

    # ──────────────────────────────────────────────────────────────────────────

    def _build_query(self, params: JobSearchParams, start: int) -> dict:
        q: dict = {
            "keywords": params.query,
            "location": params.location or "India",
            "geoId": "102713980",  # India geo ID
            "trk": "public_jobs_jobs-search-bar_search-submit",
            "start": start,
            "count": 10,
        }
        if params.work_mode and params.work_mode in _WORK_TYPE_MAP:
            q["f_WT"] = _WORK_TYPE_MAP[params.work_mode]
        # Date posted filter: r2592000 = last 30 days
        q["f_TPR"] = "r2592000"
        return q

    def _parse_html(self, html: str) -> list[dict]:
        """Parse the HTML fragment LinkedIn returns for job cards."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.find_all("li")
            jobs = []
            for card in cards:
                job = {}
                title_el = card.find("h3", {"class": "base-search-card__title"})
                company_el = card.find("h4", {"class": "base-search-card__subtitle"})
                location_el = card.find(
                    "span", {"class": "job-search-card__location"}
                )
                date_el = card.find("time")
                link_el = card.find("a", {"class": "base-card__full-link"})
                job_id_el = card.find("div", {"class": "base-card"})

                job["title"] = title_el.get_text(strip=True) if title_el else ""
                job["company"] = company_el.get_text(strip=True) if company_el else ""
                job["location"] = (
                    location_el.get_text(strip=True) if location_el else "India"
                )
                job["url"] = link_el["href"] if link_el else ""
                job["date"] = date_el.get("datetime", "") if date_el else ""
                job["job_id"] = (
                    job_id_el.get("data-entity-urn", "").split(":")[-1]
                    if job_id_el
                    else str(uuid.uuid4())
                )
                if job["title"]:  # skip empty cards
                    jobs.append(job)
            return jobs
        except Exception:
            return []

    def _map_job(self, raw: dict) -> Optional[JobListing]:
        """Map a parsed LinkedIn card dict to the unified JobListing schema."""
        try:
            job_id = raw.get("job_id", str(uuid.uuid4()))
            title = raw.get("title", "").strip()
            if not title:
                return None

            return JobListing(
                id=f"linkedin-{job_id}",
                source="linkedin",
                title=title,
                company=raw.get("company", "").strip(),
                location=raw.get("location", "India").strip(),
                salary=None,  # LinkedIn doesn't surface salary in list view
                description=f"View the full job description on LinkedIn.",
                url=raw.get("url", f"https://www.linkedin.com/jobs/view/{job_id}"),
                tags=self._extract_tags(title),
                posted_at=self._parse_date(raw.get("date", "")),
                work_mode=self._infer_work_mode(raw),
                experience_required="",
            )
        except Exception:
            return None

    def _extract_tags(self, title: str) -> list[str]:
        """Extract likely tech tags from the job title."""
        known = [
            "Python", "Java", "React", "Angular", "Node.js", "AWS", "GCP",
            "Azure", "DevOps", "ML", "AI", "Data Science", "Backend",
            "Frontend", "Full Stack", "Mobile", "iOS", "Android", "SRE",
        ]
        return [k for k in known if k.lower() in title.lower()][:5]

    def _parse_date(self, date_str: str) -> str:
        """Parse LinkedIn ISO date string or relative label."""
        if not date_str:
            return datetime.now(timezone.utc).isoformat()
        try:
            # LinkedIn sometimes provides full ISO: "2024-05-28"
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            return datetime.now(timezone.utc).isoformat()

    def _infer_work_mode(self, raw: dict) -> str:
        text = (raw.get("title", "") + " " + raw.get("location", "")).lower()
        if "remote" in text:
            return "remote"
        if "hybrid" in text:
            return "hybrid"
        return "onsite"
