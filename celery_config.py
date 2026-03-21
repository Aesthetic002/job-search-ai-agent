"""
Celery Configuration for Job Search AI Agent.

Configures Celery for background task processing including:
- Job search tasks
- Resume processing
- Email notifications
- Analytics aggregation
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Broker settings (Redis)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

broker_url = REDIS_URL
result_backend = REDIS_URL

# Task settings
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True

# Task result settings
result_expires = 3600  # Results expire after 1 hour

# Worker settings
worker_prefetch_multiplier = 1
worker_concurrency = 4

# Task routing
task_routes = {
    "celery_worker.search_jobs_task": {"queue": "job_search"},
    "celery_worker.process_resume_task": {"queue": "resume"},
    "celery_worker.send_notification_task": {"queue": "notifications"},
    "celery_worker.aggregate_analytics_task": {"queue": "analytics"},
}

# Task queue definitions
task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    },
    "job_search": {
        "exchange": "job_search",
        "routing_key": "job_search",
    },
    "resume": {
        "exchange": "resume",
        "routing_key": "resume",
    },
    "notifications": {
        "exchange": "notifications",
        "routing_key": "notifications",
    },
    "analytics": {
        "exchange": "analytics",
        "routing_key": "analytics",
    },
}

# Beat schedule for periodic tasks
beat_schedule = {
    "aggregate-daily-analytics": {
        "task": "celery_worker.aggregate_analytics_task",
        "schedule": 86400.0,  # Daily (24 hours)
        "args": ("daily",),
    },
    "cleanup-expired-sessions": {
        "task": "celery_worker.cleanup_sessions_task",
        "schedule": 3600.0,  # Hourly
    },
}

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True

# Rate limiting
task_annotations = {
    "celery_worker.search_jobs_task": {
        "rate_limit": "10/m"  # Max 10 job searches per minute
    },
    "celery_worker.send_notification_task": {
        "rate_limit": "100/m"  # Max 100 notifications per minute
    },
}
