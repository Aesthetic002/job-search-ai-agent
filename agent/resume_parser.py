"""
Resume Parser — AI-powered structured data extraction from raw resume text.
Uses the unified LLM provider (Groq -> OpenRouter -> NVIDIA NIM -> Gemini -> Cohere)
for automatic fallback if any provider is rate-limited or unavailable.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from agent.llm_provider import get_llm_with_fallback

load_dotenv()

# ==================== PYDANTIC SCHEMAS ====================

class ContactInfo(BaseModel):
    """Contact information extracted from the resume."""
    full_name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State or Country")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio or personal website URL")


class EducationEntry(BaseModel):
    """A single education entry."""
    institution: Optional[str] = Field(None, description="Name of the university or college")
    degree: Optional[str] = Field(None, description="Degree obtained e.g. B.Tech, M.Sc")
    field_of_study: Optional[str] = Field(None, description="Major or field of study e.g. Computer Science")
    start_year: Optional[str] = Field(None, description="Year studies began")
    end_year: Optional[str] = Field(None, description="Year of graduation or expected graduation")
    gpa: Optional[str] = Field(None, description="GPA or percentage if mentioned")


class ExperienceEntry(BaseModel):
    """A single work experience entry."""
    company: Optional[str] = Field(None, description="Company or organization name")
    role: Optional[str] = Field(None, description="Job title or position held")
    start_date: Optional[str] = Field(None, description="Start date e.g. Jan 2022")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    description: Optional[str] = Field(None, description="Brief summary of responsibilities and achievements")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies or tools mentioned in this role")


class SkillsInfo(BaseModel):
    """Skills extracted from the resume."""
    technical_skills: Optional[List[str]] = Field(default_factory=list, description="Programming languages, frameworks, databases, tools")
    soft_skills: Optional[List[str]] = Field(default_factory=list, description="Communication, leadership, teamwork etc.")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Any certifications or licenses")
    languages: Optional[List[str]] = Field(default_factory=list, description="Human languages spoken e.g. English, Hindi")


class ParsedResume(BaseModel):
    """Top-level structured resume data extracted by the AI."""
    contact: ContactInfo = Field(description="Contact information of the candidate")
    education: List[EducationEntry] = Field(default_factory=list, description="All education entries")
    experience: List[ExperienceEntry] = Field(default_factory=list, description="All work experience entries")
    skills: SkillsInfo = Field(description="Technical and soft skills")
    summary: Optional[str] = Field(None, description="Professional summary or objective from the resume")


# ==================== PARSER ENGINE ====================

RESUME_PARSE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert AI recruiter and resume parser. 
Your task is to extract structured information from the raw text of a resume.
Be as accurate and thorough as possible. Extract ALL entries for education and experience.
If a field is not present in the resume, return null for that field.
Do not invent or assume any information not present in the text."""
    ),
    (
        "human",
        """Please parse the following resume text and extract all structured information:

---RESUME TEXT START---
{resume_text}
---RESUME TEXT END---

Extract all contact info, education history, work experience, and skills."""
    )
])


def parse_resume(resume_text: str) -> ParsedResume:
    """
    Parse raw resume text into a structured ParsedResume object.
    Uses the best available free LLM provider with automatic fallback.

    Args:
        resume_text: Raw text content extracted from a PDF/DOCX resume.

    Returns:
        ParsedResume: Pydantic model containing all structured resume fields.

    Raises:
        ValueError: If resume_text is empty.
        RuntimeError: If all LLM providers fail.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")

    result: ParsedResume = get_llm_with_fallback(
        prompt_template=RESUME_PARSE_PROMPT,
        output_schema=ParsedResume,
        input_vars={"resume_text": resume_text},
        temperature=0.0,
    )
    return result


def parse_resume_to_dict(resume_text: str) -> dict:
    """
    Parse raw resume text and return a plain dictionary (for Firestore storage).

    Args:
        resume_text: Raw text content of the resume.

    Returns:
        dict: Serialized ParsedResume as a JSON-compatible dictionary.
    """
    parsed = parse_resume(resume_text)
    return parsed.model_dump()


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    sample_resume = """
    John Doe
    john.doe@email.com | +91-9876543210 | Bangalore, India
    linkedin.com/in/johndoe | github.com/johndoe

    SUMMARY
    Software Engineer with 3 years of experience building scalable web applications
    using Python and React. Passionate about AI and machine learning.

    EDUCATION
    Indian Institute of Technology, Bombay
    B.Tech in Computer Science | 2018 - 2022 | GPA: 8.5/10

    EXPERIENCE
    Software Engineer — Infosys, Bangalore
    July 2022 - Present
    - Developed RESTful APIs using FastAPI and Python
    - Built React dashboards consuming internal microservices
    - Optimized Postgres queries reducing load time by 40%
    Technologies: Python, FastAPI, React, PostgreSQL, Docker

    Intern — Tata Consultancy Services
    May 2021 - July 2021
    - Automated data extraction from legacy Excel reports using Pandas
    Technologies: Python, Pandas, Excel

    SKILLS
    Technical: Python, FastAPI, React, JavaScript, PostgreSQL, Docker, Git, Redis
    Soft Skills: Problem Solving, Team Collaboration, Communication
    Certifications: AWS Cloud Practitioner
    Languages: English, Hindi
    """

    print("Parsing sample resume...")
    result = parse_resume_to_dict(sample_resume)
    import json
    print(json.dumps(result, indent=2))
