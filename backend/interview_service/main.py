"""
Interview Service (Port 8004)
FastAPI microservice for generating AI-powered mock interview questions.
Uses Groq (LLaMA 3.3 70B) to tailor questions based on the candidate's resume and target role.
"""
import os
import sys
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Depends
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Fix import paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

app = FastAPI(
    title="Interview Service",
    description="AI-powered mock interview question generator",
    version="1.0.0"
)

# ==================== PYDANTIC SCHEMAS ====================

class InterviewQuestion(BaseModel):
    """A single interview question with metadata."""
    question: str = Field(description="The interview question text")
    category: str = Field(description="Category: 'Technical', 'Behavioral', 'Situational', or 'Role-Specific'")
    difficulty: str = Field(description="Difficulty level: 'Easy', 'Medium', or 'Hard'")
    hint: Optional[str] = Field(None, description="A brief tip on how to approach answering this question")
    expected_topics: Optional[List[str]] = Field(
        default_factory=list,
        description="Key topics or concepts the answer should cover"
    )


class InterviewQuestionBank(BaseModel):
    """A complete set of tailored mock interview questions."""
    job_title: str = Field(description="The job role these questions are tailored for")
    questions: List[InterviewQuestion] = Field(description="List of 8-10 tailored interview questions")
    preparation_tips: List[str] = Field(
        default_factory=list,
        description="3-5 general preparation tips for this specific role and candidate"
    )


class GenerateInterviewRequest(BaseModel):
    """Request model for generating interview questions."""
    job_title: str = Field(..., description="Target job title e.g. 'Backend Engineer at Google'")
    resume_summary: str = Field(..., description="Raw resume text or structured resume summary")
    job_description: Optional[str] = Field(None, description="Job description (optional but recommended)")
    num_questions: Optional[int] = Field(8, ge=3, le=15, description="Number of questions to generate (3-15)")


# ==================== LLM ENGINE ====================

INTERVIEW_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert technical interviewer and career coach at a top tech company.
Your task is to generate highly tailored, realistic mock interview questions for a candidate.

Rules:
1. Mix question types: Technical (specific to their stack), Behavioral (STAR method), and Role-Specific (company/industry context).
2. Base technical questions on the candidate's actual skills from their resume — don't ask about things they haven't used.
3. Include at least 2 questions about gaps or weaknesses implied by the resume vs the job requirements.
4. Make questions realistic — these should feel like actual interview questions at top companies.
5. Provide a hint for each question to help the candidate prepare."""
    ),
    (
        "human",
        """Generate {num_questions} mock interview questions for the following candidate and role.

Target Role: {job_title}

Candidate Resume:
{resume_summary}

Job Description (if provided):
{job_description}

Generate a diverse set of interview questions tailored specifically to this candidate."""
    )
])


def get_groq_llm() -> ChatGroq:
    """Initialize the Groq LLM client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY not configured. Add it to your .env file."
        )
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0.7)


# ==================== ROUTES ====================

@app.get("/")
def root():
    return {"message": "Interview Service Running", "version": "1.0.0"}


@app.post("/interview/generate", response_model=InterviewQuestionBank)
async def generate_interview_questions(request: GenerateInterviewRequest):
    """
    Generate AI-powered mock interview questions tailored to a candidate's resume and target role.

    - Accepts a job title, resume text, and optional job description.
    - Returns 8-10 questions across Technical, Behavioral, and Situational categories.
    - Each question includes difficulty, category, and preparation hints.
    """
    llm = get_groq_llm()
    structured_llm = llm.with_structured_output(InterviewQuestionBank)
    chain = INTERVIEW_PROMPT | structured_llm

    try:
        result: InterviewQuestionBank = chain.invoke({
            "job_title": request.job_title,
            "resume_summary": request.resume_summary,
            "job_description": request.job_description or "Not provided",
            "num_questions": request.num_questions
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview question generation failed: {str(e)}"
        )


@app.get("/interview/categories")
def get_question_categories():
    """Return available question categories and difficulty levels."""
    return {
        "categories": ["Technical", "Behavioral", "Situational", "Role-Specific"],
        "difficulty_levels": ["Easy", "Medium", "Hard"],
        "description": {
            "Technical": "Tests specific programming and domain knowledge",
            "Behavioral": "Uses STAR method to assess past experience and soft skills",
            "Situational": "Hypothetical scenarios to test decision-making",
            "Role-Specific": "Industry or company context questions"
        }
    }
