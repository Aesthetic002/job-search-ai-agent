"""
AI Insights Router for Jobs Service
===================================
Provides LLM-generated market insights such as salary benchmarking and company research.
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
import sys, os

# Ensure agent can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agent.llm_provider import get_llm_with_fallback
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter(prefix="/insights", tags=["Insights"])

# ─── Pydantic Models for Structured Output ───

class SalaryBenchmark(BaseModel):
    min_lpa: float = Field(description="Minimum expected salary in Lakhs Per Annum (LPA)")
    mid_lpa: float = Field(description="Median expected salary in LPA")
    max_lpa: float = Field(description="Maximum expected salary in LPA")
    confidence: str = Field(description="High, Medium, or Low")
    summary: str = Field(description="A 2-sentence explanation of the market rate for this role and location")

class CompanyResearch(BaseModel):
    company_name: str = Field(description="The name of the company")
    culture_summary: str = Field(description="A brief summary of the company culture (2-3 sentences)")
    interview_process: str = Field(description="Typical interview rounds (e.g., '1. OA, 2. Technical, 3. HR')")
    pros: list[str] = Field(description="2-3 pros of working here")
    cons: list[str] = Field(description="2-3 cons of working here")

# ─── Prompts ───

SALARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert tech recruiter in India. Provide accurate salary benchmarking in Lakhs Per Annum (LPA)."),
    ("human", "What is the typical salary range for a {role} in {location}? Consider the current tech market in India.")
])

COMPANY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a knowledgeable career advisor. Provide a concise, objective summary of working at the requested company."),
    ("human", "Tell me about the company culture, interview process, and pros/cons for {company_name}.")
])

# ─── Routes ───

@router.get("/salary", response_model=SalaryBenchmark)
async def get_salary_benchmark(
    role: str = Query(..., description="Job role, e.g., 'Python Developer'"),
    location: str = Query(..., description="Location, e.g., 'Bangalore'"),
):
    """Get AI-estimated salary range (LPA) for a role + location."""
    try:
        result = get_llm_with_fallback(
            prompt_template=SALARY_PROMPT,
            output_schema=SalaryBenchmark,
            input_vars={"role": role, "location": location},
            temperature=0.2,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to generate insight: {str(e)}")

@router.get("/company", response_model=CompanyResearch)
async def get_company_research(
    name: str = Query(..., description="Company name, e.g., 'Infosys'"),
):
    """Get AI-generated company research (culture, interview process, pros/cons)."""
    try:
        result = get_llm_with_fallback(
            prompt_template=COMPANY_PROMPT,
            output_schema=CompanyResearch,
            input_vars={"company_name": name},
            temperature=0.2,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to generate insight: {str(e)}")
