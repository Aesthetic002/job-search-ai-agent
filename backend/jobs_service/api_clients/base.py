"""
Shared base types and utilities for all job scraper clients.
"""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class JobSearchParams:
    """Unified search parameters passed to every scraper client."""

    query: str                          # e.g. "Python Developer"
    location: str = "India"             # City or "India" for national
    limit: int = 20                     # Max results to return (per source)
    min_salary_lpa: Optional[float] = None  # Minimum salary in Lakhs Per Annum
    max_salary_lpa: Optional[float] = None  # Maximum salary in LPA
    work_mode: str = "any"              # "remote" | "hybrid" | "onsite" | "any"
    notice_period: str = "any"          # "immediate" | "15days" | "30days" | "60days" | "90days" | "any"
    experience_years: Optional[int] = None  # Min years of experience required
    tags: list[str] = field(default_factory=list)  # Must-have skill tags


@dataclass
class JobListing:
    """
    Canonical job listing format — all scrapers produce this shape.
    This is what gets stored in Firestore and returned to the frontend.
    """

    id: str                             # Unique: "{source}-{source_job_id}"
    source: str                         # "naukri" | "indeed" | "linkedin"
    title: str
    company: str
    location: str
    description: str
    url: str
    tags: list[str]
    posted_at: str                      # ISO 8601 string

    # Indian-specific fields
    salary: Optional[str] = None        # Human-readable, e.g. "8-14 LPA"
    work_mode: str = "onsite"           # "remote" | "hybrid" | "onsite"
    experience_required: str = ""       # e.g. "3-5 Years"
    notice_period: str = ""             # e.g. "30 Days"

    def to_firestore_dict(self) -> dict:
        """
        Serialize to a flat dict suitable for Firestore storage.
        Snake_case keys match what the frontend api.ts expects after remapping.
        """
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "url": self.url,
            "tags": self.tags,
            "posted_at": self.posted_at,
            "salary": self.salary,
            "work_mode": self.work_mode,
            "experience_required": self.experience_required,
            "notice_period": self.notice_period,
            # match_score will be computed and injected by the routes layer
            "match_score": None,
        }

    def to_api_dict(self) -> dict:
        """
        Serialize to the JSON shape the frontend Job interface expects.
        Maps snake_case fields → camelCase for the TypeScript frontend.
        """
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary": self.salary,
            "source": self.source,
            "tags": self.tags,
            "postedAt": self.posted_at,
            "url": self.url,
            "description": self.description,
            "matchScore": None,          # injected by the ATS layer
            # Indian-specific (extra fields, ignored by TS if not in interface)
            "workMode": self.work_mode,
            "experienceRequired": self.experience_required,
            "noticePeriod": self.notice_period,
        }


def format_salary_lpa(raw: str) -> Optional[str]:
    """
    Normalize raw salary strings to a clean LPA format.

    Examples:
        "8,00,000 - 12,00,000 PA"  → "8-12 LPA"
        "Not Disclosed"            → None
        "10-14 Lakhs"              → "10-14 LPA"
        "₹ 5,00,000"               → "5 LPA"
        ""                         → None
    """
    if not raw or "not disclose" in raw.lower() or "confidential" in raw.lower():
        return None

    # Strip currency symbols
    raw = raw.replace("₹", "").replace(",", "").strip()

    # Already in lakhs ("X-Y Lakhs" or "X-Y LPA")
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*(lpa|lakh|lac)", raw, re.IGNORECASE)
    if lpa_match:
        lo, hi = lpa_match.group(1), lpa_match.group(2)
        return f"{lo}-{hi} LPA"

    single_lpa = re.search(r"(\d+(?:\.\d+)?)\s*(lpa|lakh|lac)", raw, re.IGNORECASE)
    if single_lpa:
        return f"{single_lpa.group(1)} LPA"

    # In rupees per annum (e.g. "800000 - 1200000 PA" or just "800000")
    rupee_range = re.search(r"(\d{6,})\s*[-–to]+\s*(\d{6,})", raw, re.IGNORECASE)
    if rupee_range:
        lo = round(int(rupee_range.group(1)) / 100_000, 1)
        hi = round(int(rupee_range.group(2)) / 100_000, 1)
        return f"{lo}-{hi} LPA"

    single_rupee = re.search(r"(\d{6,})", raw)
    if single_rupee:
        lpa = round(int(single_rupee.group(1)) / 100_000, 1)
        return f"{lpa} LPA"

    return None
