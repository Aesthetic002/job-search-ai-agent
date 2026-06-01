"""
Interview Answer Evaluator — agent/interview_evaluator.py

Uses Groq (LLaMA 3.3 70B) to evaluate a candidate's answer to a mock interview question.
Returns a structured evaluation with:
  - A score (0–100)
  - Detected strengths
  - Areas for improvement
  - A model "ideal answer" for comparison
  - STAR method compliance check (for behavioral questions)

Usage:
    from agent.interview_evaluator import evaluate_answer_to_dict

    result = evaluate_answer_to_dict(
        question="Tell me about a time you dealt with a difficult teammate.",
        candidate_answer="I once had a teammate who...",
        job_title="Software Engineer",
        category="Behavioral",          # optional
        expected_topics=["communication", "conflict resolution"],  # optional
    )
"""
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


# ==================== PYDANTIC SCHEMAS ====================

class STARCompliance(BaseModel):
    """STAR method compliance check (for behavioral questions)."""
    situation_present: bool = Field(description="Did the answer describe a Situation?")
    task_present: bool = Field(description="Did the answer describe a Task?")
    action_present: bool = Field(description="Did the answer describe specific Actions taken?")
    result_present: bool = Field(description="Did the answer describe the Result or outcome?")
    star_score: int = Field(description="STAR completeness score 0-100 based on how well all four elements are covered")


class AnswerEvaluation(BaseModel):
    """Structured evaluation of a candidate's interview answer."""
    score: int = Field(
        description="Overall quality score for the answer (0-100). 90+ is excellent, 70-89 is good, 50-69 is average, below 50 needs significant improvement."
    )
    verdict: str = Field(
        description="One-line verdict: 'Excellent', 'Good', 'Average', or 'Needs Improvement'"
    )
    strengths: List[str] = Field(
        description="2-4 specific strengths of this answer — what the candidate did well"
    )
    improvements: List[str] = Field(
        description="2-4 specific, actionable ways to improve this answer"
    )
    missing_topics: List[str] = Field(
        default_factory=list,
        description="Key topics or concepts expected in the answer that were not addressed"
    )
    ideal_answer_summary: str = Field(
        description="A concise 3-5 sentence model answer that demonstrates what an excellent response looks like"
    )
    star_compliance: Optional[STARCompliance] = Field(
        None,
        description="STAR method analysis — only populated for Behavioral questions"
    )
    communication_feedback: str = Field(
        description="Brief feedback on clarity, structure, and communication quality of the answer"
    )


# ==================== PROMPTS ====================

EVALUATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a senior technical interviewer and career coach at a top technology company.
Your task is to evaluate a candidate's interview answer with genuine rigor and fairness.

Evaluation Guidelines:
1. Score honestly — reserve 90+ for truly exceptional answers that would impress experienced interviewers.
2. For behavioral questions, check STAR method compliance (Situation, Task, Action, Result).
3. Base your feedback on the expected_topics list if provided — call out any missing key points.
4. Be specific in strengths and improvements — avoid generic statements.
5. The ideal_answer_summary should be concise but concrete, demonstrating what an A+ answer looks like.
6. Assess communication quality — was the answer clear, structured, concise, and confident?

Question category types:
- Technical: Evaluate correctness, depth, and real-world applicability.
- Behavioral: Evaluate STAR method, specificity, and reflection.
- Situational: Evaluate reasoning process, trade-off awareness, and decision quality.
- Role-Specific: Evaluate domain knowledge and cultural fit signals."""
    ),
    (
        "human",
        """Evaluate the following interview answer:

Interview Question: {question}
Question Category: {category}
Target Job Title: {job_title}
Expected Topics/Concepts: {expected_topics}

Candidate's Answer:
\"\"\"{candidate_answer}\"\"\"

Provide a thorough, honest evaluation of this answer."""
    )
])


# ==================== LLM ENGINE ====================

def _get_groq_llm() -> ChatGroq:
    """Initialize Groq LLM with structured output capability."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file.\n"
            "Get a free key at: https://console.groq.com"
        )
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.3,  # Lower temp for more consistent evaluation scores
    )


# ==================== PUBLIC API ====================

def evaluate_answer(
    question: str,
    candidate_answer: str,
    job_title: str,
    category: str = "General",
    expected_topics: Optional[List[str]] = None,
) -> AnswerEvaluation:
    """
    Evaluate a candidate's answer to a mock interview question.

    Args:
        question:          The interview question that was asked.
        candidate_answer:  The candidate's raw answer text.
        job_title:         Target job title (e.g., "Backend Engineer").
        category:          Question category — "Technical", "Behavioral", "Situational", "Role-Specific".
        expected_topics:   Optional list of key topics the answer should cover.

    Returns:
        AnswerEvaluation Pydantic model with full evaluation data.

    Raises:
        RuntimeError: If GROQ_API_KEY is missing.
        Exception:    If the LLM call fails.
    """
    llm = _get_groq_llm()
    structured_llm = llm.with_structured_output(AnswerEvaluation)
    chain = EVALUATOR_PROMPT | structured_llm

    result: AnswerEvaluation = chain.invoke({
        "question": question,
        "candidate_answer": candidate_answer,
        "job_title": job_title,
        "category": category,
        "expected_topics": ", ".join(expected_topics) if expected_topics else "Not specified",
    })

    # Only populate STAR compliance for behavioral questions
    if category.lower() != "behavioral" and result.star_compliance is not None:
        result.star_compliance = None

    return result


def evaluate_answer_to_dict(
    question: str,
    candidate_answer: str,
    job_title: str,
    category: str = "General",
    expected_topics: Optional[List[str]] = None,
) -> dict:
    """
    Same as evaluate_answer() but returns a plain dict (for API responses and Firestore storage).
    """
    return evaluate_answer(
        question=question,
        candidate_answer=candidate_answer,
        job_title=job_title,
        category=category,
        expected_topics=expected_topics,
    ).model_dump()


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("Testing Interview Answer Evaluator")
    print("=" * 60)

    # Test 1 — Behavioral question (with STAR check)
    result = evaluate_answer_to_dict(
        question="Tell me about a time you had to debug a critical production issue under pressure.",
        candidate_answer=(
            "Once our payment service started returning 500 errors and transactions were failing. "
            "I was on-call and had to fix it in 30 minutes before the business opened. "
            "I checked the logs, found a null pointer exception caused by a missing env variable after a deploy, "
            "rolled back the deployment and added a config validation check so it can't happen again. "
            "We had zero missed transactions after that and I wrote a post-mortem."
        ),
        job_title="Senior Backend Engineer",
        category="Behavioral",
        expected_topics=["root cause analysis", "communication", "incident response", "post-mortem"],
    )

    print("\n[BEHAVIORAL] Question Evaluation:")
    print(json.dumps(result, indent=2))

    # Test 2 - Technical question (no STAR check)
    result2 = evaluate_answer_to_dict(
        question="Explain the difference between a process and a thread, and when you'd use each.",
        candidate_answer="A process is a program running in memory. Threads are lighter. I use threads for concurrency.",
        job_title="Software Engineer",
        category="Technical",
        expected_topics=["memory isolation", "context switching", "GIL", "use cases", "shared memory"],
    )

    print("\n[TECHNICAL] Question Evaluation:")
    print(json.dumps(result2, indent=2))
