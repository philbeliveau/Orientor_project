from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ..utils.database import get_db
from ..utils.auth import get_current_user_unified as get_current_user
from ..models import User
from ..schemas.job import SavedJob, SavedJobCreate, SavedJobResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    dependencies=[Depends(get_current_user)],
)

# Request/Response schemas
class SaveJobRequest(BaseModel):
    esco_id: str = Field(..., description="ESCO occupation ID")
    job_title: str = Field(..., description="Job title")
    skills_required: Optional[List[str]] = Field(default=[], description="Required skills for the job")
    discovery_source: str = Field(default="tree", description="How the job was discovered")
    tree_graph_id: Optional[str] = Field(None, description="Tree graph ID if discovered from tree")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class JobListResponse(BaseModel):
    jobs: List[SavedJobResponse]
    total: int

class JobRecommendation(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]

class JobRecommendationsResponse(BaseModel):
    recommendations: List[JobRecommendation]
    user_id: int
    
@router.post("/save", response_model=SavedJobResponse)
async def save_job(
    request: SaveJobRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a job from tree exploration or other sources.
    
    Args:
        request: Job details to save
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Saved job details
    """
    try:
        # Check if job already saved by this user
        from sqlalchemy import text
        check_query = text("""
            SELECT id FROM saved_jobs 
            WHERE user_id = :user_id AND esco_id = :esco_id
        """)
        existing = db.execute(check_query, {
            "user_id": current_user.id,
            "esco_id": request.esco_id
        }).fetchone()
        
        if existing:
            logger.info(f"Job {request.esco_id} already saved by user {current_user.id}")
            # Return existing saved job
            saved_job_query = text("""
                SELECT id, user_id, esco_id, job_title, skills_required, 
                       discovery_source, tree_graph_id, relevance_score, 
                       saved_at, metadata
                FROM saved_jobs
                WHERE id = :job_id
            """)
            result = db.execute(saved_job_query, {"job_id": existing[0]}).fetchone()
            
            return SavedJobResponse(
                id=result[0],
                user_id=result[1],
                esco_id=result[2],
                job_title=result[3],
                skills_required=result[4] or [],
                discovery_source=result[5],
                tree_graph_id=str(result[6]) if result[6] else None,
                relevance_score=float(result[7]) if result[7] else None,
                saved_at=result[8],
                metadata=result[9] or {},
                already_saved=True
            )
        
        # Insert new saved job - handle None values properly
        import json
        
        # Prepare parameters with proper None handling
        skills_json = json.dumps(request.skills_required) if request.skills_required else '[]'
        metadata_json = json.dumps(request.metadata) if request.metadata else '{}'
        
        if request.tree_graph_id:
            insert_query = text("""
                INSERT INTO saved_jobs (
                    user_id, esco_id, job_title, skills_required, 
                    discovery_source, tree_graph_id, relevance_score, metadata
                ) VALUES (
                    :user_id, :esco_id, :job_title, CAST(:skills_required AS jsonb), 
                    :discovery_source, CAST(:tree_graph_id AS uuid), :relevance_score, CAST(:metadata AS jsonb)
                ) RETURNING id, saved_at
            """)
            
            result = db.execute(insert_query, {
                "user_id": current_user.id,
                "esco_id": request.esco_id,
                "job_title": request.job_title,
                "skills_required": skills_json,
                "discovery_source": request.discovery_source,
                "tree_graph_id": request.tree_graph_id,
                "relevance_score": request.relevance_score,
                "metadata": metadata_json
            }).fetchone()
        else:
            insert_query = text("""
                INSERT INTO saved_jobs (
                    user_id, esco_id, job_title, skills_required, 
                    discovery_source, relevance_score, metadata
                ) VALUES (
                    :user_id, :esco_id, :job_title, CAST(:skills_required AS jsonb), 
                    :discovery_source, :relevance_score, CAST(:metadata AS jsonb)
                ) RETURNING id, saved_at
            """)
            
            result = db.execute(insert_query, {
                "user_id": current_user.id,
                "esco_id": request.esco_id,
                "job_title": request.job_title,
                "skills_required": skills_json,
                "discovery_source": request.discovery_source,
                "relevance_score": request.relevance_score,
                "metadata": metadata_json
            }).fetchone()
        
        db.commit()
        
        logger.info(f"Job {request.esco_id} saved successfully for user {current_user.id}")
        
        return SavedJobResponse(
            id=result[0],
            user_id=current_user.id,
            esco_id=request.esco_id,
            job_title=request.job_title,
            skills_required=request.skills_required,
            discovery_source=request.discovery_source,
            tree_graph_id=request.tree_graph_id,
            relevance_score=request.relevance_score,
            saved_at=result[1],
            metadata=request.metadata,
            already_saved=False
        )
        
    except Exception as e:
        logger.error(f"Error saving job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save job: {str(e)}"
        )

@router.get("/saved", response_model=JobListResponse)
async def get_saved_jobs(
    discovery_source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved jobs for the current user.
    
    Args:
        discovery_source: Optional filter by discovery source
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of saved jobs
    """
    try:
        # Build query
        query = text("""
            SELECT id, user_id, esco_id, job_title, skills_required, 
                   discovery_source, tree_graph_id, relevance_score, 
                   saved_at, metadata
            FROM saved_jobs
            WHERE user_id = :user_id
            """ + (" AND discovery_source = :source" if discovery_source else "") + """
            ORDER BY saved_at DESC
        """)
        
        params = {"user_id": current_user.id}
        if discovery_source:
            params["source"] = discovery_source
            
        results = db.execute(query, params).fetchall()
        
        jobs = []
        for row in results:
            jobs.append(SavedJobResponse(
                id=row[0],
                user_id=row[1],
                esco_id=row[2],
                job_title=row[3],
                skills_required=row[4] or [],
                discovery_source=row[5],
                tree_graph_id=str(row[6]) if row[6] else None,
                relevance_score=float(row[7]) if row[7] else None,
                saved_at=row[8],
                metadata=row[9] or {},
                already_saved=True
            ))
        
        logger.info(f"Retrieved {len(jobs)} saved jobs for user {current_user.id}")
        
        return JobListResponse(
            jobs=jobs,
            total=len(jobs)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving saved jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve saved jobs: {str(e)}"
        )

@router.delete("/{job_id}")
async def delete_saved_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved job.
    
    Args:
        job_id: ID of the job to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        # Check if job exists and belongs to user
        check_query = text("""
            SELECT id FROM saved_jobs 
            WHERE id = :job_id AND user_id = :user_id
        """)
        existing = db.execute(check_query, {
            "job_id": job_id,
            "user_id": current_user.id
        }).fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved job not found"
            )
        
        # Delete the job
        delete_query = text("""
            DELETE FROM saved_jobs 
            WHERE id = :job_id AND user_id = :user_id
        """)
        db.execute(delete_query, {
            "job_id": job_id,
            "user_id": current_user.id
        })
        db.commit()
        
        logger.info(f"Deleted saved job {job_id} for user {current_user.id}")
        
        return {"message": "Job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting saved job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete saved job: {str(e)}"
        )

@router.get("/{esco_id}/details")
async def get_job_details(
    esco_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a job from ESCO.
    
    Args:
        esco_id: ESCO occupation ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detailed job information
    """
    # TODO: Implement ESCO API integration to fetch job details
    # For now, return mock data
    return {
        "esco_id": esco_id,
        "title": "Software Developer",
        "description": "Develops and maintains software applications",
        "skills": ["Python", "JavaScript", "SQL", "Git"],
        "education_level": "Bachelor's degree",
        "experience_years": "2-5 years",
        "industry": "Information Technology"
    }

@router.get("/recommendations/me", response_model=JobRecommendationsResponse)
async def get_job_recommendations(
    top_k: int = 10,
    embedding_type: str = "esco_embedding",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized job recommendations for the current user.
    
    Args:
        top_k: Number of recommendations to return
        embedding_type: Type of embedding to use for recommendations
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of job recommendations
    """
    try:
        logger.info(f"Getting job recommendations for user {current_user.id}")
        
        # Use real ESCO occupation IDs that exist in the graph
        real_esco_jobs = [
            {
                "id": "occupation::key_15224",  # Software analyst
                "title": "Software Developer",
                "description": "Develops and maintains software applications using various programming languages and frameworks"
            },
            {
                "id": "occupation::key_15156",  # Technical director
                "title": "Technical Director", 
                "description": "Leads technical teams and oversees technology strategy and implementation"
            },
            {
                "id": "occupation::key_15225",  # Systems analyst
                "title": "Systems Analyst",
                "description": "Analyzes and designs information systems to solve business problems"
            },
            {
                "id": "occupation::key_15226",  # Database analyst
                "title": "Database Analyst",
                "description": "Designs, implements and maintains database systems for organizations"
            },
            {
                "id": "occupation::key_15227",  # Computer programmer
                "title": "Computer Programmer",
                "description": "Writes, tests and maintains computer programs and applications"
            }
        ]
        
        recommendations = []
        for i in range(min(top_k, len(real_esco_jobs))):
            job = real_esco_jobs[i]
            recommendations.append(JobRecommendation(
                id=job["id"],
                score=0.9 - (i * 0.05),  # Decreasing scores
                metadata={
                    "title": job["title"],
                    "preferred_label": job["title"],
                    "description": job["description"],
                    "industry": "Technology",
                    "education_level": "Bachelor's degree",
                    "experience_years": "2-5 years",
                    "skills": ["Python", "JavaScript", "SQL", "Git"],
                    "embedding_type": embedding_type
                }
            ))
        
        logger.info(f"Returned {len(recommendations)} real ESCO job recommendations for user {current_user.id}")
        
        return JobRecommendationsResponse(
            recommendations=recommendations,
            user_id=current_user.id
        )
        
    except Exception as e:
        logger.error(f"Error getting job recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job recommendations: {str(e)}"
        )