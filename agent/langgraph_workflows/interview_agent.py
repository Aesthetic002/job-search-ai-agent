"""
Interview Agent - Provides mock interview preparation and coaching.

This agent handles:
- Generating interview questions based on job description
- Conducting mock interviews
- Providing feedback on answers
- Interview tips and preparation strategies
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class QuestionType(str, Enum):
    """Types of interview questions."""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    COMPETENCY = "competency"
    CULTURE_FIT = "culture_fit"


@dataclass
class InterviewQuestion:
    """Data class for interview question."""
    question: str
    question_type: QuestionType
    difficulty: str  # easy, medium, hard
    tips: List[str]
    sample_answer: Optional[str] = None


@dataclass
class InterviewFeedback:
    """Data class for interview answer feedback."""
    score: int  # 1-10
    strengths: List[str]
    improvements: List[str]
    revised_answer: Optional[str] = None


class InterviewAgent:
    """
    Agent responsible for interview preparation and mock interviews.
    Generates questions and provides feedback on answers.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.5,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """You are an expert interview coach with experience in HR and technical recruiting.
Your role is to help candidates prepare for job interviews through practice and feedback.

Key responsibilities:
1. Generate relevant interview questions based on job descriptions
2. Evaluate candidate responses using STAR method criteria
3. Provide constructive feedback
4. Suggest improvements
5. Share interview strategies and tips

Be encouraging while providing honest, actionable feedback."""

    def generate_questions(
        self,
        job_title: str,
        job_description: str,
        company: str,
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate interview questions based on job description."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Generate {num_questions} interview questions for this role:

Job Title: {job_title}
Company: {company}
Job Description: {job_description}

Generate a mix of:
- 3 behavioral questions (STAR method)
- 3 technical/skill-based questions
- 2 situational questions
- 2 culture fit questions

For each question, provide:
1. The question
2. Question type
3. Difficulty (easy/medium/hard)
4. Tips for answering
5. Key points to include

Format as a structured list.""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "job_title": job_title,
            "company": company,
            "questions": response.content,
            "total_questions": num_questions
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_context: str
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer to an interview question."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate this interview answer:

QUESTION: {question}

CANDIDATE'S ANSWER: {answer}

JOB CONTEXT: {job_context}

Evaluate using STAR method criteria (if applicable):
- Situation: Did they set the context?
- Task: Did they explain their responsibility?
- Action: Did they describe specific actions taken?
- Result: Did they share measurable outcomes?

Provide:
1. Score (1-10)
2. Strengths of the answer
3. Areas for improvement
4. A revised/improved version of the answer
5. Additional tips""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "question": question,
            "original_answer": answer,
            "feedback": response.content
        }

    def generate_follow_ups(
        self,
        question: str,
        answer: str
    ) -> List[str]:
        """Generate follow-up questions based on candidate's answer."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Based on this Q&A, generate 3 likely follow-up questions:

ORIGINAL QUESTION: {question}

CANDIDATE'S ANSWER: {answer}

Generate follow-up questions that:
1. Dig deeper into specific claims
2. Clarify ambiguous points
3. Test related knowledge/experience

List the follow-up questions.""")
        ])

        response = self.llm.invoke(prompt.format_messages())
        return response.content

    def provide_interview_tips(
        self,
        job_title: str,
        company: str,
        interview_type: str = "general"
    ) -> Dict[str, Any]:
        """Provide interview preparation tips."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Provide comprehensive interview tips for:

Position: {job_title}
Company: {company}
Interview Type: {interview_type}

Include:
1. Pre-interview preparation checklist
2. Research suggestions about the company
3. Common mistakes to avoid
4. Body language and communication tips
5. Questions to ask the interviewer
6. Post-interview follow-up advice""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "job_title": job_title,
            "company": company,
            "tips": response.content
        }

    def simulate_interview(
        self,
        job_info: Dict[str, Any],
        num_rounds: int = 5
    ) -> Dict[str, Any]:
        """Set up a mock interview simulation."""
        questions = self.generate_questions(
            job_info.get("title", ""),
            job_info.get("description", ""),
            job_info.get("company", ""),
            num_questions=num_rounds
        )

        tips = self.provide_interview_tips(
            job_info.get("title", ""),
            job_info.get("company", "")
        )

        return {
            "interview_setup": {
                "job_title": job_info.get("title"),
                "company": job_info.get("company"),
                "total_rounds": num_rounds
            },
            "questions": questions,
            "preparation_tips": tips,
            "status": "ready_to_start"
        }

    def process(
        self,
        job_info: Dict[str, Any],
        mode: str = "prepare",
        answer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main processing function for interview agent.

        Args:
            job_info: Job information for interview prep
            mode: "prepare" for setup, "evaluate" for answer feedback
            answer_data: Answer to evaluate (for evaluate mode)

        Returns:
            Dictionary with interview materials or feedback
        """
        if mode == "prepare":
            return self.simulate_interview(job_info)

        elif mode == "evaluate" and answer_data:
            feedback = self.evaluate_answer(
                answer_data.get("question", ""),
                answer_data.get("answer", ""),
                f"{job_info.get('title', '')} at {job_info.get('company', '')}"
            )
            follow_ups = self.generate_follow_ups(
                answer_data.get("question", ""),
                answer_data.get("answer", "")
            )

            return {
                "feedback": feedback,
                "follow_up_questions": follow_ups
            }

        elif mode == "tips":
            return self.provide_interview_tips(
                job_info.get("title", ""),
                job_info.get("company", "")
            )

        return {"error": "Invalid mode specified"}


def interview_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for interview preparation.

    Args:
        state: Current workflow state containing job info and mode

    Returns:
        Updated state with interview materials
    """
    agent = InterviewAgent()

    job_info = state.get("target_job", {})
    mode = state.get("interview_mode", "prepare")
    answer_data = state.get("answer_to_evaluate")

    results = agent.process(job_info, mode, answer_data)

    return {
        **state,
        "interview_results": results,
        "current_agent": "interview",
        "status": "interview_complete"
    }
