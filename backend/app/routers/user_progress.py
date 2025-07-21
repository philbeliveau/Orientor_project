from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models.user import User
from app.models.user_progress import UserProgress
from app.schemas.tree import UserProgressCreate, UserProgressUpdate, UserProgress as UserProgressSchema
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user-progress",
    tags=["user-progress"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=UserProgressSchema)
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get existing progress or create new
    progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
    
    if not progress:
        # Initialize user progress
        progress = UserProgress(
            user_id=current_user.id,
            total_xp=0,
            level=1,
            completed_actions={}  # Initialize empty completed actions
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    logger.info(f"Retrieved user progress for user {current_user.id}: {progress.completed_actions}")
    return progress

@router.post("/update", response_model=UserProgressSchema)
async def update_user_progress(
    update: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Received update request for user {current_user.id}: {update}")
    
    # Get existing progress or create new
    progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
    
    if not progress:
        # Initialize user progress
        progress = UserProgress(
            user_id=current_user.id,
            total_xp=update.xp_gained,
            level=1,
            last_completed_node=update.node_id,
            completed_actions=update.completed_actions or {}
        )
        logger.info(f"Created new progress with completed_actions: {progress.completed_actions}")
    else:
        # Update existing progress
        progress.total_xp += update.xp_gained
        progress.last_completed_node = update.node_id
        
        # Update completed actions if provided
        if update.completed_actions:
            if not progress.completed_actions:
                progress.completed_actions = {}
            
            # Ensure we're working with a dictionary
            current_actions = progress.completed_actions if isinstance(progress.completed_actions, dict) else {}
            new_actions = update.completed_actions if isinstance(update.completed_actions, dict) else {}
            
            logger.info(f"Current completed_actions: {current_actions}")
            logger.info(f"Updating with new actions: {new_actions}")
            
            # Update the dictionary
            current_actions.update(new_actions)
            progress.completed_actions = current_actions
            
            logger.info(f"Updated completed_actions: {progress.completed_actions}")
        
        # Calculate level based on XP
        if progress.total_xp <= 50:
            progress.level = 1
        elif progress.total_xp <= 150:
            progress.level = 2
        elif progress.total_xp <= 300:
            progress.level = 3
        elif progress.total_xp <= 500:
            progress.level = 4
        elif progress.total_xp <= 750:
            progress.level = 5
        else:
            progress.level = 6
    
    try:
        db.add(progress)
        db.commit()
        db.refresh(progress)
        logger.info(f"Final progress state: {progress.completed_actions}")
        return progress
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        ) 