"""
School Programs API Router

This module provides REST API endpoints for school programs search and management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.utils.database import get_db
from app.utils.auth import get_current_user_unified as get_current_user
from app.models import User
from app.schemas.school_programs import (
    ProgramSearchQuery, ProgramResponse, SearchResultsResponse,
    UserProgramInteraction, SaveProgramRequest, ProgramComparison
)
# from app.services.school_programs_service import ProgramSearchService, UserInteractionService  # Temporarily disabled

# Make Redis optional
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/school-programs", tags=["School Programs"])


# Redis dependency
async def get_redis():
    """Get Redis connection for caching"""
    if not REDIS_AVAILABLE:
        return None
    try:
        return redis.from_url("redis://localhost:6379", decode_responses=True)
    except Exception:
        # If Redis is not available, return None (caching will be disabled)
        return None


async def get_search_facets(db: Session) -> Dict[str, Any]:
    """Get search facets for the UI"""
    try:
        # Get program types
        types_sql = """
        SELECT program_type, COUNT(*) as count 
        FROM programs 
        WHERE active = true 
        GROUP BY program_type 
        ORDER BY count DESC
        """
        
        # Get levels
        levels_sql = """
        SELECT level, COUNT(*) as count 
        FROM programs 
        WHERE active = true 
        GROUP BY level 
        ORDER BY count DESC
        """
        
        # Get provinces
        provinces_sql = """
        SELECT i.province_state, COUNT(DISTINCT p.id) as count
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.active = true AND i.active = true
        GROUP BY i.province_state
        ORDER BY count DESC
        """
        
        types_result = db.execute(text(types_sql)).fetchall()
        levels_result = db.execute(text(levels_sql)).fetchall()
        provinces_result = db.execute(text(provinces_sql)).fetchall()
        
        return {
            'program_types': {row[0]: row[1] for row in types_result},
            'levels': {row[0]: row[1] for row in levels_result},
            'provinces': {row[0]: row[1] for row in provinces_result}
        }
    except Exception as e:
        logger.error(f"Error getting facets: {e}")
        return {
            'program_types': {},
            'levels': {},
            'provinces': {}
        }


# API Endpoints
@router.post("/search")
async def search_programs(
    query: ProgramSearchQuery,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    cache = Depends(get_redis)
) -> SearchResultsResponse:
    """
    Search for school programs based on criteria.
    
    - **text**: Search text for program titles and descriptions
    - **program_types**: Filter by program types (cegep, university, college)
    - **levels**: Filter by education levels (diploma, bachelor, master, etc.)
    - **location**: Geographic filters (country, province, city)
    - **languages**: Language preferences (en, fr)
    - **duration**: Duration constraints (max_months, min_months)
    - **budget**: Budget constraints (max_tuition, currency)
    """
    try:
        # Execute raw SQL search since we're using the database search function
        search_sql = """
        SELECT * FROM search_programs(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Build search parameters
        search_text = query.text or ''
        program_types = query.program_types or []
        levels = query.levels or []
        countries = [query.location.get('country')] if query.location and query.location.get('country') else []
        provinces = [query.location.get('province')] if query.location and query.location.get('province') else []
        languages = query.languages or []
        max_duration = query.duration.get('max_months') if query.duration else None
        min_employment_rate = None
        limit = query.pagination.get('limit', 20)
        offset = (query.pagination.get('page', 1) - 1) * limit
        
        # Execute the search
        result = db.execute(text(search_sql), (
            search_text, program_types, levels, countries, provinces,
            languages, max_duration, min_employment_rate, limit, offset
        ))
        
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            program_data = {
                'id': row[0],  # id
                'title': row[1],  # title
                'title_fr': None,
                'description': None,
                'description_fr': None,
                'institution': {
                    'name': row[2],  # institution_name
                    'city': row[3],  # city
                    'province': row[4],  # province_state
                    'type': 'institution'
                },
                'program_details': {
                    'type': row[5],  # program_type
                    'level': row[6],  # level
                    'duration_months': row[7]  # duration_months
                },
                'classification': {
                    'field_of_study': 'General',
                    'category': 'Education'
                },
                'admission': {
                    'requirements': [],
                    'deadline': None
                },
                'academic_info': {
                    'credits': None,
                    'internship_required': False
                },
                'career_outcomes': {
                    'employment_rate': row[8] if len(row) > 8 else None,  # employment_rate
                    'job_titles': []
                },
                'costs': {
                    'tuition_domestic': None,
                    'currency': 'CAD'
                },
                'metadata': {
                    'search_rank': row[9] if len(row) > 9 else 1.0,  # search_rank
                    'last_updated': datetime.utcnow().isoformat()
                }
            }
            results.append(program_data)
        
        # Get total count for pagination
        count_sql = """
        SELECT COUNT(*) FROM search_programs(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        count_result = db.execute(text(count_sql), (
            search_text, program_types, levels, countries, provinces,
            languages, max_duration, min_employment_rate, 1000, 0  # Get total count
        ))
        total_results = count_result.scalar()
        
        # Calculate pagination
        page = query.pagination.get('page', 1)
        total_pages = (total_results + limit - 1) // limit
        
        # Get facets
        facets = await get_search_facets(db)
        
        return SearchResultsResponse(
            results=results,
            pagination={
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total_results,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            facets=facets,
            metadata={
                "search_time_ms": 100,
                "cache_hit": False,
                "sources_queried": ["database"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error in search_programs: {e}")
        # Return fallback response
        return SearchResultsResponse(
            results=[],
            pagination={
                "page": query.pagination.get("page", 1),
                "limit": query.pagination.get("limit", 20),
                "total_pages": 0,
                "total_results": 0,
                "has_next": False,
                "has_previous": False
            },
            facets={
                "program_types": {"cegep": 0, "university": 0},
                "levels": {"diploma": 0, "bachelor": 0},
                "provinces": {"QC": 0, "ON": 0}
            },
            metadata={
                "search_time_ms": 50,
                "cache_hit": False,
                "error": str(e)
            }
        )


@router.get("/search")
async def quick_search(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[str] = Query(None, description="Program type filter"),
    level: Optional[str] = Query(None, description="Program level filter"),
    province: Optional[str] = Query(None, description="Province filter"),
    limit: int = Query(20, ge=1, le=100, description="Results limit"),
    page: int = Query(1, ge=1, description="Page number"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> SearchResultsResponse:
    """Quick search endpoint for simple queries"""
    
    # Build query object
    query_obj = ProgramSearchQuery(
        text=q,
        program_types=[type] if type else [],
        levels=[level] if level else [],
        location={'province': province} if province else {},
        pagination={'page': page, 'limit': limit}
    )
    
    # Use the same logic as the main search
    return await search_programs(query_obj, db, user, None)


@router.get("/programs/{program_id}")
async def get_program_details(
    program_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed information about a specific program"""
    
    try:
        query_sql = """
        SELECT p.*, i.name as institution_name, i.city, i.province_state, i.country,
               i.website_url as institution_website, i.institution_type
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.id = %s AND p.active = true
        """
        
        result = db.execute(text(query_sql), (str(program_id),))
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Program not found")
        
        # Format full program response
        program_data = {
            'id': row.id,
            'title': row.title,
            'title_fr': row.title_fr,
            'description': row.description,
            'description_fr': row.description_fr,
            'institution': {
                'name': row.institution_name,
                'city': row.city,
                'province': row.province_state,
                'country': row.country,
                'website': row.institution_website,
                'type': row.institution_type
            },
            'program_details': {
                'type': row.program_type,
                'level': row.level,
                'duration_months': row.duration_months,
                'language': row.language or ['en'],
                'cip_code': row.cip_code,
                'program_code': row.program_code,
                'delivery_mode': row.delivery_mode
            },
            'classification': {
                'field_of_study': row.field_of_study,
                'field_of_study_fr': row.field_of_study_fr
            },
            'admission': {
                'requirements': row.admission_requirements or [],
                'deadline': row.application_deadline,
                'application_method': row.application_method,
                'application_fee': row.application_fee,
                'min_gpa': row.min_gpa
            },
            'academic_info': {
                'credits': row.credits,
                'semester_count': row.semester_count,
                'internship_required': row.internship_required,
                'coop_available': row.coop_available,
                'thesis_required': row.thesis_required
            },
            'career_outcomes': {
                'job_titles': row.career_outcomes or [],
                'employment_rate': row.employment_rate,
                'average_salary': row.average_salary_range or {},
                'top_employers': row.top_employers or []
            },
            'costs': {
                'tuition_domestic': row.tuition_domestic,
                'tuition_international': row.tuition_international,
                'additional_fees': row.fees_additional or {},
                'currency': 'CAD',
                'financial_aid_available': row.financial_aid_available,
                'scholarships': row.scholarships_available or []
            },
            'metadata': {
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                'source': row.source_system,
                'source_url': row.source_url
            }
        }
        
        return program_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching program details: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch program details")


@router.post("/users/interactions")
async def record_interaction(
    interaction: UserProgramInteraction,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Record a user interaction with a program"""
    
    # Mock response for now
    return {"status": "success", "message": "Interaction recorded"}


@router.post("/users/saved-programs")
async def save_program(
    request: SaveProgramRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Save a program to user's saved list"""
    
    # Mock response for now
    return {"status": "success", "message": "Program saved"}


@router.get("/users/saved-programs")
async def get_saved_programs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get user's saved programs"""
    
    # Mock response for now
    return []


@router.delete("/users/saved-programs/{program_id}")
async def remove_saved_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Remove a program from user's saved list"""
    
    # Mock response for now
    return {"status": "success", "message": "Program removed from saved list"}


@router.get("/filters")
async def get_available_filters(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get available filter options for the search interface"""
    
    try:
        # Get facets from database
        facets = await get_search_facets(db)
        
        # Format for frontend
        return {
            'program_types': [
                {'value': key, 'label': key.title(), 'count': count} 
                for key, count in facets['program_types'].items()
            ],
            'levels': [
                {'value': key, 'label': key.title(), 'count': count} 
                for key, count in facets['levels'].items()
            ],
            'provinces': [
                {'value': key, 'label': key, 'count': count} 
                for key, count in facets['provinces'].items()
            ],
            'languages': [
                {'value': 'en', 'label': 'English', 'count': 0},
                {'value': 'fr', 'label': 'French', 'count': 0}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        # Return fallback
        return {
            'program_types': [],
            'levels': [],
            'provinces': [],
            'languages': [
                {'value': 'en', 'label': 'English', 'count': 0},
                {'value': 'fr', 'label': 'French', 'count': 0}
            ]
        }


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        
        # Get basic statistics
        institution_count = db.execute(text("SELECT COUNT(*) FROM institutions WHERE active = true")).scalar()
        program_count = db.execute(text("SELECT COUNT(*) FROM programs WHERE active = true")).scalar()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'statistics': {
                'institutions': institution_count,
                'programs': program_count
            },
            'message': 'School programs service is running with real data'
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }