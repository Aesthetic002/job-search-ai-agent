"""
Resume Agent - Tailors and optimizes resumes for specific job applications.

This agent handles:
- Analyzing resume content
- Tailoring resume for specific job descriptions
- Suggesting improvements and keyword optimization
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


@dataclass
class ResumeSection:
    """Data class for resume section."""
    name: str
    content: str
    keywords: List[str]


@dataclass
class Resume:
    """Data class for complete resume."""
    user_id: str
    full_name: str
    email: str
    phone: Optional[str]
    summary: str
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[str]
    raw_text: Optional[str] = None


class ResumeAgent:
    """
    Agent responsible for resume analysis and optimization.
    Tailors resumes to match specific job descriptions.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.4,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """You are an expert resume writer and career consultant.
Your role is to help candidates optimize their resumes for specific job applications.

Key principles:
1. Tailor content to match job requirements
2. Use action verbs and quantifiable achievements
3. Optimize for ATS (Applicant Tracking Systems)
4. Highlight relevant skills and experience
5. Maintain professional tone and formatting

Provide specific, actionable suggestions."""

    def analyze_resume(self, resume: Resume) -> Dict[str, Any]:
        """Analyze resume content and provide assessment."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Analyze this resume and provide a comprehensive assessment:

NAME: {resume.full_name}

SUMMARY:
{resume.summary}

EXPERIENCE:
{self._format_experience(resume.experience)}

EDUCATION:
{self._format_education(resume.education)}

SKILLS:
{', '.join(resume.skills)}

CERTIFICATIONS:
{', '.join(resume.certifications) if resume.certifications else 'None listed'}

Provide:
1. Overall strength rating (1-10)
2. Key strengths
3. Areas for improvement
4. Missing elements
5. ATS optimization tips""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "analysis": response.content,
            "skills_count": len(resume.skills),
            "experience_count": len(resume.experience)
        }

    def tailor_for_job(
        self,
        resume: Resume,
        job_description: str,
        job_title: str,
        company: str
    ) -> Dict[str, Any]:
        """Tailor resume for a specific job application."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Tailor this resume for the following job:

TARGET JOB:
Title: {job_title}
Company: {company}
Description: {job_description}

CURRENT RESUME:
Name: {resume.full_name}
Summary: {resume.summary}
Experience: {self._format_experience(resume.experience)}
Skills: {', '.join(resume.skills)}

Provide:
1. Tailored summary statement
2. Skills to emphasize (from existing skills)
3. Skills to add/highlight
4. Experience bullet points to modify
5. Keywords to include for ATS
6. Overall recommendations""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "job_title": job_title,
            "company": company,
            "tailoring_suggestions": response.content
        }

    def suggest_keywords(
        self,
        resume: Resume,
        job_description: str
    ) -> Dict[str, Any]:
        """Extract and suggest keywords for ATS optimization."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Compare this resume against the job description and identify keyword gaps:

JOB DESCRIPTION:
{job_description}

RESUME SKILLS:
{', '.join(resume.skills)}

RESUME SUMMARY:
{resume.summary}

Provide:
1. Keywords present in job but missing from resume
2. Keywords already matching
3. Suggested phrases to add
4. Priority keywords (most important for ATS)""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "keyword_analysis": response.content,
            "current_skills": resume.skills
        }

    def generate_summary(
        self,
        resume: Resume,
        target_role: str
    ) -> str:
        """Generate a professional summary tailored to target role."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Generate a compelling professional summary for this candidate targeting {target_role}:

Current Summary: {resume.summary}
Experience: {self._format_experience(resume.experience[:2])}  # Top 2 experiences
Skills: {', '.join(resume.skills[:10])}

Generate a 3-4 sentence professional summary that:
1. Highlights years of relevant experience
2. Mentions key skills
3. Shows value proposition
4. Is tailored for {target_role}""")
        ])

        response = self.llm.invoke(prompt.format_messages())
        return response.content

    def optimize_bullet_points(
        self,
        bullet_points: List[str],
        target_keywords: List[str]
    ) -> List[str]:
        """Optimize experience bullet points with action verbs and metrics."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Optimize these resume bullet points:

ORIGINAL BULLETS:
{chr(10).join(f'- {bp}' for bp in bullet_points)}

TARGET KEYWORDS TO INCLUDE:
{', '.join(target_keywords)}

Rewrite each bullet point to:
1. Start with a strong action verb
2. Include quantifiable metrics where possible
3. Incorporate relevant keywords naturally
4. Be concise (under 2 lines)

Return the optimized bullet points.""")
        ])

        response = self.llm.invoke(prompt.format_messages())
        return response.content

    def _format_experience(self, experience: List[Dict[str, Any]]) -> str:
        """Format experience list for prompt."""
        formatted = []
        for exp in experience:
            formatted.append(f"""
Role: {exp.get('title', 'N/A')}
Company: {exp.get('company', 'N/A')}
Duration: {exp.get('duration', 'N/A')}
Highlights: {', '.join(exp.get('highlights', []))}
""")
        return "\n".join(formatted)

    def _format_education(self, education: List[Dict[str, Any]]) -> str:
        """Format education list for prompt."""
        formatted = []
        for edu in education:
            formatted.append(f"""
Degree: {edu.get('degree', 'N/A')}
Institution: {edu.get('institution', 'N/A')}
Year: {edu.get('year', 'N/A')}
""")
        return "\n".join(formatted)

    def process(
        self,
        resume: Resume,
        job_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main processing function for resume agent.

        Args:
            resume: Resume object to analyze/optimize
            job_info: Optional job info for tailoring

        Returns:
            Dictionary with analysis and suggestions
        """
        # Base analysis
        analysis = self.analyze_resume(resume)

        result = {
            "resume_analysis": analysis,
            "status": "analyzed"
        }

        # If job info provided, tailor the resume
        if job_info:
            tailoring = self.tailor_for_job(
                resume,
                job_info.get("description", ""),
                job_info.get("title", ""),
                job_info.get("company", "")
            )
            keywords = self.suggest_keywords(
                resume,
                job_info.get("description", "")
            )

            result["tailoring_suggestions"] = tailoring
            result["keyword_suggestions"] = keywords
            result["status"] = "tailored"

        return result


def resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for resume processing.

    Args:
        state: Current workflow state containing resume and job info

    Returns:
        Updated state with resume analysis and suggestions
    """
    agent = ResumeAgent()

    resume_data = state.get("resume", {})
    job_info = state.get("target_job")

    # Convert dict to Resume object if needed
    if isinstance(resume_data, dict):
        resume = Resume(
            user_id=resume_data.get("user_id", ""),
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
    else:
        resume = resume_data

    results = agent.process(resume, job_info)

    return {
        **state,
        "resume_results": results,
        "current_agent": "resume",
        "status": "resume_complete"
    }
