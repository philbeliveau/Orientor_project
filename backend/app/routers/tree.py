from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
from app.schemas.tree import ProfileInput, TreeResponse, TreeNode, SkillsTreeInput
from app.services.LLMskillsTree import TreeService
from app.utils.auth import get_current_user_unified as get_current_user
import logging
import traceback
import json

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/tree",
    tags=["Skill Tree"],
    responses={404: {"description": "Not found"}},
)

# Initialize tree service
tree_service = TreeService()

# Make authentication optional
async def get_optional_current_user():
    try:
        return await get_current_user()
    except Exception as e:
        logger.info(f"No authentication provided: {str(e)}")
        return None


@router.post("", response_model=TreeResponse)
async def generate_tree(
    request: Request,
    profile_input: ProfileInput,
    current_user: Optional[dict] = Depends(get_optional_current_user)
) -> TreeResponse:
    """
    Generate a skill-to-career exploration tree based on the provided student profile.
    
    - **profile**: Student profile description (interests, traits, etc.)
    - Returns a structured tree with skills, outcomes, and careers.
    """
    request_id = id(request)
    client_host = request.client.host if request.client else "unknown"
    
    logger.info(f"[{request_id}] Tree generation request from {client_host}")
    logger.info(f"[{request_id}] Request profile: {profile_input.profile[:50]}...")
    logger.info(f"[{request_id}] Authenticated user: {current_user.get('id') if current_user else 'None'}")
    
    try:
        # Get user_id for caching if user is authenticated
        user_id = current_user.get("id") if current_user else None
        logger.info(f"[{request_id}] Using user_id for caching: {user_id}")
        
        # Generate tree
        logger.info(f"[{request_id}] Calling tree_service.generate_tree")
        tree = await tree_service.generate_tree(profile_input.profile, user_id)
        logger.info(f"[{request_id}] Tree generated successfully with root id: {tree.id}")
        
        return TreeResponse(tree=tree)
    
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"[{request_id}] Validation error: {error_msg}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating tree: {error_msg}"
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{request_id}] Unexpected error: {error_msg}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        
        # Try to provide more context about the error
        error_type = type(e).__name__
        error_context = {
            "error_type": error_type,
            "error_message": error_msg,
            "user_id": current_user.get("id") if current_user else None,
            "profile_length": len(profile_input.profile)
        }
        
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail=json.dumps({
                "message": "An unexpected error occurred while generating the tree.",
                "error_context": error_context
            })
        )

@router.post("/skills", response_model=TreeResponse)
async def generate_skills_tree(
    request: Request,
    skills_input: SkillsTreeInput,
    current_user: Optional[dict] = Depends(get_optional_current_user)
) -> TreeResponse:
    """
    Generate a technical skills tree based on the provided profile and custom prompt.
    
    - **profile**: User technical background and goals
    - **custom_prompt**: Custom prompt for generating a technical skills tree
    - Returns a structured tree with technical skills
    """
    request_id = id(request)
    client_host = request.client.host if request.client else "unknown"
    
    logger.info(f"[{request_id}] Skills tree generation request from {client_host}")
    logger.info(f"[{request_id}] Request profile: {skills_input.profile[:50]}...")
    logger.info(f"[{request_id}] Authenticated user: {current_user.get('id') if current_user else 'None'}")
    logger.info(f"[{request_id}] Custom prompt provided: {len(skills_input.custom_prompt) > 0}")
    
    try:
        # Get user_id for caching if user is authenticated
        user_id = current_user.get("id") if current_user else None
        logger.info(f"[{request_id}] Using user_id for caching: {user_id}")
        
        # Generate tree with custom prompt
        logger.info(f"[{request_id}] Calling tree_service.generate_custom_tree")
        tree = await tree_service.generate_custom_tree(
            profile=skills_input.profile, 
            custom_prompt=skills_input.custom_prompt, 
            user_id=user_id
        )
        logger.info(f"[{request_id}] Skills tree generated successfully with root id: {tree.id}")
        
        return TreeResponse(tree=tree)
    
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"[{request_id}] Validation error: {error_msg}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating skills tree: {error_msg}"
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{request_id}] Unexpected error: {error_msg}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        
        # Try to provide more context about the error
        error_type = type(e).__name__
        error_context = {
            "error_type": error_type,
            "error_message": error_msg,
            "user_id": current_user.get("id") if current_user else None,
            "profile_length": len(skills_input.profile)
        }
        
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail=json.dumps({
                "message": "An unexpected error occurred while generating the skills tree.",
                "error_context": error_context
            })
        ) 