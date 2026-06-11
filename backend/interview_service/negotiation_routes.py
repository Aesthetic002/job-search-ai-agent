"""
Salary Negotiation Chatbot Router
===================================
Provides an AI HR representative to practice salary negotiations.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import sys, os

# Ensure agent can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agent.llm_provider import get_llm_with_fallback
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

router = APIRouter(prefix="/negotiation", tags=["Negotiation"])

class NegotiationMessage(BaseModel):
    role: str = Field(description="Either 'user' or 'ai'")
    content: str = Field(description="The message content")

class NegotiationRequest(BaseModel):
    job_title: str
    target_salary_lpa: float
    history: List[NegotiationMessage] = Field(default_factory=list)
    user_message: str

class NegotiationResponse(BaseModel):
    ai_response: str = Field(description="The recruiter's response")
    feedback: str = Field(description="Behind-the-scenes feedback on the user's negotiation tactic")
    sentiment: str = Field(description="Positive, Neutral, or Negative")

# ─── Prompts ───

NEGOTIATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an experienced HR Recruiter at a top tech company in India. 
You are currently negotiating an offer for the role of {job_title} with a candidate.
The candidate's target salary is {target_salary_lpa} LPA, but your initial budget is 20% lower.
Be professional, firm, but open to persuasion if the candidate makes strong, value-based arguments (e.g. highlighting their unique skills, market rate, or competing offers).
If they just ask for more money without justification, push back politely.
Provide your response, and also provide a brief behind-the-scenes 'feedback' on their negotiation tactic.
"""),
    # We will format the history manually into the prompt to keep it simple with structured output
    ("human", "{chat_history}\nCandidate: {user_message}")
])

@router.post("/chat", response_model=NegotiationResponse)
async def chat_negotiation(req: NegotiationRequest):
    """Process a turn in the salary negotiation chat."""
    try:
        # Format chat history
        history_str = ""
        for msg in req.history:
            prefix = "Recruiter:" if msg.role == "ai" else "Candidate:"
            history_str += f"{prefix} {msg.content}\n"
            
        result = get_llm_with_fallback(
            prompt_template=NEGOTIATION_PROMPT,
            output_schema=NegotiationResponse,
            input_vars={
                "job_title": req.job_title,
                "target_salary_lpa": req.target_salary_lpa,
                "chat_history": history_str,
                "user_message": req.user_message
            },
            temperature=0.4,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Negotiation engine failed: {str(e)}")
