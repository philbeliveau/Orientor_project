"""
Career Goals Router - API endpoints for managing user career goals
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import logging

from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User, CareerGoal, CareerMilestone
from app.services.career_progression_service import CareerProgressionService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/career-goals", tags=["career-goals"])

# Pydantic schemas
class CareerGoalCreate(BaseModel):
    esco_occupation_id: Optional[str] = None
    oasis_code: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    source: Optional[str] = Field(None, description="Where goal was set from: oasis, saved, swipe, tree")
    source_metadata: Optional[dict] = None

class CareerGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class CareerGoalResponse(BaseModel):
    id: int
    user_id: int
    esco_occupation_id: Optional[str]
    oasis_code: Optional[str]
    title: str
    description: Optional[str]
    target_date: Optional[datetime]
    is_active: bool
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    achieved_at: Optional[datetime]
    source: Optional[str]
    milestones_count: int = 0
    completed_milestones: int = 0

    class Config:
        from_attributes = True

class MilestoneResponse(BaseModel):
    id: int
    skill_id: str
    skill_name: str
    tier_level: int
    is_completed: bool
    confidence_score: float
    xp_value: int
    
    class Config:
        from_attributes = True

# Initialize services
career_progression_service = CareerProgressionService()

@router.post("/", response_model=dict)
async def create_career_goal(
    goal_data: CareerGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new career goal from any job card in the platform.
    Deactivates previous goals and generates GraphSage timeline.
    """
    try:
        # Validate that at least one identifier is provided
        if not goal_data.esco_occupation_id and not goal_data.oasis_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either esco_occupation_id or oasis_code must be provided"
            )
        
        # Deactivate all previous goals for this user
        db.query(CareerGoal).filter(
            CareerGoal.user_id == current_user.id,
            CareerGoal.is_active == True
        ).update({"is_active": False})
        
        # Set default target date if not provided (1 year from now)
        if not goal_data.target_date:
            goal_data.target_date = datetime.utcnow() + timedelta(days=365)
        
        # Create new career goal
        new_goal = CareerGoal(
            user_id=current_user.id,
            esco_occupation_id=goal_data.esco_occupation_id,
            oasis_code=goal_data.oasis_code,
            title=goal_data.title,
            description=goal_data.description,
            target_date=goal_data.target_date,
            source=goal_data.source,
            source_metadata=json.dumps(goal_data.source_metadata) if goal_data.source_metadata else None,
            is_active=True
        )
        
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        
        # Generate GraphSage timeline if ESCO ID is available
        timeline = None
        if goal_data.esco_occupation_id:
            try:
                progression_data = career_progression_service.extract_career_progression(
                    occupation_id=goal_data.esco_occupation_id,
                    user_id=current_user.id,
                    depth=3
                )
                
                # Create milestones from the progression tiers
                if progression_data and "tiers" in progression_data:
                    for tier in progression_data["tiers"]:
                        for skill in tier.get("skills", []):
                            milestone = CareerMilestone(
                                goal_id=new_goal.id,
                                skill_id=skill.get("id", ""),
                                skill_name=skill.get("label", ""),
                                tier_level=tier.get("tier_number", 1),
                                confidence_score=skill.get("graphsage_score", 0.0),
                                xp_value=100 * tier.get("tier_number", 1)  # Higher tiers = more XP
                            )
                            db.add(milestone)
                    
                    db.commit()
                    timeline = progression_data
                    
            except Exception as e:
                logger.error(f"Error generating GraphSage timeline: {str(e)}")
                # Continue without timeline - goal is still created
        
        # Prepare response
        goal_response = CareerGoalResponse.from_orm(new_goal)
        goal_response.milestones_count = db.query(CareerMilestone).filter(
            CareerMilestone.goal_id == new_goal.id
        ).count()
        
        return {
            "goal": goal_response,
            "timeline": timeline,
            "message": f"Career goal '{new_goal.title}' set successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error creating career goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create career goal: {str(e)}"
        )

@router.get("/active", response_model=dict)
async def get_active_career_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's currently active career goal with progression data.
    """
    try:
        # Get active goal
        active_goal = db.query(CareerGoal).filter(
            CareerGoal.user_id == current_user.id,
            CareerGoal.is_active == True
        ).first()
        
        if not active_goal:
            return {
                "goal": None,
                "progression": None,
                "milestones": [],
                "message": "No active career goal set"
            }
        
        # Get milestones
        milestones = db.query(CareerMilestone).filter(
            CareerMilestone.goal_id == active_goal.id
        ).order_by(
            CareerMilestone.tier_level,
            CareerMilestone.confidence_score.desc()
        ).all()
        
        # Calculate progress
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.is_completed)
        
        if total_milestones > 0:
            active_goal.progress_percentage = (completed_milestones / total_milestones) * 100
            db.commit()
        
        # Prepare goal response
        goal_response = CareerGoalResponse.from_orm(active_goal)
        goal_response.milestones_count = total_milestones
        goal_response.completed_milestones = completed_milestones
        
        # Get fresh progression data if ESCO ID available
        progression = None
        if active_goal.esco_occupation_id:
            try:
                progression = career_progression_service.extract_career_progression(
                    occupation_id=active_goal.esco_occupation_id,
                    user_id=current_user.id,
                    depth=3
                )
            except Exception as e:
                logger.error(f"Error fetching progression: {str(e)}")
        
        return {
            "goal": goal_response,
            "progression": progression,
            "milestones": [MilestoneResponse.from_orm(m) for m in milestones],
            "message": "Active goal retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting active goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active goal: {str(e)}"
        )

@router.get("/", response_model=List[CareerGoalResponse])
async def get_all_career_goals(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all career goals for the current user.
    """
    query = db.query(CareerGoal).filter(CareerGoal.user_id == current_user.id)
    
    if not include_inactive:
        query = query.filter(CareerGoal.is_active == True)
    
    goals = query.order_by(CareerGoal.created_at.desc()).all()
    
    # Add milestone counts to each goal
    goal_responses = []
    for goal in goals:
        goal_response = CareerGoalResponse.from_orm(goal)
        milestones = db.query(CareerMilestone).filter(
            CareerMilestone.goal_id == goal.id
        ).all()
        goal_response.milestones_count = len(milestones)
        goal_response.completed_milestones = sum(1 for m in milestones if m.is_completed)
        goal_responses.append(goal_response)
    
    return goal_responses

@router.put("/{goal_id}", response_model=CareerGoalResponse)
async def update_career_goal(
    goal_id: int,
    goal_update: CareerGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a career goal's details.
    """
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # If activating this goal, deactivate others
    if goal_update.is_active and not goal.is_active:
        db.query(CareerGoal).filter(
            CareerGoal.user_id == current_user.id,
            CareerGoal.is_active == True,
            CareerGoal.id != goal_id
        ).update({"is_active": False})
    
    # Update fields
    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    
    # Add milestone counts
    goal_response = CareerGoalResponse.from_orm(goal)
    milestones = db.query(CareerMilestone).filter(
        CareerMilestone.goal_id == goal.id
    ).all()
    goal_response.milestones_count = len(milestones)
    goal_response.completed_milestones = sum(1 for m in milestones if m.is_completed)
    
    return goal_response

@router.delete("/{goal_id}")
async def delete_career_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a career goal and all its milestones.
    """
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"message": f"Career goal '{goal.title}' deleted successfully"}

@router.post("/{goal_id}/milestones/{milestone_id}/complete")
async def complete_milestone(
    goal_id: int,
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a milestone as completed and award XP.
    """
    # Verify goal ownership
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # Get milestone
    milestone = db.query(CareerMilestone).filter(
        CareerMilestone.id == milestone_id,
        CareerMilestone.goal_id == goal_id
    ).first()
    
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    if milestone.is_completed:
        return {"message": "Milestone already completed", "xp_awarded": 0}
    
    # Mark as completed
    milestone.is_completed = True
    milestone.completed_at = datetime.utcnow()
    
    # Award XP (integrate with existing XP system if available)
    xp_awarded = milestone.xp_value
    if not milestone.xp_awarded:
        milestone.xp_awarded = True
        # TODO: Add XP to user's progress here
    
    # Update goal progress
    all_milestones = db.query(CareerMilestone).filter(
        CareerMilestone.goal_id == goal_id
    ).all()
    completed = sum(1 for m in all_milestones if m.is_completed)
    goal.progress_percentage = (completed / len(all_milestones)) * 100 if all_milestones else 0
    
    # Check if goal is achieved
    if goal.progress_percentage >= 100 and not goal.achieved_at:
        goal.achieved_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": f"Milestone '{milestone.skill_name}' completed!",
        "xp_awarded": xp_awarded,
        "goal_progress": goal.progress_percentage,
        "goal_achieved": goal.achieved_at is not None
    }

@router.get("/{goal_id}/milestones", response_model=List[MilestoneResponse])
async def get_goal_milestones(
    goal_id: int,
    tier_level: Optional[int] = None,
    completed_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all milestones for a specific goal.
    """
    # Verify goal ownership
    goal = db.query(CareerGoal).filter(
        CareerGoal.id == goal_id,
        CareerGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career goal not found"
        )
    
    # Build query
    query = db.query(CareerMilestone).filter(CareerMilestone.goal_id == goal_id)
    
    if tier_level is not None:
        query = query.filter(CareerMilestone.tier_level == tier_level)
    
    if completed_only:
        query = query.filter(CareerMilestone.is_completed == True)
    
    milestones = query.order_by(
        CareerMilestone.tier_level,
        CareerMilestone.confidence_score.desc()
    ).all()
    
    return [MilestoneResponse.from_orm(m) for m in milestones]