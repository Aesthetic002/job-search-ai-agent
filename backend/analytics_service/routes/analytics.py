"""
Analytics routes for application statistics and metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta

from ..models import Application, Job, ApplicationStatus
from ..schemas import (
    AnalyticsSummary,
    ApplicationStats,
    ApplicationTrend,
    TopCompany,
    MetricResponse
)
from ..dependencies import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user_id: int = Query(..., description="User ID to get analytics for"),
    db: Session = Depends(get_db)
):
    """
    Get complete analytics summary for a user.

    Returns:
    - Total applications
    - Applications by status
    - Weekly application trends
    - Top applied companies
    - Success rate
    """
    # Total applications
    total_applications = db.query(func.count(Application.id)).filter(
        Application.user_id == user_id
    ).scalar() or 0

    # Applications by status
    status_counts = db.query(
        Application.status,
        func.count(Application.id)
    ).filter(
        Application.user_id == user_id
    ).group_by(Application.status).all()

    applications_by_status = {status: count for status, count in status_counts}

    # Weekly applications (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    weekly_data = db.query(
        func.date(Application.applied_at).label("date"),
        func.count(Application.id).label("count")
    ).filter(
        and_(
            Application.user_id == user_id,
            Application.applied_at >= seven_days_ago
        )
    ).group_by(func.date(Application.applied_at)).all()

    weekly_applications = [
        ApplicationTrend(date=str(row.date), count=row.count)
        for row in weekly_data
    ]

    # Top companies
    top_companies_data = db.query(
        Job.company,
        func.count(Application.id).label("count")
    ).join(
        Application, Application.job_id == Job.id
    ).filter(
        Application.user_id == user_id
    ).group_by(Job.company).order_by(
        func.count(Application.id).desc()
    ).limit(5).all()

    top_companies = [
        TopCompany(company=row.company or "Unknown", application_count=row.count)
        for row in top_companies_data
    ]

    # Success rate (offers + interviews / total)
    success_count = db.query(func.count(Application.id)).filter(
        and_(
            Application.user_id == user_id,
            Application.status.in_([ApplicationStatus.OFFER.value, ApplicationStatus.INTERVIEW.value])
        )
    ).scalar() or 0

    success_rate = (success_count / total_applications * 100) if total_applications > 0 else 0.0

    # Total jobs viewed (using job count as proxy)
    total_jobs_viewed = db.query(func.count(Job.id)).scalar() or 0

    return AnalyticsSummary(
        total_applications=total_applications,
        total_jobs_viewed=total_jobs_viewed,
        applications_by_status=applications_by_status,
        weekly_applications=weekly_applications,
        top_companies=top_companies,
        success_rate=round(success_rate, 2)
    )


@router.get("/applications", response_model=ApplicationStats)
async def get_application_stats(
    user_id: int = Query(..., description="User ID to get stats for"),
    db: Session = Depends(get_db)
):
    """
    Get application statistics for a user.

    Returns total applications, breakdown by status, and recent activity.
    """
    # Total applications
    total = db.query(func.count(Application.id)).filter(
        Application.user_id == user_id
    ).scalar() or 0

    # By status
    status_counts = db.query(
        Application.status,
        func.count(Application.id)
    ).filter(
        Application.user_id == user_id
    ).group_by(Application.status).all()

    applications_by_status = {status: count for status, count in status_counts}

    # Recent (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent = db.query(func.count(Application.id)).filter(
        and_(
            Application.user_id == user_id,
            Application.applied_at >= seven_days_ago
        )
    ).scalar() or 0

    return ApplicationStats(
        total_applications=total,
        applications_by_status=applications_by_status,
        recent_applications=recent
    )


@router.get("/metrics/success-rate", response_model=MetricResponse)
async def get_success_rate(
    user_id: int = Query(..., description="User ID to get metric for"),
    db: Session = Depends(get_db)
):
    """
    Get the success rate metric for a user.

    Success rate = (Offers + Interviews) / Total Applications
    """
    total = db.query(func.count(Application.id)).filter(
        Application.user_id == user_id
    ).scalar() or 0

    success_count = db.query(func.count(Application.id)).filter(
        and_(
            Application.user_id == user_id,
            Application.status.in_([ApplicationStatus.OFFER.value, ApplicationStatus.INTERVIEW.value])
        )
    ).scalar() or 0

    rate = (success_count / total * 100) if total > 0 else 0.0

    return MetricResponse(
        metric_name="success_rate",
        value=round(rate, 2),
        description="Percentage of applications resulting in interviews or offers"
    )


@router.get("/metrics/response-rate", response_model=MetricResponse)
async def get_response_rate(
    user_id: int = Query(..., description="User ID to get metric for"),
    db: Session = Depends(get_db)
):
    """
    Get the response rate metric for a user.

    Response rate = (All non-applied statuses) / Total Applications
    """
    total = db.query(func.count(Application.id)).filter(
        Application.user_id == user_id
    ).scalar() or 0

    responded = db.query(func.count(Application.id)).filter(
        and_(
            Application.user_id == user_id,
            Application.status != ApplicationStatus.APPLIED.value
        )
    ).scalar() or 0

    rate = (responded / total * 100) if total > 0 else 0.0

    return MetricResponse(
        metric_name="response_rate",
        value=round(rate, 2),
        description="Percentage of applications that received a response"
    )


@router.get("/trends/weekly")
async def get_weekly_trends(
    user_id: int = Query(..., description="User ID to get trends for"),
    weeks: int = Query(4, ge=1, le=12, description="Number of weeks to include"),
    db: Session = Depends(get_db)
):
    """
    Get weekly application trends for the specified number of weeks.
    """
    start_date = datetime.utcnow() - timedelta(weeks=weeks)

    weekly_data = db.query(
        func.date_trunc('week', Application.applied_at).label("week"),
        func.count(Application.id).label("count")
    ).filter(
        and_(
            Application.user_id == user_id,
            Application.applied_at >= start_date
        )
    ).group_by(
        func.date_trunc('week', Application.applied_at)
    ).order_by("week").all()

    return {
        "user_id": user_id,
        "weeks": weeks,
        "trends": [
            {"week": str(row.week), "applications": row.count}
            for row in weekly_data
        ]
    }
