from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from ..utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from ..models import User, SavedRecommendation, UserNote, UserSkill, UserProfile
from ..schemas.space import (
    SavedRecommendationCreate, SavedRecommendation as SavedRecommendationSchema,
    UserNoteCreate, UserNoteUpdate, UserNote as UserNoteSchema,
    UserSkillUpdate,
    RecommendationWithNotes, SkillComparison, SkillsComparison, CognitiveTraits
)
from ..services.llm_analysis_service import update_recommendation_analysis, generate_personalized_analysis

router = APIRouter(
    prefix="/space",
    tags=["space"],
    dependencies=[Depends(get_current_user)]
)

# Helper function to extract skill values from text
def extract_skill_values(text: str) -> dict:
    skill_values = {
        "creativity": None,
        "leadership": None,
        "digital_literacy": None,
        "critical_thinking": None,
        "problem_solving": None
    }
    
    # Parse the text to find skill values (format: "Skill: 4")
    for skill in skill_values.keys():
        # Handle the case of digital literacy which has a space
        pattern = f"{skill.replace('_', ' ').title()}: (\\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skill_values[skill] = float(match.group(1))
    
    return skill_values

# ===== Saved Recommendations Endpoints =====
@router.post("/recommendations", response_model=SavedRecommendationSchema)
def create_saved_recommendation(
    recommendation: SavedRecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Creating recommendation for user {current_user.id} with oasis_code: {recommendation.oasis_code}")
    logger.info(f"Recommendation data: {recommendation.dict()}")
    
    # Check if recommendation already exists
    db_recommendation = db.query(SavedRecommendation).filter(
        SavedRecommendation.user_id == current_user.id,
        SavedRecommendation.oasis_code == recommendation.oasis_code
    ).first()
    
    if db_recommendation:
        logger.info(f"Recommendation already exists for user {current_user.id}, oasis_code: {recommendation.oasis_code}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This recommendation is already saved."
        )
    
    try:
        # Create new saved recommendation
        db_recommendation = SavedRecommendation(
            user_id=current_user.id,
            oasis_code=recommendation.oasis_code,
            label=recommendation.label,
            description=recommendation.description,
            main_duties=recommendation.main_duties,
            role_creativity=recommendation.role_creativity,
            role_leadership=recommendation.role_leadership,
            role_digital_literacy=recommendation.role_digital_literacy,
            role_critical_thinking=recommendation.role_critical_thinking,
            role_problem_solving=recommendation.role_problem_solving,
            analytical_thinking=recommendation.analytical_thinking,
            attention_to_detail=recommendation.attention_to_detail,
            collaboration=recommendation.collaboration,
            adaptability=recommendation.adaptability,
            independence=recommendation.independence,
            evaluation=recommendation.evaluation,
            decision_making=recommendation.decision_making,
            stress_tolerance=recommendation.stress_tolerance,
            all_fields=recommendation.all_fields
        )
        
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        logger.info(f"Successfully created recommendation with ID: {db_recommendation.id}")
        
        # Generate LLM analysis for the recommendation asynchronously
        try:
            import asyncio
            # Run the async function in a sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(
                generate_personalized_analysis(current_user.id, db_recommendation, db)
            )
            loop.close()
            
            # Update the recommendation with the analysis
            db_recommendation.personal_analysis = analysis['personal_analysis']
            db_recommendation.entry_qualifications = analysis['entry_qualifications']
            db_recommendation.suggested_improvements = analysis['suggested_improvements']
            db.commit()
            db.refresh(db_recommendation)
            logger.info(f"Successfully generated LLM analysis for recommendation {db_recommendation.id}")
        except Exception as e:
            logger.error(f"Failed to generate LLM analysis: {str(e)}")
            # Continue without analysis if it fails
        
        return db_recommendation
        
    except Exception as e:
        logger.error(f"Failed to create recommendation: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recommendation: {str(e)}"
        )

@router.get("/recommendations", response_model=List[RecommendationWithNotes])
def get_saved_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get user's saved recommendations
    recommendations = db.query(SavedRecommendation).filter(
        SavedRecommendation.user_id == current_user.id
    ).all()
    
    logger.info(f"Found {len(recommendations)} recommendations for user {current_user.id}")
    
    # Get the user's skills and cognitive traits
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
    
    result = []
    for rec in recommendations:
        # Get notes for this recommendation
        notes = db.query(UserNote).filter(
            UserNote.user_id == current_user.id,
            UserNote.saved_recommendation_id == rec.id
        ).all()
        
        # Build skill comparison if both user and role skills are available
        skill_comparison = None
        if user_skills:
            # Add user's cognitive traits to the recommendation
            rec.user_analytical_thinking = user_skills.analytical_thinking
            rec.user_attention_to_detail = user_skills.attention_to_detail
            rec.user_collaboration = user_skills.collaboration
            rec.user_adaptability = user_skills.adaptability
            rec.user_independence = user_skills.independence
            rec.user_evaluation = user_skills.evaluation
            rec.user_decision_making = user_skills.decision_making
            rec.user_stress_tolerance = user_skills.stress_tolerance
            
            # Build skill comparison
            if (user_skills.creativity is not None or user_skills.leadership is not None or \
                user_skills.digital_literacy is not None or user_skills.critical_thinking is not None or \
                user_skills.problem_solving is not None):
                
                comparison = {}
                for skill in ["creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving"]:
                    role_skill_name = f"role_{skill}"
                    comparison[skill] = SkillComparison(
                        user_skill=getattr(user_skills, skill),
                        role_skill=getattr(rec, role_skill_name)
                    )
                
                skill_comparison = SkillsComparison(**comparison)
        
        # Create recommendation with notes
        recommendation_with_notes = RecommendationWithNotes(
            id=rec.id,
            user_id=rec.user_id,
            oasis_code=rec.oasis_code,
            label=rec.label,
            description=rec.description,
            main_duties=rec.main_duties,
            role_creativity=rec.role_creativity,
            role_leadership=rec.role_leadership,
            role_digital_literacy=rec.role_digital_literacy,
            role_critical_thinking=rec.role_critical_thinking,
            role_problem_solving=rec.role_problem_solving,
            analytical_thinking=rec.analytical_thinking,
            attention_to_detail=rec.attention_to_detail,
            collaboration=rec.collaboration,
            adaptability=rec.adaptability,
            independence=rec.independence,
            evaluation=rec.evaluation,
            decision_making=rec.decision_making,
            stress_tolerance=rec.stress_tolerance,
            user_analytical_thinking=rec.user_analytical_thinking,
            user_attention_to_detail=rec.user_attention_to_detail,
            user_collaboration=rec.user_collaboration,
            user_adaptability=rec.user_adaptability,
            user_independence=rec.user_independence,
            user_evaluation=rec.user_evaluation,
            user_decision_making=rec.user_decision_making,
            user_stress_tolerance=rec.user_stress_tolerance,
            saved_at=rec.saved_at,
            notes=notes,
            skill_comparison=skill_comparison,
            personal_analysis=rec.personal_analysis,
            entry_qualifications=rec.entry_qualifications,
            suggested_improvements=rec.suggested_improvements
        )
        
        result.append(recommendation_with_notes)
    
    return result

@router.delete("/recommendations/{identifier}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_recommendation(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Try to parse as integer first (for backward compatibility)
    recommendation = None
    
    try:
        # Try as integer ID first
        recommendation_id = int(identifier)
        recommendation = db.query(SavedRecommendation).filter(
            SavedRecommendation.id == recommendation_id,
            SavedRecommendation.user_id == current_user.id
        ).first()
    except ValueError:
        # If not an integer, treat as OASIS code
        recommendation = db.query(SavedRecommendation).filter(
            SavedRecommendation.oasis_code == identifier,
            SavedRecommendation.user_id == current_user.id
        ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Delete the recommendation (cascade will also delete associated notes)
    db.delete(recommendation)
    db.commit()
    
    return None

# ===== User Notes Endpoints =====
@router.post("/notes", response_model=UserNoteSchema)
def create_note(
    note: UserNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If note is associated with a recommendation, verify it exists and belongs to user
    if note.saved_recommendation_id:
        recommendation = db.query(SavedRecommendation).filter(
            SavedRecommendation.id == note.saved_recommendation_id,
            SavedRecommendation.user_id == current_user.id
        ).first()
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved recommendation not found"
            )
    
    # Create the note
    db_note = UserNote(
        user_id=current_user.id,
        saved_recommendation_id=note.saved_recommendation_id,
        content=note.content
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.get("/notes", response_model=List[UserNoteSchema])
def get_notes(
    saved_recommendation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query for user's notes
    query = db.query(UserNote).filter(UserNote.user_id == current_user.id)
    
    # Filter by recommendation if specified
    if saved_recommendation_id is not None:
        query = query.filter(UserNote.saved_recommendation_id == saved_recommendation_id)
    
    return query.all()

@router.put("/notes/{note_id}", response_model=UserNoteSchema)
def update_note(
    note_id: int,
    note_update: UserNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the note
    db_note = db.query(UserNote).filter(
        UserNote.id == note_id,
        UserNote.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields if provided
    if note_update.content is not None:
        db_note.content = note_update.content
    
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the note
    db_note = db.query(UserNote).filter(
        UserNote.id == note_id,
        UserNote.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Delete the note
    db.delete(db_note)
    db.commit()
    
    return None

# ===== User Skills Endpoints =====
@router.get("/skills", response_model=UserSkillUpdate)
def get_user_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user's skills record
    user_skill = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
    if not user_skill:
        # Return default values if no record exists
        return UserSkillUpdate()
    
    # Return the skills
    return UserSkillUpdate(
        creativity=user_skill.creativity,
        leadership=user_skill.leadership,
        digital_literacy=user_skill.digital_literacy,
        critical_thinking=user_skill.critical_thinking,
        problem_solving=user_skill.problem_solving,
        analytical_thinking=user_skill.analytical_thinking,
        attention_to_detail=user_skill.attention_to_detail,
        collaboration=user_skill.collaboration,
        adaptability=user_skill.adaptability,
        independence=user_skill.independence,
        evaluation=user_skill.evaluation,
        decision_making=user_skill.decision_making,
        stress_tolerance=user_skill.stress_tolerance
    )

@router.put("/skills", response_model=UserSkillUpdate)
def update_user_skills(
    skills: UserSkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get or create the user's skills record
    user_skill = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
    if not user_skill:
        # Create a new user skills record if it doesn't exist
        user_skill = UserSkill(user_id=current_user.id)
        db.add(user_skill)
    
    # Update skill values if provided
    updated = False
    for field in [
        "creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving",
        "analytical_thinking", "attention_to_detail", "collaboration", "adaptability",
        "independence", "evaluation", "decision_making", "stress_tolerance"
    ]:
        value = getattr(skills, field)
        if value is not None:
            setattr(user_skill, field, value)
            updated = True
    
    if updated:
        db.commit()
        db.refresh(user_skill)
    
    # Return the updated skills
    return UserSkillUpdate(
        creativity=user_skill.creativity,
        leadership=user_skill.leadership,
        digital_literacy=user_skill.digital_literacy,
        critical_thinking=user_skill.critical_thinking,
        problem_solving=user_skill.problem_solving,
        analytical_thinking=user_skill.analytical_thinking,
        attention_to_detail=user_skill.attention_to_detail,
        collaboration=user_skill.collaboration,
        adaptability=user_skill.adaptability,
        independence=user_skill.independence,
        evaluation=user_skill.evaluation,
        decision_making=user_skill.decision_making,
        stress_tolerance=user_skill.stress_tolerance
    )

# ===== Special Endpoints =====
@router.get("/recommendations/{oasis_code}/skill-comparison", response_model=SkillsComparison)
def get_skill_comparison(
    oasis_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get recommendation for this oasis_code
    recommendation = db.query(SavedRecommendation).filter(
        SavedRecommendation.oasis_code == oasis_code
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Get user's skills
    user_skill = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
    if not user_skill:
        user_skill = UserSkill(user_id=current_user.id)
        db.add(user_skill)
    
    # Build comparison
    comparison = {}
    for skill in ["creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving"]:
        role_skill_name = f"role_{skill}"
        comparison[skill] = SkillComparison(
            user_skill=getattr(user_skill, skill),
            role_skill=getattr(recommendation, role_skill_name)
        )
    
    return SkillsComparison(**comparison)

# ===== LLM Analysis Endpoints =====
@router.post("/recommendations/{recommendation_id}/generate-analysis", response_model=SavedRecommendationSchema)
async def generate_recommendation_analysis(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate or regenerate LLM analysis for a saved recommendation.
    """
    # Get the recommendation
    recommendation = db.query(SavedRecommendation).filter(
        SavedRecommendation.id == recommendation_id,
        SavedRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    try:
        # Generate the analysis
        updated_recommendation = await update_recommendation_analysis(
            recommendation_id=recommendation_id,
            user_id=current_user.id,
            db=db
        )
        
        return updated_recommendation
    except Exception as e:
        logger.error(f"Failed to generate analysis for recommendation {recommendation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analysis. Please try again later."
        ) 