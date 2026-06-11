"""
Career Advisor Agent - Provides career guidance and recommendations.

This agent handles:
- Career path analysis and recommendations
- Skill gap identification
- Industry insights
- Long-term career planning
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


@dataclass
class CareerPath:
    """Data class for career path suggestion."""
    title: str
    timeline: str
    required_skills: List[str]
    salary_range: str
    growth_potential: str


@dataclass
class SkillGap:
    """Data class for skill gap analysis."""
    skill: str
    importance: str  # critical, important, nice-to-have
    learning_resources: List[str]
    estimated_time: str


class CareerAdvisor:
    """
    Agent responsible for career guidance and long-term planning.
    Provides insights on career paths, skill development, and industry trends.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.6,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = """You are an experienced career advisor and industry expert.
Your role is to help professionals make informed career decisions and plan their growth.

Key responsibilities:
1. Analyze career trajectories and suggest paths
2. Identify skill gaps and learning opportunities
3. Provide industry insights and trends
4. Offer salary negotiation guidance
5. Suggest networking strategies

Be realistic yet encouraging. Base advice on current market trends."""

    def analyze_career_path(
        self,
        current_role: str,
        experience_years: int,
        skills: List[str],
        goals: str
    ) -> Dict[str, Any]:
        """Analyze current position and suggest career paths."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Analyze this professional's career and suggest paths:

Current Role: {current_role}
Years of Experience: {experience_years}
Current Skills: {', '.join(skills)}
Career Goals: {goals}

Provide:
1. Assessment of current career position
2. Three potential career paths (short, medium, long-term)
3. Skills needed for each path
4. Estimated timeline for each transition
5. Industry trends affecting these paths
6. Specific action items for the next 6 months""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "current_role": current_role,
            "experience": experience_years,
            "career_analysis": response.content
        }

    def identify_skill_gaps(
        self,
        current_skills: List[str],
        target_role: str,
        industry: str
    ) -> Dict[str, Any]:
        """Identify skill gaps for target role."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Identify skill gaps for career transition:

Current Skills: {', '.join(current_skills)}
Target Role: {target_role}
Industry: {industry}

Provide:
1. Skills already possessed that are relevant
2. Critical skills missing (must-have)
3. Important skills to develop (nice-to-have)
4. Learning resources for each missing skill
5. Estimated time to acquire each skill
6. Priority order for skill development""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "target_role": target_role,
            "industry": industry,
            "skill_gap_analysis": response.content,
            "current_skills_count": len(current_skills)
        }

    def get_industry_insights(
        self,
        industry: str,
        role_type: str
    ) -> Dict[str, Any]:
        """Get current industry insights and trends."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Provide industry insights for:

Industry: {industry}
Role Type: {role_type}

Include:
1. Current industry trends
2. In-demand skills
3. Salary benchmarks
4. Top companies hiring
5. Remote work trends
6. Future outlook (1-3 years)
7. Emerging technologies/practices
8. Networking opportunities""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "industry": industry,
            "role_type": role_type,
            "insights": response.content
        }

    def salary_guidance(
        self,
        role: str,
        experience_years: int,
        location: str,
        skills: List[str]
    ) -> Dict[str, Any]:
        """Provide salary negotiation guidance."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Provide salary guidance for:

Role: {role}
Experience: {experience_years} years
Location: {location}
Key Skills: {', '.join(skills)}

Include:
1. Expected salary range for this profile
2. Factors that could increase compensation
3. Negotiation strategies
4. Benefits to negotiate beyond salary
5. When to negotiate vs accept
6. Red flags in offers""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "role": role,
            "location": location,
            "salary_guidance": response.content
        }

    def create_development_plan(
        self,
        profile: Dict[str, Any],
        target_role: str,
        timeline_months: int = 12
    ) -> Dict[str, Any]:
        """Create a professional development plan."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Create a {timeline_months}-month development plan:

Current Profile:
- Role: {profile.get('current_role', 'Not specified')}
- Experience: {profile.get('experience_years', 0)} years
- Skills: {', '.join(profile.get('skills', []))}

Target Role: {target_role}
Timeline: {timeline_months} months

Provide a month-by-month plan including:
1. Skills to develop each quarter
2. Certifications to pursue
3. Projects to build
4. Networking activities
5. Learning resources
6. Milestones and checkpoints
7. Portfolio items to create""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "target_role": target_role,
            "timeline_months": timeline_months,
            "development_plan": response.content
        }

    def networking_strategy(
        self,
        industry: str,
        target_companies: List[str],
        goals: str
    ) -> Dict[str, Any]:
        """Suggest networking strategies."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Create a networking strategy:

Industry: {industry}
Target Companies: {', '.join(target_companies)}
Goals: {goals}

Include:
1. Platforms to focus on (LinkedIn, etc.)
2. Events and conferences to attend
3. Communities to join
4. Content creation strategy
5. Outreach templates
6. Follow-up best practices
7. Building genuine relationships""")
        ])

        response = self.llm.invoke(prompt.format_messages())

        return {
            "industry": industry,
            "networking_strategy": response.content
        }

    def process(
        self,
        user_profile: Dict[str, Any],
        request_type: str = "career_path"
    ) -> Dict[str, Any]:
        """
        Main processing function for career advisor.

        Args:
            user_profile: User's profile and career information
            request_type: Type of advice requested

        Returns:
            Dictionary with career advice and recommendations
        """
        results = {}

        if request_type == "career_path":
            results = self.analyze_career_path(
                user_profile.get("current_role", ""),
                user_profile.get("experience_years", 0),
                user_profile.get("skills", []),
                user_profile.get("goals", "")
            )

        elif request_type == "skill_gaps":
            results = self.identify_skill_gaps(
                user_profile.get("skills", []),
                user_profile.get("target_role", ""),
                user_profile.get("industry", "")
            )

        elif request_type == "industry_insights":
            results = self.get_industry_insights(
                user_profile.get("industry", ""),
                user_profile.get("role_type", "")
            )

        elif request_type == "salary":
            results = self.salary_guidance(
                user_profile.get("current_role", ""),
                user_profile.get("experience_years", 0),
                user_profile.get("location", ""),
                user_profile.get("skills", [])
            )

        elif request_type == "development_plan":
            results = self.create_development_plan(
                user_profile,
                user_profile.get("target_role", ""),
                user_profile.get("timeline_months", 12)
            )

        elif request_type == "networking":
            results = self.networking_strategy(
                user_profile.get("industry", ""),
                user_profile.get("target_companies", []),
                user_profile.get("goals", "")
            )

        return results


def career_advisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for career advice.

    Args:
        state: Current workflow state containing user profile

    Returns:
        Updated state with career advice
    """
    agent = CareerAdvisor()

    user_profile = state.get("user_profile", {})
    request_type = state.get("advice_type", "career_path")

    results = agent.process(user_profile, request_type)

    return {
        **state,
        "career_advice": results,
        "current_agent": "career_advisor",
        "status": "career_advice_complete"
    }
