from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from ..utils.database import get_db
from ..utils.auth import get_current_user_unified as get_current_user
from ..models import User, UserProfile, UserSkill, SavedRecommendation
from ..services.llm_service import generate_career_advice
import json

router = APIRouter(prefix="/api/careers", tags=["career-advisor"])
logger = logging.getLogger(__name__)

class LLMQueryRequest(BaseModel):
    job_id: str
    job_source: str  # 'esco' or 'oasis'
    query: str
    context: Optional[Dict[str, Any]] = None

class LLMQueryResponse(BaseModel):
    response: str
    query: str

@router.post("/llm-query", response_model=LLMQueryResponse)
async def query_career_advisor(
    request: LLMQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process LLM queries about specific careers with user context.
    Uses appropriate formatters based on job source (ESCO vs OaSIS).
    """
    try:
        # Get user profile and skills
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        
        if not user_profile:
            raise HTTPException(status_code=400, detail="User profile not found")
        
        # Get job details based on source
        job_details = None
        formatter_type = None
        
        if request.job_source == "esco":
            # Get ESCO job from saved_recommendations (home page recommendations)
            saved_rec = db.query(SavedRecommendation).filter(
                SavedRecommendation.oasis_code == request.job_id,
                SavedRecommendation.user_id == current_user.id
            ).first()
            
            if saved_rec:
                job_details = {
                    "title": saved_rec.label,
                    "description": saved_rec.description,
                    "main_duties": saved_rec.main_duties,
                    "skills": {
                        "creativity": saved_rec.role_creativity,
                        "leadership": saved_rec.role_leadership,
                        "digital_literacy": saved_rec.role_digital_literacy,
                        "critical_thinking": saved_rec.role_critical_thinking,
                        "problem_solving": saved_rec.role_problem_solving
                    },
                    "entry_qualifications": saved_rec.entry_qualifications,
                    "all_fields": (
                        saved_rec.all_fields if isinstance(saved_rec.all_fields, dict) 
                        else json.loads(saved_rec.all_fields) if saved_rec.all_fields 
                        else {}
                    )
                }
                formatter_type = "ESCO-OccupationFormatter"  # ESCO uses ESCO formatter
                
        elif request.job_source == "oasis":
            # Get OaSIS job from saved_jobs (SwipeMyWay discoveries)
            from sqlalchemy import text
            query = text("""
                SELECT job_title, metadata
                FROM saved_jobs
                WHERE esco_id = :job_id AND user_id = :user_id
                LIMIT 1
            """)
            result = db.execute(query, {"job_id": request.job_id, "user_id": current_user.id}).fetchone()
            
            if result:
                job_details = {
                    "title": result.job_title,
                    "description": result.metadata.get("description", "") if result.metadata else "",
                    "skills": result.metadata.get("skills", []) if result.metadata else [],
                    "education_level": result.metadata.get("education_level", "") if result.metadata else "",
                    "experience_years": result.metadata.get("experience_years", "") if result.metadata else ""
                }
                formatter_type = "OaSIS-RoleFormatter"  # OaSIS uses OaSIS formatter
        
        if not job_details:
            raise HTTPException(status_code=404, detail=f"Job not found: {request.job_id}")
        
        # Build context for LLM
        llm_context = {
            "user_profile": {
                "name": user_profile.name,
                "age": user_profile.age,
                "major": user_profile.major,
                "year": user_profile.year,
                "gpa": user_profile.gpa,
                "education_level": user_profile.education_level,
                "years_experience": user_profile.years_experience,
                "career_goals": user_profile.career_goals,
                "interests": user_profile.interests,
                "hobbies": user_profile.hobbies,
                "learning_style": user_profile.learning_style
            },
            "user_skills": {
                "creativity": user_skills.creativity if user_skills else 0,
                "leadership": user_skills.leadership if user_skills else 0,
                "digital_literacy": user_skills.digital_literacy if user_skills else 0,
                "critical_thinking": user_skills.critical_thinking if user_skills else 0,
                "problem_solving": user_skills.problem_solving if user_skills else 0
            } if user_skills else {},
            "job_details": job_details,
            "formatter_type": formatter_type,
            "fit_analysis": request.context  # Include any career fit analysis
        }
        
        # Common career questions with tailored prompts
        question_prompts = {
            "Why would I want to do this job?": f"""
                Based on the user's profile and interests, explain why {job_details['title']} 
                would be personally fulfilling and align with their values and goals.
                Consider their learning style, hobbies, and career aspirations.
            """,
            "What are the 3 biggest barriers?": f"""
                Identify the 3 most significant barriers between the user and becoming a {job_details['title']}.
                Be specific about skill gaps, education requirements, experience needs, and timeline.
                Order from most to least challenging.
            """,
            "How long would it realistically take to qualify?": f"""
                Calculate a realistic timeline for the user to qualify for {job_details['title']}.
                Consider their current education level, skills, and the typical path.
                Break down into phases: education, skill building, experience gaining, job search.
            """,
            "Do I need a PhD for this?": f"""
                Analyze whether a PhD is required or beneficial for {job_details['title']}.
                Consider: minimum requirements, competitive advantage, industry norms, and ROI.
                Suggest alternative paths if PhD is not essential.
            """,
            "What are the actual qualifications?": f"""
                List the concrete qualifications needed for {job_details['title']}.
                Include: education, certifications, skills, experience, portfolio requirements.
                Distinguish between must-haves and nice-to-haves.
            """
        }
        
        # Check if query matches a common question
        enhanced_query = request.query
        for common_q, prompt in question_prompts.items():
            if common_q.lower() in request.query.lower():
                enhanced_query = prompt
                break
        
        # Generate response using LLM
        system_prompt = f"""
        You are a career advisor helping a student understand career fit for {job_details['title']}.
        Use the {formatter_type} to structure your response appropriately.
        
        Be honest about barriers and timelines. Students need truth, not optimism.
        If something will take 8 years and significant debt, say so clearly.
        
        User Context:
        - Education: {user_profile.major}, Year {user_profile.year}, GPA {user_profile.gpa}
        - Experience: {user_profile.years_experience} years
        - Age: {user_profile.age}
        """
        
        response = await generate_career_advice(
            system_prompt=system_prompt,
            user_query=enhanced_query,
            context=llm_context
        )
        
        return LLMQueryResponse(
            query=request.query,
            response=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in career advisor query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process career advice query: {str(e)}"
        )