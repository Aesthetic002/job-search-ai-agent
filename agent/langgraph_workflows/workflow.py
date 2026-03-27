"""
Main LangGraph Workflow - Orchestrates all agents in the job search pipeline.

This module defines the complete workflow that connects:
Job Search Agent → Resume Agent → Interview Agent → Career Advisor
"""
import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from enum import Enum
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .job_search_agent import job_search_node
from .resume_agent import resume_node
from .interview_agent import interview_node
from .career_advisor import career_advisor_node


class WorkflowStage(str, Enum):
    """Stages in the job search workflow."""
    JOB_SEARCH = "job_search"
    RESUME = "resume"
    INTERVIEW = "interview"
    CAREER_ADVICE = "career_advice"
    COMPLETE = "complete"


class JobSearchState(TypedDict, total=False):
    """Type definition for workflow state."""
    # User information
    user_id: str
    user_profile: Dict[str, Any]

    # Resume data
    resume: Dict[str, Any]
    resume_results: Dict[str, Any]

    # Job search data
    available_jobs: List[Dict[str, Any]]
    job_search_results: Dict[str, Any]
    target_job: Dict[str, Any]

    # Interview data
    interview_mode: str
    interview_results: Dict[str, Any]
    answer_to_evaluate: Dict[str, Any]

    # Career advice data
    advice_type: str
    career_advice: Dict[str, Any]

    # Workflow control
    current_agent: str
    status: str
    error: Optional[str]
    next_stage: str


def should_continue_to_resume(state: JobSearchState) -> str:
    """Determine if workflow should continue to resume stage."""
    if state.get("job_search_results", {}).get("matching_jobs", 0) > 0:
        return "resume"
    return "end"


def should_continue_to_interview(state: JobSearchState) -> str:
    """Determine if workflow should continue to interview stage."""
    resume_results = state.get("resume_results", {})
    if resume_results.get("status") in ["analyzed", "tailored"]:
        return "interview"
    return "end"


def should_continue_to_career(state: JobSearchState) -> str:
    """Determine if workflow should continue to career advice stage."""
    interview_results = state.get("interview_results", {})
    if interview_results.get("status") == "ready_to_start":
        return "career_advice"
    return "end"


def route_by_stage(state: JobSearchState) -> str:
    """Route to next stage based on current state."""
    next_stage = state.get("next_stage", "job_search")

    if next_stage == "job_search":
        return "job_search"
    elif next_stage == "resume":
        return "resume"
    elif next_stage == "interview":
        return "interview"
    elif next_stage == "career_advice":
        return "career_advice"
    else:
        return END


def entry_node(state: JobSearchState) -> JobSearchState:
    """Entry node to initialize workflow."""
    return {
        **state,
        "status": "started",
        "current_agent": "entry"
    }


def create_job_search_workflow(
    checkpointer: Optional[MemorySaver] = None
) -> StateGraph:
    """
    Create the complete job search workflow graph.

    The workflow follows this pipeline:
    1. Job Search - Find matching jobs
    2. Resume - Tailor resume for target job
    3. Interview - Prepare for interviews
    4. Career Advice - Get career guidance

    Args:
        checkpointer: Optional memory saver for state persistence

    Returns:
        Compiled StateGraph workflow
    """
    # Create the graph
    workflow = StateGraph(JobSearchState)

    # Add nodes
    workflow.add_node("entry", entry_node)
    workflow.add_node("job_search", job_search_node)
    workflow.add_node("resume", resume_node)
    workflow.add_node("interview", interview_node)
    workflow.add_node("career_advice", career_advisor_node)

    # Set entry point
    workflow.set_entry_point("entry")

    # Add edges
    workflow.add_edge("entry", "job_search")

    # Conditional edges based on results
    workflow.add_conditional_edges(
        "job_search",
        should_continue_to_resume,
        {
            "resume": "resume",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "resume",
        should_continue_to_interview,
        {
            "interview": "interview",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "interview",
        should_continue_to_career,
        {
            "career_advice": "career_advice",
            "end": END
        }
    )

    workflow.add_edge("career_advice", END)

    # Compile the graph
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)

    return workflow.compile()


def create_single_agent_workflow(agent_type: str) -> StateGraph:
    """
    Create a workflow for a single agent.

    Useful for running individual agents without the full pipeline.

    Args:
        agent_type: One of "job_search", "resume", "interview", "career_advice"

    Returns:
        Compiled StateGraph for single agent
    """
    workflow = StateGraph(JobSearchState)

    node_map = {
        "job_search": job_search_node,
        "resume": resume_node,
        "interview": interview_node,
        "career_advice": career_advisor_node
    }

    if agent_type not in node_map:
        raise ValueError(f"Unknown agent type: {agent_type}")

    workflow.add_node(agent_type, node_map[agent_type])
    workflow.set_entry_point(agent_type)
    workflow.add_edge(agent_type, END)

    return workflow.compile()


# Example usage
if __name__ == "__main__":
    # Create the full workflow
    app = create_job_search_workflow()

    # Example initial state
    initial_state = {
        "user_id": "user123",
        "user_profile": {
            "desired_role": "Software Engineer",
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "experience_level": "Mid-level",
            "location": "Remote",
            "industry": "Technology"
        },
        "resume": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "summary": "Experienced software developer...",
            "experience": [],
            "education": [],
            "skills": ["Python", "JavaScript"],
            "certifications": []
        },
        "available_jobs": [],
        "next_stage": "job_search"
    }

    # Run the workflow
    # result = app.invoke(initial_state)
    # print(result)
