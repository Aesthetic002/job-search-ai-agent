"""
Interview Service (Port 8004)
FastAPI microservice for AI-powered mock interviews.

Endpoints:
  POST /interview/generate  — Generate tailored interview questions
  POST /interview/evaluate  — Evaluate a candidate's answer with AI scoring
  GET  /interview/categories — List question categories and difficulty levels
  GET  /interview/health    — Health check

Powered by Groq (LLaMA 3.3 70B) via LangChain.
"""
import os
import sys
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Fix import paths so agent/ modules are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.interview_evaluator import evaluate_answer_to_dict
from agent.llm_provider import get_llm_with_fallback, list_configured_providers
from .negotiation_routes import router as negotiation_router



app = FastAPI(
    title="Interview Service",
    description="AI-powered mock interview question generator and answer evaluator.",
    version="2.0.0"
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(negotiation_router)

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


class EvaluateAnswerRequest(BaseModel):
    """Request model for evaluating a candidate's interview answer."""
    question: str = Field(..., description="The interview question that was asked")
    candidate_answer: str = Field(..., min_length=10, description="The candidate's answer text")
    job_title: str = Field(..., description="Target job title e.g. 'Backend Engineer'")
    category: Optional[str] = Field(
        "General",
        description="Question category: 'Technical', 'Behavioral', 'Situational', 'Role-Specific', or 'General'"
    )
    expected_topics: Optional[List[str]] = Field(
        default_factory=list,
        description="Key topics the answer should cover (from the question generator's expected_topics field)"
    )


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



# ==================== ROUTES ====================

@app.get("/")
def root():
    return {
        "message": "Interview Service Running",
        "version": "2.0.0",
        "endpoints": {
            "generate": "POST /interview/generate",
            "evaluate": "POST /interview/evaluate",
            "categories": "GET /interview/categories",
            "health": "GET /interview/health",
        }
    }


@app.get("/interview/health")
def health_check():
    """Health check — verifies the service is running and which LLM providers are configured."""
    providers = list_configured_providers()
    return {
        "status": "healthy" if providers else "degraded",
        "configured_providers": providers,
        "primary_provider": providers[0] if providers else None,
        "total_providers": len(providers),
    }


@app.post("/interview/generate", response_model=InterviewQuestionBank)
async def generate_interview_questions(request: GenerateInterviewRequest):
    """
    Generate AI-powered mock interview questions tailored to a candidate's resume and target role.
    Uses the best available free LLM provider with automatic fallback.

    - Accepts a job title, resume text, and optional job description.
    - Returns 8-10 questions across Technical, Behavioral, and Situational categories.
    - Each question includes difficulty, category, and preparation hints.
    """
    try:
        result: InterviewQuestionBank = get_llm_with_fallback(
            prompt_template=INTERVIEW_PROMPT,
            output_schema=InterviewQuestionBank,
            input_vars={
                "job_title": request.job_title,
                "resume_summary": request.resume_summary,
                "job_description": request.job_description or "Not provided",
                "num_questions": request.num_questions,
            },
            temperature=0.7,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview question generation failed: {str(e)}"
        )


@app.post("/interview/evaluate")
async def evaluate_interview_answer(request: EvaluateAnswerRequest):
    """
    Evaluate a candidate's answer to a mock interview question using AI.

    - Scores the answer from 0–100 with a 'Excellent / Good / Average / Needs Improvement' verdict.
    - Identifies specific strengths and actionable improvement areas.
    - Flags any expected topics/concepts that were missed.
    - Provides a concise ideal answer summary for comparison.
    - For Behavioral questions: checks STAR method compliance (Situation, Task, Action, Result).
    - Gives feedback on communication quality and answer structure.
    """
    try:
        evaluation = evaluate_answer_to_dict(
            question=request.question,
            candidate_answer=request.candidate_answer,
            job_title=request.job_title,
            category=request.category or "General",
            expected_topics=request.expected_topics or [],
        )
    except RuntimeError as e:
        # Missing API key
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Answer evaluation failed: {str(e)}"
        )

    return {
        "message": "Answer evaluated successfully",
        "job_title": request.job_title,
        "question": request.question,
        "category": request.category,
        "evaluation": evaluation,
    }


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
