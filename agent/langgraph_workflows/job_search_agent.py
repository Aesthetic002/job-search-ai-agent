"""
Job Search Agent - Finds and filters job listings based on user preferences.

This agent handles:
- Searching for jobs based on criteria (title, location, skills)
- Filtering and ranking job listings
- Job matching using semantic similarity
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import numpy as np


@dataclass
class JobListing:
    """Data class for job listing."""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    salary_range: Optional[str] = None
    source: str = "unknown"
    match_score: float = 0.0


class JobSearchAgent:
    """
    Agent responsible for searching and finding relevant job listings.
    Uses semantic similarity to match jobs with user preferences and skills.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """You are a job search specialist AI assistant.
Your role is to help users find relevant job opportunities based on their skills, experience, and preferences.

When analyzing job listings:
1. Match job requirements with user skills
2. Consider location preferences
3. Evaluate company culture fit
4. Assess career growth potential

Provide clear, actionable recommendations."""

    def create_search_query(self, user_preferences: Dict[str, Any]) -> str:
        """Generate an optimized search query from user preferences."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Based on these user preferences, create an optimized job search query:

Title/Role: {user_preferences.get('desired_role', 'Not specified')}
Skills: {', '.join(user_preferences.get('skills', []))}
Experience Level: {user_preferences.get('experience_level', 'Not specified')}
Location: {user_preferences.get('location', 'Remote')}
Industry: {user_preferences.get('industry', 'Any')}

Generate a concise, effective search query.""")
        ])

        response = self.llm.invoke(prompt.format_messages())
        return response.content

    def calculate_match_score(
        self,
        job_description: str,
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate semantic similarity score between job and user profile.
        Uses cosine similarity between embeddings.
        """
        # Create user profile text
        profile_text = f"""
        Role: {user_profile.get('desired_role', '')}
        Skills: {', '.join(user_profile.get('skills', []))}
        Experience: {user_profile.get('experience_level', '')}
        Summary: {user_profile.get('summary', '')}
        """

        # Get embeddings
        job_embedding = self.embeddings.embed_query(job_description)
        profile_embedding = self.embeddings.embed_query(profile_text)

        # Calculate cosine similarity
        job_vec = np.array(job_embedding)
        profile_vec = np.array(profile_embedding)

        similarity = np.dot(job_vec, profile_vec) / (
            np.linalg.norm(job_vec) * np.linalg.norm(profile_vec)
        )

        return float(similarity)

    def rank_jobs(
        self,
        jobs: List[JobListing],
        user_profile: Dict[str, Any]
    ) -> List[JobListing]:
        """Rank jobs by match score and return sorted list."""
        for job in jobs:
            job.match_score = self.calculate_match_score(
                job.description,
                user_profile
            )

        return sorted(jobs, key=lambda x: x.match_score, reverse=True)

    def analyze_job_fit(
        self,
        job: JobListing,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide detailed analysis of job fit for user."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Analyze this job's fit for the candidate:

JOB:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description: {job.description}
Requirements: {', '.join(job.requirements)}

CANDIDATE:
Desired Role: {user_profile.get('desired_role', 'Not specified')}
Skills: {', '.join(user_profile.get('skills', []))}
Experience: {user_profile.get('experience_level', 'Not specified')}

Provide:
1. Overall fit assessment (1-10)
2. Matching skills
3. Skill gaps
4. Recommendations for application""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company,
            "match_score": job.match_score,
            "analysis": response.content
        }

    def search(
        self,
        user_profile: Dict[str, Any],
        jobs: List[JobListing]
    ) -> Dict[str, Any]:
        """
        Main search function - filters and ranks jobs for user.

        Args:
            user_profile: User's skills, preferences, and experience
            jobs: List of available job listings

        Returns:
            Dictionary with ranked jobs and recommendations
        """
        # Rank jobs by match score
        ranked_jobs = self.rank_jobs(jobs, user_profile)

        # Get top matches (score > 0.7)
        top_matches = [j for j in ranked_jobs if j.match_score > 0.7][:10]

        # Analyze top 3 jobs
        detailed_analysis = []
        for job in top_matches[:3]:
            analysis = self.analyze_job_fit(job, user_profile)
            detailed_analysis.append(analysis)

        return {
            "total_jobs_found": len(jobs),
            "matching_jobs": len(top_matches),
            "top_matches": [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "match_score": round(j.match_score * 100, 1)
                }
                for j in top_matches
            ],
            "detailed_analysis": detailed_analysis
        }


def job_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for job search.

    Args:
        state: Current workflow state containing user_profile and jobs

    Returns:
        Updated state with search results
    """
    agent = JobSearchAgent()

    user_profile = state.get("user_profile", {})
    jobs = state.get("available_jobs", [])

    # Convert dict jobs to JobListing objects if needed
    job_listings = []
    for job in jobs:
        if isinstance(job, dict):
            job_listings.append(JobListing(
                id=job.get("id", ""),
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                description=job.get("description", ""),
                requirements=job.get("requirements", []),
                salary_range=job.get("salary_range"),
                source=job.get("source", "unknown")
            ))
        else:
            job_listings.append(job)

    results = agent.search(user_profile, job_listings)

    return {
        **state,
        "job_search_results": results,
        "current_agent": "job_search",
        "status": "job_search_complete"
    }
