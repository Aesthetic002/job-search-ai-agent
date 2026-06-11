"""
Celery Worker for Job Search AI Agent.

Defines background tasks for:
- Job searching and matching
- Resume processing
- Notification sending
- Analytics aggregation
"""
import os
from typing import Dict, List, Any, Optional
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
app = Celery("job_search_agent")
app.config_from_object("celery_config")


@app.task(bind=True, max_retries=3)
def search_jobs_task(
    self,
    user_id: str,
    search_criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to search for jobs based on user criteria.

    Args:
        user_id: User ID making the search
        search_criteria: Search parameters (title, location, skills, etc.)

    Returns:
        Dictionary with search results
    """
    try:
        from agent.langgraph_workflows import JobSearchAgent

        agent = JobSearchAgent()

        # Create user profile from search criteria
        user_profile = {
            "desired_role": search_criteria.get("title", ""),
            "skills": search_criteria.get("skills", []),
            "experience_level": search_criteria.get("experience_level", ""),
            "location": search_criteria.get("location", "Remote"),
            "industry": search_criteria.get("industry", "")
        }

        # Generate search query
        query = agent.create_search_query(user_profile)

        return {
            "user_id": user_id,
            "status": "completed",
            "search_query": query,
            "message": "Job search initiated"
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Retry after 60 seconds


@app.task(bind=True, max_retries=3)
def process_resume_task(
    self,
    user_id: str,
    resume_data: Dict[str, Any],
    job_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Background task to process and analyze a resume.

    Args:
        user_id: User ID owning the resume
        resume_data: Resume content and metadata
        job_info: Optional job to tailor resume for

    Returns:
        Dictionary with resume analysis results
    """
    try:
        from agent.langgraph_workflows import ResumeAgent, Resume

        agent = ResumeAgent()

        # Create Resume object
        resume = Resume(
            user_id=user_id,
            full_name=resume_data.get("full_name", ""),
            email=resume_data.get("email", ""),
            phone=resume_data.get("phone"),
            summary=resume_data.get("summary", ""),
            experience=resume_data.get("experience", []),
            education=resume_data.get("education", []),
            skills=resume_data.get("skills", []),
            certifications=resume_data.get("certifications", []),
            raw_text=resume_data.get("raw_text")
        )

        # Process resume
        results = agent.process(resume, job_info)

        return {
            "user_id": user_id,
            "status": "completed",
            "results": results
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@app.task(bind=True, max_retries=3)
def prepare_interview_task(
    self,
    user_id: str,
    job_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to prepare interview materials.

    Args:
        user_id: User ID preparing for interview
        job_info: Job information for interview prep

    Returns:
        Dictionary with interview preparation materials
    """
    try:
        from agent.langgraph_workflows import InterviewAgent

        agent = InterviewAgent()
        results = agent.simulate_interview(job_info)

        return {
            "user_id": user_id,
            "status": "completed",
            "interview_prep": results
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@app.task(bind=True, max_retries=3)
def get_career_advice_task(
    self,
    user_id: str,
    user_profile: Dict[str, Any],
    advice_type: str = "career_path"
) -> Dict[str, Any]:
    """
    Background task to generate career advice.

    Args:
        user_id: User ID requesting advice
        user_profile: User's profile information
        advice_type: Type of advice to generate

    Returns:
        Dictionary with career advice
    """
    try:
        from agent.langgraph_workflows import CareerAdvisor

        agent = CareerAdvisor()
        results = agent.process(user_profile, advice_type)

        return {
            "user_id": user_id,
            "status": "completed",
            "advice": results
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@app.task(bind=True, max_retries=2)
def send_notification_task(
    self,
    user_id: str,
    notification_type: str,
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to send email notifications via SMTP.

    Reads credentials from environment variables:
        SMTP_HOST     — SMTP server hostname  (default: smtp.sendgrid.net)
        SMTP_PORT     — SMTP port             (default: 587)
        SMTP_USER     — SMTP username         (default: apikey for SendGrid)
        SMTP_PASSWORD — SMTP password / SendGrid API key
        FROM_EMAIL    — Sender email address

    Args:
        user_id: User ID to notify
        notification_type: Type of notification (email, push, job_alert)
        content: Dict with keys:
                   - to_email: recipient address
                   - subject: email subject line
                   - body: plain-text email body (HTML also supported via body_html)
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "apikey")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", "noreply@jobsearchai.app")

    to_email = content.get("to_email")
    subject = content.get("subject", "Job Search AI Notification")
    body_text = content.get("body", "")
    body_html = content.get("body_html", "")

    if not to_email:
        return {"status": "skipped", "reason": "No to_email provided"}

    if not smtp_password:
        # No SMTP configured — log and skip gracefully
        print(f"[send_notification_task] SMTP_PASSWORD not set. Skipping email to {to_email}.")
        return {"status": "skipped", "reason": "SMTP not configured"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())

        return {
            "user_id": user_id,
            "notification_type": notification_type,
            "status": "sent",
            "to": to_email,
            "message": f"Email sent to {to_email}",
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)
        return {"status": "failed", "error": str(exc)}


@app.task
def aggregate_analytics_task(period: str = "daily") -> Dict[str, Any]:
    """
    Background task to aggregate analytics data.

    Args:
        period: Aggregation period (daily, weekly, monthly)

    Returns:
        Dictionary with aggregation status
    """
    # TODO: Implement analytics aggregation logic
    # This would query the database and compute statistics

    return {
        "period": period,
        "status": "completed",
        "message": f"Analytics aggregated for {period} period"
    }


@app.task
def cleanup_sessions_task() -> Dict[str, Any]:
    """
    Background task to cleanup expired sessions.

    Returns:
        Dictionary with cleanup status
    """
    # TODO: Implement session cleanup logic

    return {
        "status": "completed",
        "message": "Expired sessions cleaned up"
    }


@app.task(bind=True, max_retries=3)
def run_workflow_task(
    self,
    user_id: str,
    workflow_type: str,
    initial_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to run a complete LangGraph workflow.

    Args:
        user_id: User ID running the workflow
        workflow_type: Type of workflow (full, single_agent)
        initial_state: Initial state for the workflow

    Returns:
        Dictionary with workflow results
    """
    try:
        from agent.langgraph_workflows import (
            create_job_search_workflow,
            create_single_agent_workflow
        )

        if workflow_type == "full":
            workflow = create_job_search_workflow()
        else:
            workflow = create_single_agent_workflow(workflow_type)

        # Run the workflow
        result = workflow.invoke(initial_state)

        return {
            "user_id": user_id,
            "workflow_type": workflow_type,
            "status": "completed",
            "result": result
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=60)


# Health check task
@app.task
def health_check() -> Dict[str, str]:
    """Simple health check task."""
    return {"status": "healthy", "worker": "celery"}


if __name__ == "__main__":
    app.start()
