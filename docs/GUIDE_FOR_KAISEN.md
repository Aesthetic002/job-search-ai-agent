# Contribution Guide for Kaisen

## Resume Parser & Interview Service Developer

**Branch:** `feature/resume-parser`
**Phase:** 1 (Work in parallel with Hemanth)
**Owner of:** `agent/resume_parser.py`, `agent/ats_scoring.py`, `backend/resume_service/`, `backend/interview_service/`

---

## 1. Overview

You are responsible for building the resume parsing logic, ATS scoring system, and interview service. Your work runs in **Phase 1** alongside Hemanth's work.

**Your responsibilities:**
- PDF parsing logic in `agent/resume_parser.py`
- ATS scoring logic in `agent/ats_scoring.py`
- NLP pipeline for skill/keyword extraction
- Mock interview session flow in `interview_service`
- Resume scoring against job descriptions

---

## 2. Current Backend Status (What Hemanth Has Built)

Before you start, understand what's already implemented:

### Storage Architecture

Hemanth has set up:
- **Firestore** - NoSQL database for all data
- **Azure Blob Storage** - For resume files (PDF, DOCX, TXT)

**Important:** Resume files are stored in Azure Blob Storage, NOT locally.

### Resume Upload System (Already Built by Hemanth)

Hemanth has created a complete resume upload system:

| What | Where | Description |
|------|-------|-------------|
| File Upload API | `backend/resume_routes.py` | Handles file upload to Azure |
| File Service | `backend/resume_file_service.py` | Azure Blob operations + basic parsing |
| Config | `config.py` | Firebase + Azure initialization |

**The upload flow:**
1. User uploads file via `/resumes/upload`
2. File is stored in Azure Blob Storage at path: `{user_id}/{resume_id}.pdf`
3. Basic text is extracted (PyPDF2 for PDF, python-docx for DOCX)
4. Metadata + parsed text stored in Firestore `resumes` collection

### What You Need to Build

Hemanth's basic parser extracts raw text. **You need to build:**
- Advanced NLP parsing (extract skills, experience, education)
- ATS scoring algorithm
- Resume-to-job matching
- Interview service

---

## 3. How to Set Up Your Development Environment

### Step 1: Clone and Create Your Branch

```bash
git clone <repo-url>
cd job-search-ai-agent
git checkout main
git pull origin main
git checkout -b feature/resume-parser
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt

# Additional NLP dependencies you might need
pip install spacy nltk scikit-learn
python -m spacy download en_core_web_sm
```

### Step 3: Environment Setup

You don't need Firebase/Azure credentials for development. You can:
1. **Ask Hemanth for test credentials**, OR
2. **Work with mock data** during development

For mock development, create test files locally:

```python
# tests/mock_resume.txt
SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer
john@email.com | (555) 123-4567

SKILLS
Python, JavaScript, React, Node.js, PostgreSQL, Docker

EXPERIENCE
Senior Software Engineer | TechCorp | 2020-Present
- Built microservices architecture
- Led team of 5 developers

EDUCATION
BS Computer Science | State University | 2016
"""
```

---

## 4. Files You Should Create

### Directory Structure

```
agent/
├── resume_parser.py           # Main parsing logic (replace placeholder)
├── ats_scoring.py             # ATS scoring algorithm (replace placeholder)
└── utils/
    ├── __init__.py
    ├── pdf_extractor.py       # Advanced PDF extraction
    ├── skill_matcher.py       # Skill keyword matching
    └── nlp_pipeline.py        # NLP processing

backend/resume_service/
├── main.py                    # FastAPI app (modify existing)
├── routes/
│   └── resume.py              # Resume scoring endpoints
├── schemas.py                 # Pydantic models
├── dependencies.py            # Firestore helpers
└── Dockerfile

backend/interview_service/
├── main.py                    # FastAPI app (modify existing)
├── routes/
│   └── interview.py           # Interview session endpoints
├── schemas.py                 # Pydantic models
├── dependencies.py            # Helpers
└── Dockerfile
```

---

## 5. Resume Parser Implementation

### agent/resume_parser.py

```python
"""
Resume Parser - Extracts structured data from resume text.
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ParsedResume:
    """Structured resume data."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = None
    experience: List[Dict] = None
    education: List[Dict] = None
    summary: Optional[str] = None
    raw_text: str = ""

class ResumeParser:
    """
    Parse resume text into structured data.
    """

    # Common skills to look for
    TECH_SKILLS = [
        "python", "javascript", "java", "c++", "react", "angular", "vue",
        "node.js", "django", "flask", "fastapi", "sql", "postgresql", "mysql",
        "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp",
        "git", "linux", "machine learning", "deep learning", "tensorflow",
        "pytorch", "nlp", "data science", "pandas", "numpy"
    ]

    def __init__(self):
        self.skills_pattern = re.compile(
            r'\b(' + '|'.join(self.TECH_SKILLS) + r')\b',
            re.IGNORECASE
        )

    def parse(self, text: str) -> ParsedResume:
        """
        Parse resume text into structured data.

        Args:
            text: Raw text extracted from resume file

        Returns:
            ParsedResume object with extracted fields
        """
        return ParsedResume(
            name=self._extract_name(text),
            email=self._extract_email(text),
            phone=self._extract_phone(text),
            skills=self._extract_skills(text),
            experience=self._extract_experience(text),
            education=self._extract_education(text),
            summary=self._extract_summary(text),
            raw_text=text
        )

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address."""
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number."""
        patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+91[\s-]?[0-9]{10}'  # Indian phone format
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name.
        Usually the first line or first capitalized words.
        """
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Skip empty lines and common headers
            if not line or line.lower() in ['resume', 'cv', 'curriculum vitae']:
                continue
            # Check if line looks like a name (2-4 capitalized words)
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                return line
        return None

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills."""
        text_lower = text.lower()
        found_skills = set()

        for skill in self.TECH_SKILLS:
            if skill.lower() in text_lower:
                found_skills.add(skill.title())

        return list(found_skills)

    def _extract_experience(self, text: str) -> List[Dict]:
        """
        Extract work experience sections.
        Returns list of experience entries.
        """
        experience = []

        # Look for experience section
        exp_pattern = r'(?:experience|work history|employment)\s*\n([\s\S]*?)(?=\n(?:education|skills|projects)|$)'
        match = re.search(exp_pattern, text, re.IGNORECASE)

        if match:
            exp_text = match.group(1)
            # Parse individual entries (simplified)
            lines = [l.strip() for l in exp_text.split('\n') if l.strip()]

            current_entry = {}
            for line in lines:
                # Look for company/title patterns
                if '|' in line or '-' in line:
                    if current_entry:
                        experience.append(current_entry)
                    current_entry = {'title': line, 'description': []}
                elif current_entry:
                    current_entry['description'].append(line)

            if current_entry:
                experience.append(current_entry)

        return experience

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information."""
        education = []

        edu_pattern = r'(?:education|academic|qualification)\s*\n([\s\S]*?)(?=\n(?:experience|skills|projects)|$)'
        match = re.search(edu_pattern, text, re.IGNORECASE)

        if match:
            edu_text = match.group(1)
            lines = [l.strip() for l in edu_text.split('\n') if l.strip()]

            for line in lines:
                if any(deg in line.lower() for deg in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bsc', 'msc']):
                    education.append({'degree': line})

        return education

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary."""
        summary_pattern = r'(?:summary|objective|profile)\s*\n([\s\S]*?)(?=\n(?:experience|education|skills)|$)'
        match = re.search(summary_pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()[:500]  # Limit to 500 chars
        return None


# Convenience function
def parse_resume(text: str) -> ParsedResume:
    """Parse resume text into structured data."""
    parser = ResumeParser()
    return parser.parse(text)
```

---

## 6. ATS Scoring Implementation

### agent/ats_scoring.py

```python
"""
ATS (Applicant Tracking System) Scoring - Score resumes against job descriptions.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class ATSScore:
    """ATS scoring result."""
    overall_score: float  # 0-100
    skill_match_score: float
    keyword_score: float
    experience_score: float
    education_score: float
    formatting_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]

class ATSScorer:
    """
    Score resumes against job descriptions.
    """

    def __init__(self):
        # Weights for different scoring components
        self.weights = {
            'skills': 0.35,
            'keywords': 0.25,
            'experience': 0.25,
            'education': 0.10,
            'formatting': 0.05
        }

    def score(
        self,
        resume_text: str,
        job_description: str,
        required_skills: Optional[List[str]] = None
    ) -> ATSScore:
        """
        Score a resume against a job description.

        Args:
            resume_text: Parsed or raw resume text
            job_description: Job posting text
            required_skills: Optional list of must-have skills

        Returns:
            ATSScore with detailed breakdown
        """
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        # Extract skills from job description if not provided
        if required_skills is None:
            required_skills = self._extract_job_skills(job_description)

        # Calculate individual scores
        skill_score, matched, missing = self._score_skills(
            resume_lower, required_skills
        )
        keyword_score = self._score_keywords(resume_lower, job_lower)
        experience_score = self._score_experience(resume_text)
        education_score = self._score_education(resume_text)
        formatting_score = self._score_formatting(resume_text)

        # Calculate weighted overall score
        overall = (
            skill_score * self.weights['skills'] +
            keyword_score * self.weights['keywords'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            formatting_score * self.weights['formatting']
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(
            skill_score, matched, missing, formatting_score
        )

        return ATSScore(
            overall_score=round(overall, 1),
            skill_match_score=round(skill_score, 1),
            keyword_score=round(keyword_score, 1),
            experience_score=round(experience_score, 1),
            education_score=round(education_score, 1),
            formatting_score=round(formatting_score, 1),
            matched_skills=matched,
            missing_skills=missing,
            suggestions=suggestions
        )

    def _extract_job_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description."""
        common_skills = [
            "python", "javascript", "java", "c++", "react", "angular", "node.js",
            "sql", "postgresql", "mongodb", "docker", "kubernetes", "aws", "azure",
            "machine learning", "data science", "api", "rest", "microservices"
        ]

        job_lower = job_description.lower()
        found = [skill for skill in common_skills if skill in job_lower]
        return found

    def _score_skills(
        self,
        resume_text: str,
        required_skills: List[str]
    ) -> tuple:
        """Score skill matching."""
        if not required_skills:
            return 70.0, [], []  # Default score if no skills specified

        matched = []
        missing = []

        for skill in required_skills:
            if skill.lower() in resume_text:
                matched.append(skill)
            else:
                missing.append(skill)

        if not required_skills:
            score = 70.0
        else:
            score = (len(matched) / len(required_skills)) * 100

        return score, matched, missing

    def _score_keywords(self, resume_text: str, job_text: str) -> float:
        """Score keyword overlap between resume and job."""
        # Extract significant words from job description
        job_words = set(re.findall(r'\b[a-z]{4,}\b', job_text))
        job_words -= {'that', 'with', 'this', 'have', 'from', 'will', 'been'}

        if not job_words:
            return 70.0

        # Count matches
        matches = sum(1 for word in job_words if word in resume_text)
        score = min((matches / len(job_words)) * 150, 100)  # Scale up

        return score

    def _score_experience(self, resume_text: str) -> float:
        """Score based on experience indicators."""
        score = 50.0  # Base score

        # Check for years of experience
        years_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        match = re.search(years_pattern, resume_text, re.IGNORECASE)
        if match:
            years = int(match.group(1))
            score += min(years * 5, 30)  # Up to 30 bonus points

        # Check for company mentions
        if re.search(r'(?:senior|lead|principal|manager)', resume_text, re.IGNORECASE):
            score += 15

        return min(score, 100)

    def _score_education(self, resume_text: str) -> float:
        """Score education level."""
        score = 50.0

        text_lower = resume_text.lower()

        if any(deg in text_lower for deg in ['phd', 'doctorate']):
            score = 100
        elif any(deg in text_lower for deg in ["master's", 'masters', 'm.tech', 'msc', 'mba']):
            score = 85
        elif any(deg in text_lower for deg in ["bachelor's", 'bachelors', 'b.tech', 'bsc', 'b.e.']):
            score = 70

        return score

    def _score_formatting(self, resume_text: str) -> float:
        """Score resume formatting quality."""
        score = 100.0

        # Penalize if too short
        if len(resume_text) < 500:
            score -= 30

        # Penalize if no clear sections
        sections = ['experience', 'education', 'skills']
        found_sections = sum(1 for s in sections if s in resume_text.lower())
        if found_sections < 2:
            score -= 20

        # Penalize excessive special characters
        special_chars = len(re.findall(r'[^\w\s\.\,\-\@]', resume_text))
        if special_chars > 50:
            score -= 10

        return max(score, 0)

    def _generate_suggestions(
        self,
        skill_score: float,
        matched: List[str],
        missing: List[str],
        formatting_score: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        if missing:
            suggestions.append(
                f"Add these missing skills if applicable: {', '.join(missing[:5])}"
            )

        if skill_score < 50:
            suggestions.append(
                "Your resume lacks many keywords from the job description. "
                "Consider tailoring it to match the job requirements."
            )

        if formatting_score < 70:
            suggestions.append(
                "Improve resume formatting: ensure clear sections for "
                "Experience, Education, and Skills."
            )

        if not suggestions:
            suggestions.append("Your resume is well-matched for this position!")

        return suggestions


# Convenience function
def score_resume(
    resume_text: str,
    job_description: str,
    required_skills: Optional[List[str]] = None
) -> ATSScore:
    """Score a resume against a job description."""
    scorer = ATSScorer()
    return scorer.score(resume_text, job_description, required_skills)
```

---

## 7. Resume Service Endpoints

### backend/resume_service/routes/resume.py

```python
"""
Resume Service Routes - Scoring and analysis endpoints.

NOTE: File upload is handled by Hemanth's code in backend/resume_routes.py
This file handles scoring and analysis of already-uploaded resumes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from agent.resume_parser import parse_resume
from agent.ats_scoring import score_resume
from config import get_firestore_client

router = APIRouter(prefix="/resume", tags=["resume"])

@router.get("/{resume_id}/parse")
async def parse_resume_endpoint(resume_id: str):
    """
    Parse a resume and return structured data.

    The resume text is fetched from Firestore (already parsed by upload service).
    """
    db = get_firestore_client()

    # Get resume from Firestore
    doc = db.collection('resumes').document(resume_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_data = doc.to_dict()
    raw_text = resume_data.get('parsed_text', '')

    if not raw_text:
        raise HTTPException(
            status_code=400,
            detail="Resume has no parsed text. Try re-uploading."
        )

    # Parse into structured data
    parsed = parse_resume(raw_text)

    return {
        "resume_id": resume_id,
        "name": parsed.name,
        "email": parsed.email,
        "phone": parsed.phone,
        "skills": parsed.skills,
        "experience_count": len(parsed.experience or []),
        "education_count": len(parsed.education or [])
    }


@router.get("/{resume_id}/score")
async def score_resume_endpoint(
    resume_id: str,
    job_description: Optional[str] = Query(None, description="Job description to score against")
):
    """
    Score a resume against a job description (ATS scoring).

    Args:
        resume_id: ID of the resume in Firestore
        job_description: Optional job description text. If not provided,
                        returns a general quality score.
    """
    db = get_firestore_client()

    # Get resume from Firestore
    doc = db.collection('resumes').document(resume_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_data = doc.to_dict()
    raw_text = resume_data.get('parsed_text', '')

    if not raw_text:
        raise HTTPException(
            status_code=400,
            detail="Resume has no parsed text"
        )

    # Use default job description if none provided
    if not job_description:
        job_description = """
        Software Engineer position requiring experience with Python,
        JavaScript, SQL, and cloud technologies. Bachelor's degree preferred.
        """

    # Score the resume
    result = score_resume(raw_text, job_description)

    return {
        "resume_id": resume_id,
        "overall_score": result.overall_score,
        "breakdown": {
            "skill_match": result.skill_match_score,
            "keywords": result.keyword_score,
            "experience": result.experience_score,
            "education": result.education_score,
            "formatting": result.formatting_score
        },
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "suggestions": result.suggestions
    }


@router.post("/{resume_id}/score-against-job/{job_id}")
async def score_against_job(resume_id: str, job_id: str):
    """
    Score a resume against a specific job from the jobs collection.
    """
    db = get_firestore_client()

    # Get resume
    resume_doc = db.collection('resumes').document(resume_id).get()
    if not resume_doc.exists:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get job
    job_doc = db.collection('jobs').document(job_id).get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_text = resume_doc.to_dict().get('parsed_text', '')
    job_data = job_doc.to_dict()
    job_description = job_data.get('description', '')

    # Score
    result = score_resume(resume_text, job_description)

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "job_title": job_data.get('title'),
        "company": job_data.get('company'),
        "match_score": result.overall_score,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "suggestions": result.suggestions
    }
```

---

## 8. Interview Service

### backend/interview_service/routes/interview.py

```python
"""
Interview Service - Mock interview sessions.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

router = APIRouter(prefix="/interviews", tags=["interviews"])

# In-memory session storage (replace with Firestore in production)
interview_sessions = {}

class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    job_type: str
    difficulty: str
    questions: List[dict]
    current_question: int
    answers: List[dict]
    started_at: str
    status: str  # active, completed, abandoned

class StartInterviewRequest(BaseModel):
    user_id: str
    job_type: str = "software_engineer"
    difficulty: str = "medium"  # easy, medium, hard

class AnswerRequest(BaseModel):
    answer: str

# Sample interview questions
INTERVIEW_QUESTIONS = {
    "software_engineer": {
        "easy": [
            {"id": 1, "question": "Tell me about yourself and your background.", "type": "behavioral"},
            {"id": 2, "question": "What programming languages are you most comfortable with?", "type": "technical"},
            {"id": 3, "question": "Describe a project you're proud of.", "type": "behavioral"},
        ],
        "medium": [
            {"id": 1, "question": "Explain the difference between REST and GraphQL APIs.", "type": "technical"},
            {"id": 2, "question": "How do you handle disagreements with team members?", "type": "behavioral"},
            {"id": 3, "question": "What is your approach to debugging a complex issue?", "type": "technical"},
            {"id": 4, "question": "Describe a time you had to learn something quickly.", "type": "behavioral"},
        ],
        "hard": [
            {"id": 1, "question": "Design a URL shortening service like bit.ly.", "type": "system_design"},
            {"id": 2, "question": "How would you optimize a slow database query?", "type": "technical"},
            {"id": 3, "question": "Tell me about a time you failed and what you learned.", "type": "behavioral"},
            {"id": 4, "question": "Explain how you would scale an application to millions of users.", "type": "system_design"},
        ]
    }
}

@router.post("/start", response_model=dict)
async def start_interview(request: StartInterviewRequest):
    """Start a new mock interview session."""

    # Get questions for the job type and difficulty
    job_questions = INTERVIEW_QUESTIONS.get(request.job_type, INTERVIEW_QUESTIONS["software_engineer"])
    questions = job_questions.get(request.difficulty, job_questions["medium"])

    session_id = str(uuid.uuid4())
    session = InterviewSession(
        session_id=session_id,
        user_id=request.user_id,
        job_type=request.job_type,
        difficulty=request.difficulty,
        questions=questions,
        current_question=0,
        answers=[],
        started_at=datetime.utcnow().isoformat(),
        status="active"
    )

    interview_sessions[session_id] = session

    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "difficulty": request.difficulty,
        "first_question": questions[0] if questions else None
    }

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get current interview session status."""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "status": session.status,
        "current_question": session.current_question,
        "total_questions": len(session.questions),
        "answers_submitted": len(session.answers)
    }

@router.get("/{session_id}/current-question")
async def get_current_question(session_id: str):
    """Get the current question in the interview."""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Interview already completed")

    if session.current_question >= len(session.questions):
        return {"message": "No more questions", "completed": True}

    question = session.questions[session.current_question]
    return {
        "question_number": session.current_question + 1,
        "total_questions": len(session.questions),
        "question": question["question"],
        "type": question["type"]
    }

@router.post("/{session_id}/answer")
async def submit_answer(session_id: str, request: AnswerRequest):
    """Submit an answer to the current question."""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Interview already completed")

    # Store the answer
    session.answers.append({
        "question_id": session.current_question,
        "question": session.questions[session.current_question]["question"],
        "answer": request.answer,
        "submitted_at": datetime.utcnow().isoformat()
    })

    # Move to next question
    session.current_question += 1

    # Check if completed
    if session.current_question >= len(session.questions):
        session.status = "completed"
        return {
            "message": "Interview completed!",
            "completed": True,
            "total_answered": len(session.answers)
        }

    # Return next question
    next_q = session.questions[session.current_question]
    return {
        "message": "Answer submitted",
        "next_question": {
            "question_number": session.current_question + 1,
            "question": next_q["question"],
            "type": next_q["type"]
        }
    }

@router.get("/{session_id}/results")
async def get_results(session_id: str):
    """Get interview results and feedback."""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed yet")

    # Generate basic feedback (in production, use AI for analysis)
    return {
        "session_id": session_id,
        "total_questions": len(session.questions),
        "questions_answered": len(session.answers),
        "difficulty": session.difficulty,
        "answers": session.answers,
        "feedback": "Thank you for completing the mock interview. Review your answers above.",
        "tips": [
            "Practice the STAR method for behavioral questions",
            "For technical questions, think out loud to show your reasoning",
            "Take your time before answering"
        ]
    }
```

---

## 9. Important Notes - Avoid Conflicts

### DO NOT Modify These Files (Hemanth's Code)

- `config.py` - Firebase/Azure initialization
- `backend/auth_service/*` - Authentication service
- `backend/analytics_service/*` - Analytics service
- `backend/resume_file_service.py` - File upload to Azure
- `backend/resume_routes.py` - Resume upload endpoints
- `agent/langgraph_workflows/*` - AI agent workflows

### Your Files (Safe to Create/Modify)

- `agent/resume_parser.py` - Replace placeholder
- `agent/ats_scoring.py` - Replace placeholder
- `agent/utils/*` - Create new utilities
- `backend/resume_service/routes/*` - Scoring endpoints
- `backend/interview_service/*` - Interview service

### Integration Points with Hemanth's Code

You need to **read from** but not modify:
1. **Firestore `resumes` collection** - Contains `parsed_text` field with extracted text
2. **`config.py`** - Import `get_firestore_client()` for database access

Example integration:
```python
# Import Hemanth's config (read-only usage)
from config import get_firestore_client

db = get_firestore_client()
resume = db.collection('resumes').document(resume_id).get()
text = resume.to_dict().get('parsed_text', '')  # Use this for scoring
```

---

## 10. Testing Your Code

### Run Resume Service

```bash
cd job-search-ai-agent
python -m uvicorn backend.resume_service.main:app --port 8003 --reload
```

### Run Interview Service

```bash
python -m uvicorn backend.interview_service.main:app --port 8004 --reload
```

### Test Endpoints

```bash
# Parse resume
curl http://localhost:8003/resume/{resume_id}/parse

# Score resume
curl "http://localhost:8003/resume/{resume_id}/score?job_description=python developer"

# Start interview
curl -X POST http://localhost:8004/interviews/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "job_type": "software_engineer", "difficulty": "medium"}'
```

---

## 11. Git Workflow

```bash
# Before starting
git checkout feature/resume-parser
git pull origin main

# Daily commits
git add .
git commit -m "Add resume parsing logic"
git push origin feature/resume-parser
```

---

## 12. Questions?

- **File upload issues?** - Ask Hemanth (he owns the upload code)
- **Frontend integration?** - Ask Rohith
- **Job data integration?** - Ask Aaryan

---

**Start Date:** Phase 1 (Now - parallel with Hemanth)
**Branch:** `feature/resume-parser`
**Your Focus:** NLP parsing, ATS scoring, interview service

Good luck!
