"""
Pydantic schemas for analytics_service request/response validation.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ApplicationStats(BaseModel):
    """Schema for overall application statistics."""
    total_applications: int
    applications_by_status: Dict[str, int]
    recent_applications: int  # Last 7 days


class ApplicationTrend(BaseModel):
    """Schema for application trend data."""
    date: str
    count: int


class TopCompany(BaseModel):
    """Schema for top applied companies."""
    company: str
    application_count: int


class AnalyticsSummary(BaseModel):
    """Schema for complete analytics summary."""
    total_applications: int
    total_jobs_viewed: int
    applications_by_status: Dict[str, int]
    weekly_applications: List[ApplicationTrend]
    top_companies: List[TopCompany]
    success_rate: float  # Percentage of offers/interviews


class DateRangeFilter(BaseModel):
    """Schema for date range filtering."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MetricResponse(BaseModel):
    """Schema for individual metric response."""
    metric_name: str
    value: float
    description: Optional[str] = None
    change_percentage: Optional[float] = None  # Compared to previous period
