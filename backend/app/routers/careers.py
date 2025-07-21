from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple
from ..utils.database import get_db
from ..utils.auth import get_current_user_unified as get_current_user
from ..models import User
from ..services.Swipe_career_recommendation_service import (
    get_career_recommendations,
    save_career_recommendation,
    get_saved_careers
)
import logging
import json

router = APIRouter(prefix="/careers", tags=["careers"])
logger = logging.getLogger(__name__)

def extract_job_skills_graphsage_sync(job_id: str, job_title: str, job_description: str) -> List[Dict[str, Any]]:
    """
    Synchronous version of GraphSAGE skill extraction for use in sync endpoints.
    """
    try:
        from ..services.graphsage_llm_integration import graphsage_llm
        
        # Create a mock career goal list from job title and description
        career_keywords = [job_title]
        if job_description:
            # Extract key terms from description (simple approach)
            words = job_description.lower().split()
            skill_keywords = ["analytical", "leadership", "communication", "technical", "creative", 
                            "problem-solving", "teamwork", "management", "digital", "critical"]
            career_keywords.extend([w for w in words if any(k in w for k in skill_keywords)])[:5]
        
        # Get skill relevance scores for this job
        relevance_scores = graphsage_llm.compute_skill_relevance_scores(
            {},  # Empty user skills to get job-specific requirements
            career_keywords
        )
        
        # Sort and get top 5 skills
        top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Format the results
        skill_results = []
        for skill_id, score in top_skills:
            skill_metadata = graphsage_llm.node_metadata.get(skill_id, {})
            skill_results.append({
                "skill_id": skill_id,
                "skill_name": skill_metadata.get("label", "Unknown Skill"),
                "relevance_score": round(score, 3),
                "description": skill_metadata.get("description", "")[:100] + "..."  # Truncate long descriptions
            })
        
        return skill_results
        
    except Exception as e:
        logger.error(f"Error in GraphSAGE skill extraction: {str(e)}")
        # Return empty list on error
        return []

async def extract_job_skills_graphsage(oasis_code: str, job_title: str, job_description: str) -> List[Dict[str, Any]]:
    """
    Extract top skills for a job using GraphSAGE analysis.
    
    Args:
        oasis_code: The OaSIS code of the job
        job_title: Title of the job
        job_description: Description of the job
        
    Returns:
        List of top 5 skills with relevance scores
    """
    try:
        from ..services.graphsage_llm_integration import graphsage_llm
        
        # Create a mock career goal list from job title and description
        career_keywords = [job_title]
        if job_description:
            # Extract key terms from description (simple approach)
            words = job_description.lower().split()
            skill_keywords = ["analytical", "leadership", "communication", "technical", "creative", 
                            "problem-solving", "teamwork", "management", "digital", "critical"]
            career_keywords.extend([w for w in words if any(k in w for k in skill_keywords)])[:5]
        
        # Get skill relevance scores for this job
        relevance_scores = graphsage_llm.compute_skill_relevance_scores(
            {},  # Empty user skills to get job-specific requirements
            career_keywords
        )
        
        # Sort and get top 5 skills
        top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Format the results
        skill_results = []
        for skill_id, score in top_skills:
            skill_metadata = graphsage_llm.node_metadata.get(skill_id, {})
            skill_results.append({
                "skill_id": skill_id,
                "skill_name": skill_metadata.get("label", "Unknown Skill"),
                "relevance_score": round(score, 3),
                "description": skill_metadata.get("description", "")[:100] + "..."  # Truncate long descriptions
            })
        
        return skill_results
        
    except Exception as e:
        logger.error(f"Error in GraphSAGE skill extraction: {str(e)}")
        # Return empty list on error
        return []

@router.get("/recommendations", response_model=List[Dict[str, Any]])
def read_career_recommendations(
    limit: int = Query(30, gt=0, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized career recommendations for the current user.
    These are swipeable recommendations in the "Find Your Way" tab.
    """
    try:
        recommendations = get_career_recommendations(db, current_user.id, limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error retrieving career recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve career recommendations: {str(e)}"
        )

@router.post("/save/{career_id}", response_model=Dict[str, Any])
def save_career(
    career_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a career recommendation for the current user.
    This happens when the user swipes right on a career in the "Find Your Way" tab.
    """
    try:
        success = save_career_recommendation(db, current_user.id, career_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to save career recommendation"
            )
        
        return {"success": True, "message": "Career saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving career recommendation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save career recommendation: {str(e)}"
        )

@router.get("/saved", response_model=List[Dict[str, Any]])
def read_saved_careers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved career recommendations for the current user.
    These appear in the "My Space" section.
    
    Returns both:
    - ESCO jobs: From saved_recommendations table (home page recommendations)  
    - OaSIS jobs: From saved_jobs table (SwipeMyWay/Find Your Way discoveries)
    
    OaSIS jobs get GraphSAGE skill extraction, ESCO jobs show full analysis.
    """
    try:
        # Get ESCO saved careers from saved_recommendations table (home page recommendations)
        esco_careers = get_saved_careers(db, current_user.id)
        
        # Get OaSIS saved jobs from saved_jobs table (SwipeMyWay discoveries)
        from sqlalchemy import text
        oasis_query = text("""
            SELECT 
                id,
                esco_id,
                job_title,
                skills_required,
                discovery_source,
                tree_graph_id,
                relevance_score,
                saved_at,
                metadata
            FROM saved_jobs
            WHERE user_id = :user_id
            ORDER BY saved_at DESC
        """)
        
        oasis_results = db.execute(oasis_query, {"user_id": current_user.id}).fetchall()
        
        # Format OaSIS jobs to match the expected structure
        oasis_careers = []
        for row in oasis_results:
            oasis_job = {
                "id": f"oasis_{row.id}",  # Prefix to distinguish from ESCO
                "esco_id": row.esco_id,  # OaSIS jobs use ESCO IDs
                "oasis_code": row.esco_id,  # Use ESCO ID as OaSIS code for consistency
                "title": row.job_title,
                "label": row.job_title if row.job_title else f"OaSIS Job {row.id}",  # Ensure label is never empty
                "description": row.metadata.get("description", "") if row.metadata else "",
                "main_duties": row.metadata.get("main_duties", "") if row.metadata else "",
                "skills_required": row.skills_required or [],
                "discovery_source": row.discovery_source,
                "tree_graph_id": str(row.tree_graph_id) if row.tree_graph_id else None,
                "relevance_score": float(row.relevance_score) if row.relevance_score else None,
                "saved_at": row.saved_at.isoformat() if row.saved_at else None,
                "source": "swipemyway",  # SwipeMyWay source
                "source_type": "oasis",
                "metadata": row.metadata or {},
                "graphsage_skills": []  # Will be populated below
            }
            
            # Extract top 5 skills using GraphSAGE for OaSIS jobs
            if row.esco_id:
                try:
                    # GraphSAGE skill extraction for OaSIS jobs
                    top_skills = extract_job_skills_graphsage_sync(
                        row.esco_id,
                        row.job_title,
                        row.metadata.get("description", "") if row.metadata else ""
                    )
                    oasis_job["graphsage_skills"] = top_skills[:5]  # Top 5 skills
                except Exception as e:
                    logger.error(f"Error extracting GraphSAGE skills for OaSIS job {row.esco_id}: {str(e)}")
                    oasis_job["graphsage_skills"] = []
            
            oasis_careers.append(oasis_job)
        
        # ESCO jobs get full analysis (from home page recommendations)
        for career in esco_careers:
            career["source_type"] = "esco"  # Home page recommendations
            career["source"] = "recommendations"
            # ESCO jobs already have full skill analysis from saved_recommendations
        
        # Return combined list as flat array
        all_careers = esco_careers + oasis_careers
        
        logger.info(f"Retrieved {len(esco_careers)} ESCO and {len(oasis_careers)} OaSIS careers for user {current_user.id}")
        return all_careers
        
    except Exception as e:
        logger.error(f"Error retrieving saved careers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve saved careers: {str(e)}"
        )

# Career Fit Analysis Endpoint
from pydantic import BaseModel

class CareerFitRequest(BaseModel):
    job_id: str
    job_source: str  # "esco" or "oasis"

class SkillMatch(BaseModel):
    skill_name: str
    user_level: Optional[float]
    required_level: Optional[float]
    match_percentage: float
    
class CareerFitResponse(BaseModel):
    fit_score: float
    skill_match: Dict[str, SkillMatch]
    gap_analysis: Dict[str, Any]
    recommendations: List[str]

@router.post("/fit-analysis", response_model=CareerFitResponse)
async def analyze_career_fit(
    request: CareerFitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate career fit based on user profile and job requirements.
    Analyzes skill gaps, cognitive trait alignment, and provides recommendations.
    """
    try:
        # Get user skills and profile
        from ..models import UserSkill, UserProfile
        user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not user_skills:
            raise HTTPException(
                status_code=400,
                detail="User skills not found. Please complete your profile first."
            )
        
        # Get job details based on source
        job_details = None
        if request.job_source == "esco":
            # ESCO jobs are in saved_recommendations table (home page recommendations)
            from sqlalchemy import text
            query = text("""
                SELECT oasis_code, label, description, main_duties,
                       role_creativity, role_leadership, role_digital_literacy,
                       role_critical_thinking, role_problem_solving,
                       analytical_thinking, attention_to_detail, collaboration,
                       adaptability, independence, evaluation, decision_making,
                       stress_tolerance
                FROM saved_recommendations
                WHERE oasis_code = :job_id
                LIMIT 1
            """)
            result = db.execute(query, {"job_id": request.job_id}).fetchone()
            
            if result:
                job_details = {
                    "id": result.oasis_code,
                    "title": result.label,
                    "description": result.description,
                    "main_duties": result.main_duties,
                    "skills": {
                        "creativity": result.role_creativity,
                        "leadership": result.role_leadership,
                        "digital_literacy": result.role_digital_literacy,
                        "critical_thinking": result.role_critical_thinking,
                        "problem_solving": result.role_problem_solving
                    },
                    "cognitive_traits": {
                        "analytical_thinking": result.analytical_thinking,
                        "attention_to_detail": result.attention_to_detail,
                        "collaboration": result.collaboration,
                        "adaptability": result.adaptability,
                        "independence": result.independence,
                        "evaluation": result.evaluation,
                        "decision_making": result.decision_making,
                        "stress_tolerance": result.stress_tolerance
                    }
                }
                
        elif request.job_source == "oasis":
            # OaSIS jobs are in saved_jobs table (SwipeMyWay discoveries)
            from sqlalchemy import text
            query = text("""
                SELECT esco_id, job_title, metadata
                FROM saved_jobs
                WHERE esco_id = :job_id
                LIMIT 1
            """)
            result = db.execute(query, {"job_id": request.job_id}).fetchone()
            
            if result:
                job_details = {
                    "id": result.esco_id,
                    "title": result.job_title,
                    "description": result.metadata.get("description", "") if result.metadata else "",
                    "skills": result.metadata.get("skills", {}) if result.metadata else {},
                    "cognitive_traits": {}  # OaSIS jobs might not have these
                }
        
        if not job_details:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found with ID {request.job_id}"
            )
        
        # Calculate skill matches
        skill_matches = {}
        total_match_score = 0
        skill_count = 0
        
        # Map user skills to job requirements
        skill_mapping = {
            "creativity": "creativity",
            "leadership": "leadership", 
            "digital_literacy": "digital_literacy",
            "critical_thinking": "critical_thinking",
            "problem_solving": "problem_solving"
        }
        
        for user_skill_attr, job_skill_key in skill_mapping.items():
            user_level = getattr(user_skills, user_skill_attr)
            job_level = job_details.get("skills", {}).get(job_skill_key)
            
            if user_level is not None and job_level is not None:
                match_percentage = min(100, (user_level / job_level) * 100) if job_level > 0 else 100
                skill_matches[job_skill_key] = SkillMatch(
                    skill_name=job_skill_key.replace("_", " ").title(),
                    user_level=user_level,
                    required_level=job_level,
                    match_percentage=match_percentage
                )
                total_match_score += match_percentage
                skill_count += 1
        
        # Calculate overall fit score
        skill_fit_score = total_match_score / skill_count if skill_count > 0 else 0
        
        # Add cognitive trait matching if available
        cognitive_fit_score = 0
        cognitive_count = 0
        cognitive_mapping = {
            "analytical_thinking": "analytical_thinking",
            "attention_to_detail": "attention_to_detail",
            "collaboration": "collaboration",
            "adaptability": "adaptability",
            "independence": "independence",
            "evaluation": "evaluation",
            "decision_making": "decision_making",
            "stress_tolerance": "stress_tolerance"
        }
        
        for user_attr, job_attr in cognitive_mapping.items():
            user_trait = getattr(user_skills, user_attr)
            job_trait = job_details.get("cognitive_traits", {}).get(job_attr)
            
            if user_trait is not None and job_trait is not None:
                trait_match = min(100, (user_trait / job_trait) * 100) if job_trait > 0 else 100
                cognitive_fit_score += trait_match
                cognitive_count += 1
        
        if cognitive_count > 0:
            cognitive_fit_score = cognitive_fit_score / cognitive_count
            # Weighted average: 60% skills, 40% cognitive traits
            overall_fit_score = (skill_fit_score * 0.6) + (cognitive_fit_score * 0.4)
        else:
            overall_fit_score = skill_fit_score
        
        # Gap analysis
        gap_analysis = {
            "skill_gaps": [],
            "strength_areas": [],
            "improvement_areas": []
        }
        
        for skill_name, match in skill_matches.items():
            if match.match_percentage < 70:
                gap_analysis["skill_gaps"].append({
                    "skill": match.skill_name,
                    "current": match.user_level,
                    "required": match.required_level,
                    "gap": match.required_level - match.user_level if match.user_level and match.required_level else 0
                })
            elif match.match_percentage >= 90:
                gap_analysis["strength_areas"].append(match.skill_name)
            else:
                gap_analysis["improvement_areas"].append(match.skill_name)
        
        # Generate recommendations
        recommendations = []
        if overall_fit_score >= 80:
            recommendations.append(f"Excellent fit! Your profile aligns well with {job_details['title']}.")
        elif overall_fit_score >= 60:
            recommendations.append(f"Good potential fit for {job_details['title']} with some skill development.")
        else:
            recommendations.append(f"Consider building more skills before pursuing {job_details['title']}.")
        
        # Specific skill recommendations
        for gap in gap_analysis["skill_gaps"]:
            recommendations.append(f"Focus on improving {gap['skill']} (current: {gap['current']}/5, required: {gap['required']}/5)")
        
        # Career path recommendation
        if user_profile and user_profile.years_experience:
            if user_profile.years_experience < 2 and overall_fit_score < 60:
                recommendations.append("Consider entry-level positions or internships to build experience.")
            elif user_profile.years_experience >= 5 and overall_fit_score >= 80:
                recommendations.append("Your experience level matches well with this role.")
        
        return CareerFitResponse(
            fit_score=round(overall_fit_score, 2),
            skill_match=skill_matches,
            gap_analysis=gap_analysis,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in career fit analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze career fit: {str(e)}"
        )

@router.delete("/cleanup-test-jobs")
async def cleanup_test_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cleanup fake test jobs that start with 'occupation::key_' from saved_recommendations.
    These are dummy jobs created during development/testing.
    """
    try:
        from sqlalchemy import text
        
        # Delete fake ESCO jobs (starting with occupation::key_)
        delete_query = text("""
            DELETE FROM saved_recommendations 
            WHERE user_id = :user_id 
            AND oasis_code LIKE 'occupation::key_%'
        """)
        result = db.execute(delete_query, {"user_id": current_user.id})
        deleted_count = result.rowcount
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} fake test jobs for user {current_user.id}")
        
        return {
            "success": True,
            "message": f"Removed {deleted_count} test jobs",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up test jobs: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup test jobs: {str(e)}"
        )
