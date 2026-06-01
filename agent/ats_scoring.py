"""
ATS Scoring Engine — Keyword matching and formatting checker against a Job Description.
Uses Groq (LLaMA 3.3 70B) via LangChain to produce a structured ATS report.
"""
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# ==================== PYDANTIC SCHEMAS ====================

class KeywordMatch(BaseModel):
    """A single keyword and whether it was found."""
    keyword: str = Field(description="The keyword or skill from the job description")
    found: bool = Field(description="Whether this keyword was found in the resume")
    context: Optional[str] = Field(None, description="Where in the resume it was found (optional short excerpt)")


class FormattingFeedback(BaseModel):
    """Feedback on the resume's formatting and structure."""
    has_clear_sections: bool = Field(description="Does the resume have clearly labeled sections?")
    has_quantified_achievements: bool = Field(description="Are there measurable achievements (e.g., 'increased by 40%')?")
    has_action_verbs: bool = Field(description="Does the resume use strong action verbs?")
    suggestions: List[str] = Field(default_factory=list, description="List of actionable formatting improvement tips")


class ATSScore(BaseModel):
    """Complete ATS evaluation report for a resume against a job description."""
    overall_score: int = Field(
        description="Overall ATS compatibility score from 0 to 100",
        ge=0, le=100
    )
    score_breakdown: dict = Field(
        description="Score breakdown by category. Keys: 'keyword_match' (0-50), 'experience_relevance' (0-30), 'formatting' (0-20)"
    )
    keyword_analysis: List[KeywordMatch] = Field(
        default_factory=list,
        description="Detailed analysis of each important keyword from the job description"
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Important keywords from the JD that are completely missing from the resume"
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords from the JD successfully found in the resume"
    )
    formatting_feedback: FormattingFeedback = Field(
        description="Structural and formatting quality assessment"
    )
    experience_relevance_summary: str = Field(
        description="Short paragraph evaluating how well the candidate's experience matches the role"
    )
    top_recommendations: List[str] = Field(
        default_factory=list,
        description="Top 3-5 prioritized, actionable recommendations to improve ATS score"
    )


# ==================== ATS SCORING ENGINE ====================

ATS_SCORE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert ATS (Applicant Tracking System) analyst and career coach.
Your task is to evaluate how well a candidate's resume matches a given job description.

Scoring Criteria:
- Keyword Match (0-50 points): Does the resume contain important technical skills, tools, and keywords from the JD?
- Experience Relevance (0-30 points): How closely does the candidate's work history match the role's requirements?
- Formatting Quality (0-20 points): Is the resume well-structured with clear sections, quantified achievements, and action verbs?

Be objective, specific, and provide genuinely actionable recommendations.
Do NOT just say "add more keywords" — be specific about WHICH keywords are missing and WHERE to add them."""
    ),
    (
        "human",
        """Please evaluate the following resume against the provided job description.

---JOB DESCRIPTION START---
{job_description}
---JOB DESCRIPTION END---

---RESUME TEXT START---
{resume_text}
---RESUME TEXT END---

Provide a complete, detailed ATS compatibility report."""
    )
])


def get_groq_llm(model: str = "llama-3.3-70b-versatile") -> ChatGroq:
    """Initialize the Groq LLM client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables.\n"
            "Get your free key at https://console.groq.com and add it to .env"
        )
    return ChatGroq(model=model, api_key=api_key, temperature=0)


def score_resume_against_jd(resume_text: str, job_description: str) -> ATSScore:
    """
    Score a resume against a job description using LLM-powered ATS analysis.

    Args:
        resume_text: Raw text content of the candidate's resume.
        job_description: The full job description text to match against.

    Returns:
        ATSScore: Pydantic model with detailed ATS scoring report.

    Raises:
        ValueError: If inputs are empty or GROQ_API_KEY is missing.
        Exception: If LLM call fails.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    llm = get_groq_llm()
    structured_llm = llm.with_structured_output(ATSScore)
    chain = ATS_SCORE_PROMPT | structured_llm

    result: ATSScore = chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description
    })
    return result


def score_resume_to_dict(resume_text: str, job_description: str) -> dict:
    """
    Score a resume against a JD and return a plain dictionary (for API responses).

    Args:
        resume_text: Raw text content of the resume.
        job_description: Job description to score against.

    Returns:
        dict: Serialized ATSScore as a JSON-compatible dictionary.
    """
    score = score_resume_against_jd(resume_text, job_description)
    return score.model_dump()


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    sample_resume = """
    John Doe | john.doe@email.com | Bangalore, India
    Software Engineer at Infosys (2022-Present)
    - Built RESTful APIs using FastAPI and Python
    - React dashboards, PostgreSQL, Docker
    Skills: Python, FastAPI, React, PostgreSQL, Docker, Git
    B.Tech Computer Science, IIT Bombay 2022
    """

    sample_jd = """
    We are looking for a Backend Engineer with:
    - 2+ years of experience with Python and FastAPI or Django
    - Experience with cloud platforms (AWS or Azure)
    - Strong knowledge of databases: PostgreSQL or MongoDB
    - Experience with Docker and Kubernetes
    - Familiarity with CI/CD pipelines (GitHub Actions or Jenkins)
    - Good communication skills and ability to work in an agile team
    """

    print("Scoring resume against job description...")
    result = score_resume_to_dict(sample_resume, sample_jd)
    import json
    print(json.dumps(result, indent=2))
