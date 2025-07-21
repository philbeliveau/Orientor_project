from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging
import json

from ..services.competenceTree import CompetenceTreeService
from ..utils.database import get_db
from ..utils.auth import get_current_user_unified as get_current_user
from ..models import User, UserSkillTree

# Configure logging
logger = logging.getLogger(__name__)

# Request schemas
class AnchorSkillsRequest(BaseModel):
    anchor_skills: List[str] = Field(..., min_items=5, max_items=5, description="Exactly 5 ESCO skill IDs")
    max_depth: int = Field(3, ge=1, le=6, description="Maximum tree depth")
    max_nodes: int = Field(50, ge=10, le=100, description="Maximum nodes in tree")
    include_occupations: bool = Field(True, description="Include occupation nodes")

router = APIRouter(
    prefix="/competence-tree",
    tags=["competence-tree"],
    dependencies=[Depends(get_current_user)],
)

# Global variable for lazy loading
_competence_tree_service = None

def get_competence_tree_service():
    """Get or initialize the competence tree service with lazy loading"""
    global _competence_tree_service
    if _competence_tree_service is None:
        _competence_tree_service = CompetenceTreeService()
    return _competence_tree_service

@router.post("/generate", response_model=Dict[str, Any])
def generate_competence_tree(
    max_depth: int = Query(3, gt=0, le=6, description="Maximum depth of skill tree traversal"),
    max_nodes: int = Query(50, gt=10, le=100, description="Maximum total nodes in the tree"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new competence tree for a user following palmier specification.
    
    Flow:
    1. Infer 5 anchor skills from user profile using LLM
    2. Format skills using ESCO templates
    3. Build tree structure using GraphSAGE traversal
    4. Apply gamification rules (70% hidden nodes)
    5. Save tree with competenceTree JSONB column
    6. Return graph_id for retrieval
    
    Args:
        max_depth: Maximum depth of the tree (1-6, default 3)
        max_nodes: Maximum total nodes in tree (5-30, default 20)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dict with graph_id for accessing the generated tree
    """
    logger.info(f"Request received to generate competence tree for user {current_user.id}")
    
    try:
        # Set response timeout handling
        import signal
        
        def timeout_handler(signum, frame):
            logger.warning(f"Competence tree generation timed out for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Tree generation is taking longer than expected. Please try again."
            )
        
        # Set a timeout (adjust as needed - this is for very long operations)
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(120)  # 2 minute timeout
        
        try:
            # Create the competence tree with reduced parameters to avoid timeout
            logger.info(f"Creating competence tree for user {current_user.id} with max_depth={max_depth}, max_nodes_per_level={max(5, min(8, max_nodes // max_depth))}")
            
            tree_data = get_competence_tree_service().create_skill_tree(
                db, 
                current_user.id,
                max_depth=max_depth,
                max_nodes_per_level=max(5, min(8, max_nodes // max_depth))  # Increase nodes per level for richer tree
            )
            
            if not tree_data:
                logger.error(f"create_skill_tree returned empty data for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create competence tree - no data returned"
                )
            
            # Log tree data structure before saving
            nodes_count = len(tree_data.get('nodes', []))
            edges_count = len(tree_data.get('edges', []))
            anchors_count = len(tree_data.get('anchors', []))
            anchor_metadata_count = len(tree_data.get('anchor_metadata', []))
            
            logger.info(f"Tree data created successfully: nodes={nodes_count}, edges={edges_count}, "
                       f"anchors={anchors_count}, anchor_metadata={anchor_metadata_count}")
            
            # Validate tree structure
            if nodes_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Generated tree has no nodes"
                )
            
            if anchors_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Generated tree has no anchor skills"
                )
            
            # Save the tree in the database
            logger.info(f"Saving competence tree to database for user {current_user.id}")
            graph_id = get_competence_tree_service().save_skill_tree(db, current_user.id, tree_data)
            
            if not graph_id:
                logger.error(f"save_skill_tree returned empty graph_id for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save competence tree to database"
                )
            
            logger.info(f"Competence tree saved successfully with graph_id: {graph_id}")
            
            # Return successful response
            response_data = {
                "graph_id": graph_id, 
                "message": "Competence tree generated successfully",
                "stats": {
                    "total_nodes": nodes_count,
                    "total_edges": edges_count,
                    "anchor_skills": anchors_count
                }
            }
            
            logger.info(f"Returning success response for user {current_user.id}: {response_data}")
            return response_data
            
        finally:
            # Cancel the timeout
            # signal.alarm(0)
            pass
            
    except HTTPException as he:
        logger.error(f"HTTP Exception in generate_competence_tree for user {current_user.id}: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error generating competence tree for user {current_user.id}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during tree generation: {str(e)}"
        )

@router.post("/generate-from-anchors", response_model=Dict[str, Any])
def generate_tree_from_anchors(
    request: AnchorSkillsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a competence tree from 5 specific anchor skills.
    
    This endpoint allows users to generate a competence tree based on
    5 pre-selected anchor skills (ESCO skill IDs).
    
    Args:
        request: Contains anchor_skills list with exactly 5 ESCO skill IDs
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dict with graph_id for accessing the generated tree
    """
    logger.info(f"Request to generate tree from anchor skills for user {current_user.id}")
    logger.info(f"Anchor skills provided: {request.anchor_skills}")
    
    try:
        # Validate anchor skills count (additional validation beyond Pydantic)
        if len(request.anchor_skills) != 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exactly 5 anchor skills required, got {len(request.anchor_skills)}"
            )
        
        # Check for duplicates
        if len(set(request.anchor_skills)) != len(request.anchor_skills):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate anchor skills provided. All 5 skills must be unique."
            )
        
        # Get or create the competence tree service
        tree_service = get_competence_tree_service()
        
        # Generate tree from the provided anchor skills
        logger.info(f"Creating tree from anchors with max_depth={request.max_depth}, max_nodes={request.max_nodes}")
        
        # Use the existing create_skill_tree method with anchor skills
        tree_data = tree_service.create_skill_tree_from_anchors(
            db,
            current_user.id,
            anchor_skills=request.anchor_skills,
            max_depth=request.max_depth,
            max_nodes_per_level=max(5, min(10, request.max_nodes // request.max_depth)),
            include_occupations=request.include_occupations
        )
        
        if not tree_data:
            logger.error(f"create_skill_tree_from_anchors returned empty data")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tree from anchor skills"
            )
        
        # Log tree statistics
        nodes_count = len(tree_data.get('nodes', []))
        edges_count = len(tree_data.get('edges', []))
        
        logger.info(f"Tree generated successfully: nodes={nodes_count}, edges={edges_count}")
        
        # Save the tree
        graph_id = tree_service.save_skill_tree(db, current_user.id, tree_data)
        
        if not graph_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save generated tree"
            )
        
        return {
            "graph_id": graph_id,
            "status": "success",
            "nodes_generated": nodes_count,
            "edges_generated": edges_count,
            "message": "Tree generated successfully from anchor skills"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating tree from anchors: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/anchor-skills", response_model=Dict[str, Any])
def get_user_anchor_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's anchor skills from their latest competence tree.
    
    Returns anchor skills without regenerating the tree if one exists.
    """
    logger.info(f"Request received to get anchor skills for user {current_user.id}")
    try:
        # Get the user's latest skill tree
        skill_tree = db.query(UserSkillTree).filter(
            UserSkillTree.user_id == current_user.id
        ).order_by(UserSkillTree.created_at.desc()).first()
        
        if not skill_tree:
            return {
                "anchor_skills": [],
                "message": "No competence tree found. Generate one first."
            }
        
        # Parse tree data
        tree_data = skill_tree.tree_data
        if isinstance(tree_data, str):
            tree_data = json.loads(tree_data)
        
        logger.info(f"Retrieved tree data for user {current_user.id}: "
                   f"nodes={len(tree_data.get('nodes', []))}, "
                   f"anchors={len(tree_data.get('anchors', []))}, "
                   f"anchor_metadata={len(tree_data.get('anchor_metadata', []))}")
        
        anchor_metadata = tree_data.get("anchor_metadata", [])
        
        return {
            "anchor_skills": anchor_metadata,
            "graph_id": skill_tree.graph_id,
            "message": f"Found {len(anchor_metadata)} anchor skills"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving anchor skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving anchor skills: {str(e)}"
        )

@router.get("/{graph_id}")
def get_competence_tree(
    graph_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an existing competence tree.
    """
    logger.info(f"Request received to get competence tree with ID {graph_id}")
    try:
        # Get the competence tree from the database
        logger.info(f"Retrieving competence tree {graph_id} from database")
        skill_tree = db.query(UserSkillTree).filter(
            UserSkillTree.graph_id == graph_id,
            UserSkillTree.user_id == current_user.id
        ).first()
        
        if not skill_tree:
            logger.warning(f"Competence tree not found for graph_id: {graph_id} and user_id: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competence tree with ID {graph_id} not found for user {current_user.id}"
            )
        
        # Log the type and content of tree_data for debugging
        logger.info(f"Type of tree_data: {type(skill_tree.tree_data)}")
        
        try:
            # Handle different types of tree_data
            if isinstance(skill_tree.tree_data, str):
                # If it's a string, parse it as JSON
                tree_data = json.loads(skill_tree.tree_data)
            else:
                # If it's already a dict (JSONB), use it directly
                tree_data = skill_tree.tree_data
            
            # Log what we're actually returning
            logger.info(f"Returning tree data with {len(tree_data.get('nodes', []))} nodes and {len(tree_data.get('edges', []))} edges")
            logger.info(f"Tree data keys: {list(tree_data.keys())}")
            
            # Sample some nodes and edges for debugging
            nodes = tree_data.get('nodes', [])
            edges = tree_data.get('edges', [])
            
            if nodes:
                logger.info(f"Sample node: {nodes[0]}")
                anchor_nodes = [n for n in nodes if n.get('is_anchor')]
                non_anchor_nodes = [n for n in nodes if not n.get('is_anchor')]
                logger.info(f"Anchor nodes: {len(anchor_nodes)}, Non-anchor nodes: {len(non_anchor_nodes)}")
            
            if edges:
                logger.info(f"Sample edge: {edges[0]}")
                edge_types = {}
                for edge in edges:
                    edge_type = edge.get('type', 'unknown')
                    edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                logger.info(f"Edge types: {edge_types}")
            
            # Return as JSONResponse to ensure proper serialization
            return JSONResponse(content=tree_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from tree_data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decoding competence tree data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error processing tree data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing competence tree data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving competence tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving competence tree: {str(e)}"
        )

@router.patch("/node/{node_id}/complete", response_model=Dict[str, Any])
def complete_challenge(
    node_id: str,  # Changed to string to match ESCO node IDs
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a node challenge as completed following palmier specification.
    
    Flow:
    1. Mark node state as completed
    2. Update user_progress.total_xp
    3. Add completion timestamp
    4. Reveal children nodes (set visible=true)
    5. Update user skill tree in database
    
    Args:
        node_id: ESCO node ID to mark as completed
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success status and updated node information
    """
    logger.info(f"Request received to complete challenge {node_id} for user {current_user.id}")
    try:
        # Complete the challenge using the new service method
        logger.info(f"Marking challenge {node_id} as completed for user {current_user.id}")
        result = get_competence_tree_service().complete_challenge(db, node_id, current_user.id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", f"Could not complete challenge for node {node_id}")
            )
        
        # Log the completion
        logger.info(f"Challenge {node_id} completed successfully for user {current_user.id}: "
                   f"+{result.get('xp_earned', 0)} XP, {result.get('children_revealed', 0)} children revealed")
        
        return {
            "success": True, 
            "message": "Challenge completed successfully",
            "xp_earned": result.get("xp_earned", 0),
            "total_xp": result.get("total_xp", 0),
            "level": result.get("level", 1),
            "children_revealed": result.get("children_revealed", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing challenge: {str(e)}"
        )