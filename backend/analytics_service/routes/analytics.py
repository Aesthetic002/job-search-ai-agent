"""
Analytics routes for application statistics and metrics.
Uses Firestore for data storage.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore_v1 import Client as FirestoreClient
from typing import Optional, List,Dict
from datetime import datetime, timedelta
from collections import Counter

from ..schemas import (
    AnalyticsSummary,
    ApplicationStats,
    ApplicationTrend,
    TopCompany,
    MetricResponse
)
from ..dependencies import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_user_applications(db: FirestoreClient, user_id: str) -> List[Dict]:
    """Get all applications for a user from Firestore."""
    applications_ref = db.collection('applications')
    query = applications_ref.where('user_id', '==', user_id)
    docs = query.stream()

    applications = []
    for doc in docs:
        app_data = doc.to_dict()
        app_data['id'] = doc.id
        applications.append(app_data)

    return applications


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user_id: str = Query(..., description="User ID to get analytics for"),
    db: FirestoreClient = Depends(get_db)
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
    # Get all applications for user
    applications = get_user_applications(db, user_id)

    # Total applications
    total_applications = len(applications)

    # Applications by status
    status_counter = Counter(app.get('status', 'applied') for app in applications)
    applications_by_status = dict(status_counter)

    # Weekly applications (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_counts = Counter()

    for app in applications:
        applied_at = app.get('applied_at')
        if applied_at:
            # Handle Firestore timestamp
            if hasattr(applied_at, 'timestamp'):
                app_date = datetime.fromtimestamp(applied_at.timestamp())
            else:
                app_date = applied_at

            if app_date >= seven_days_ago:
                date_str = app_date.strftime('%Y-%m-%d')
                daily_counts[date_str] += 1

    weekly_applications = [
        ApplicationTrend(date=date, count=count)
        for date, count in sorted(daily_counts.items())
    ]

    # Top companies
    company_counter = Counter(app.get('company', 'Unknown') for app in applications)
    top_companies = [
        TopCompany(company=company, application_count=count)
        for company, count in company_counter.most_common(5)
    ]

    # Success rate (offers + interviews / total)
    success_count = sum(
        1 for app in applications
        if app.get('status') in ['offer', 'interview']
    )
    success_rate = (success_count / total_applications * 100) if total_applications > 0 else 0.0

    # Total jobs viewed (count unique jobs across all users)
    jobs_ref = db.collection('jobs')
    total_jobs_viewed = len(list(jobs_ref.limit(1000).stream()))

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
    user_id: str = Query(..., description="User ID to get stats for"),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get application statistics for a user.

    Returns total applications, breakdown by status, and recent activity.
    """
    # Get all applications for user
    applications = get_user_applications(db, user_id)

    # Total applications
    total = len(applications)

    # By status
    status_counter = Counter(app.get('status', 'applied') for app in applications)
    applications_by_status = dict(status_counter)

    # Recent (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent = sum(
        1 for app in applications
        if app.get('applied_at') and
        (datetime.fromtimestamp(app['applied_at'].timestamp())
         if hasattr(app['applied_at'], 'timestamp')
         else app['applied_at']) >= seven_days_ago
    )

    return ApplicationStats(
        total_applications=total,
        applications_by_status=applications_by_status,
        recent_applications=recent
    )


@router.get("/metrics/success-rate", response_model=MetricResponse)
async def get_success_rate(
    user_id: str = Query(..., description="User ID to get metric for"),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get the success rate metric for a user.

    Success rate = (Offers + Interviews) / Total Applications
    """
    applications = get_user_applications(db, user_id)
    total = len(applications)

    success_count = sum(
        1 for app in applications
        if app.get('status') in ['offer', 'interview']
    )

    rate = (success_count / total * 100) if total > 0 else 0.0

    return MetricResponse(
        metric_name="success_rate",
        value=round(rate, 2),
        description="Percentage of applications resulting in interviews or offers"
    )


@router.get("/metrics/response-rate", response_model=MetricResponse)
async def get_response_rate(
    user_id: str = Query(..., description="User ID to get metric for"),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get the response rate metric for a user.

    Response rate = (All non-applied statuses) / Total Applications
    """
    applications = get_user_applications(db, user_id)
    total = len(applications)

    responded = sum(
        1 for app in applications
        if app.get('status') != 'applied'
    )

    rate = (responded / total * 100) if total > 0 else 0.0

    return MetricResponse(
        metric_name="response_rate",
        value=round(rate, 2),
        description="Percentage of applications that received a response"
    )


@router.get("/trends/weekly")
async def get_weekly_trends(
    user_id: str = Query(..., description="User ID to get trends for"),
    weeks: int = Query(4, ge=1, le=12, description="Number of weeks to include"),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get weekly application trends for the specified number of weeks.
    """
    applications = get_user_applications(db, user_id)
    start_date = datetime.utcnow() - timedelta(weeks=weeks)

    # Group by week
    weekly_counts = Counter()

    for app in applications:
        applied_at = app.get('applied_at')
        if applied_at:
            # Handle Firestore timestamp
            if hasattr(applied_at, 'timestamp'):
                app_date = datetime.fromtimestamp(applied_at.timestamp())
            else:
                app_date = applied_at

            if app_date >= start_date:
                # Get start of week (Monday)
                week_start = app_date - timedelta(days=app_date.weekday())
                week_str = week_start.strftime('%Y-%m-%d')
                weekly_counts[week_str] += 1

    return {
        "user_id": user_id,
        "weeks": weeks,
        "trends": [
            {"week": week, "applications": count}
            for week, count in sorted(weekly_counts.items())
        ]
    }


@router.get("/dashboard")
async def get_dashboard_stats(
    db: FirestoreClient = Depends(get_db),
):
    """
    Aggregated dashboard stats consumed by the Next.js DashboardPage.

    Unlike other analytics endpoints this does NOT require a user_id query param —
    the JWT dependency (added in a later sprint) will scope data per user.
    For now it returns global aggregates so the frontend renders real numbers.

    Response shape:
        {
          "totalApplications": int,
          "scheduledInterviews": int,
          "avgAtsScore": float | null,
          "offerRate": float | null
        }
    """
    try:
        # Pull all applications from Firestore
        apps = [d.to_dict() for d in db.collection("applications").stream()]

        total = len(apps)

        # Count applications where stage == "interviewing" as scheduled interviews
        interviews = sum(1 for a in apps if a.get("stage") == "interviewing")

        # Offer rate = offer / total * 100
        offers = sum(1 for a in apps if a.get("stage") == "offer")
        offer_rate = round(offers / total * 100, 1) if total > 0 else None

        # Average ATS score (from matchScore field if stored on applications)
        scores = [a["matchScore"] for a in apps if a.get("matchScore") is not None]
        avg_ats = round(sum(scores) / len(scores), 1) if scores else None

        return {
            "totalApplications": total,
            "scheduledInterviews": interviews,
            "avgAtsScore": avg_ats,
            "offerRate": offer_rate,
        }
    except Exception:
        # Firestore unavailable — return safe zeros so the UI still loads
        return {
            "totalApplications": 0,
            "scheduledInterviews": 0,
            "avgAtsScore": None,
            "offerRate": None,
        }
