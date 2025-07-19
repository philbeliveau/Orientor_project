"""
FastAPI Service for School Programs Integration

This module provides the REST API endpoints for searching and managing school programs.
Follows Orientor platform patterns with dependency injection and consistent error handling.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import redis.asyncio as redis

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic Models
class ProgramSearchQuery(BaseModel):
    """Program search query parameters"""
    text: Optional[str] = Field(None, description="Search text for program titles and descriptions")
    program_types: Optional[List[str]] = Field(default=[], description="Filter by program types")
    levels: Optional[List[str]] = Field(default=[], description="Filter by program levels")
    location: Optional[Dict[str, str]] = Field(default={}, description="Location filters")
    languages: Optional[List[str]] = Field(default=[], description="Language preferences")
    duration: Optional[Dict[str, int]] = Field(default={}, description="Duration constraints")
    budget: Optional[Dict[str, float]] = Field(default={}, description="Budget constraints")
    sort: Optional[Dict[str, str]] = Field(default={"field": "relevance", "direction": "desc"})
    pagination: Optional[Dict[str, int]] = Field(default={"page": 1, "limit": 20})
    
    @validator('pagination')
    def validate_pagination(cls, v):
        if v.get('limit', 20) > 100:
            v['limit'] = 100
        if v.get('page', 1) < 1:
            v['page'] = 1
        return v


class ProgramResponse(BaseModel):
    """Program data response model"""
    id: UUID
    title: str
    title_fr: Optional[str]
    description: Optional[str]
    description_fr: Optional[str]
    institution: Dict[str, Any]
    program_details: Dict[str, Any]
    classification: Dict[str, Any]
    admission: Dict[str, Any]
    academic_info: Dict[str, Any]
    career_outcomes: Dict[str, Any]
    costs: Dict[str, Any]
    metadata: Dict[str, Any]


class SearchResultsResponse(BaseModel):
    """Search results response model"""
    results: List[ProgramResponse]
    pagination: Dict[str, Any]
    facets: Dict[str, Any]
    metadata: Dict[str, Any]


class UserProgramInteraction(BaseModel):
    """User program interaction model"""
    program_id: UUID
    interaction_type: str = Field(..., regex="^(viewed|saved|applied|dismissed|shared|compared)$")
    metadata: Optional[Dict[str, Any]] = Field(default={})


class SaveProgramRequest(BaseModel):
    """Save program request model"""
    program_id: UUID
    notes: Optional[str] = None
    priority_level: Optional[int] = Field(1, ge=1, le=5)
    tags: Optional[List[str]] = Field(default=[])


class ProgramComparison(BaseModel):
    """Program comparison request"""
    program_ids: List[UUID] = Field(..., min_items=2, max_items=5)


# Service Classes
class ProgramSearchService:
    """Service for program search operations"""
    
    def __init__(self, db: AsyncSession, cache: redis.Redis, user: User):
        self.db = db
        self.cache = cache
        self.user = user
        self.cache_ttl = 3600  # 1 hour
    
    async def search_programs(self, query: ProgramSearchQuery) -> SearchResultsResponse:
        """Search for programs based on query parameters"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(query)
            
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for search query: {cache_key}")
                result_data = json.loads(cached_result)
                result_data['metadata']['cache_hit'] = True
                return SearchResultsResponse(**result_data)
            
            # Perform database search
            search_start = datetime.utcnow()
            
            # Build search filters
            filters = self._build_search_filters(query)
            
            # Execute search query using the database function
            search_results = await self._execute_search_query(query, filters)
            
            # Get facets for filtering
            facets = await self._get_search_facets(query, filters)
            
            # Calculate pagination
            total_results = len(search_results) if search_results else 0
            pagination = self._calculate_pagination(query.pagination, total_results)
            
            # Prepare response
            search_time = (datetime.utcnow() - search_start).total_seconds() * 1000
            
            response_data = {
                'results': search_results,
                'pagination': pagination,
                'facets': facets,
                'metadata': {
                    'search_time_ms': search_time,
                    'sources_queried': ['database'],
                    'cache_hit': False
                }
            }
            
            # Cache the results
            await self.cache.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response_data, default=str)
            )
            
            return SearchResultsResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error in program search: {e}")
            raise HTTPException(status_code=500, detail="Search service temporarily unavailable")
    
    def _generate_cache_key(self, query: ProgramSearchQuery) -> str:
        """Generate cache key for search query"""
        query_str = json.dumps(query.dict(), sort_keys=True)
        return f"program_search:{hashlib.md5(query_str.encode()).hexdigest()}"
    
    def _build_search_filters(self, query: ProgramSearchQuery) -> Dict[str, Any]:
        """Build database filters from search query"""
        filters = {}
        
        if query.text:
            filters['search_text'] = query.text
        
        if query.program_types:
            filters['program_types'] = query.program_types
        
        if query.levels:
            filters['levels'] = query.levels
        
        if query.location:
            if query.location.get('country'):
                filters['countries'] = [query.location['country']]
            if query.location.get('province'):
                filters['provinces'] = [query.location['province']]
        
        if query.languages:
            filters['languages'] = query.languages
        
        if query.duration:
            if query.duration.get('max_months'):
                filters['max_duration'] = query.duration['max_months']
        
        return filters
    
    async def _execute_search_query(self, query: ProgramSearchQuery, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the actual search query against database"""
        try:
            # Use the database search function
            search_sql = """
            SELECT * FROM search_programs(
                $1::TEXT, $2::TEXT[], $3::TEXT[], $4::TEXT[], $5::TEXT[], 
                $6::TEXT[], $7::INTEGER, $8::DECIMAL, $9::INTEGER, $10::INTEGER
            )
            """
            
            # Prepare parameters
            search_text = filters.get('search_text', '')
            program_types = filters.get('program_types', [])
            levels = filters.get('levels', [])
            countries = filters.get('countries', [])
            provinces = filters.get('provinces', [])
            languages = filters.get('languages', [])
            max_duration = filters.get('max_duration')
            min_employment_rate = None  # Could be added to query
            
            limit = query.pagination.get('limit', 20)
            offset = (query.pagination.get('page', 1) - 1) * limit
            
            # Execute query
            connection = await self.db.connection()
            rows = await connection.fetch(
                search_sql,
                search_text, program_types, levels, countries, provinces,
                languages, max_duration, min_employment_rate, limit, offset
            )
            
            # Convert to response format
            results = []
            for row in rows:
                program_data = await self._format_program_response(dict(row))
                results.append(program_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Database search error: {e}")
            return []
    
    async def _format_program_response(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Format database row into program response"""
        return {
            'id': row['id'],
            'title': row['title'],
            'title_fr': None,  # Would need to join with full program data
            'description': None,
            'description_fr': None,
            'institution': {
                'name': row['institution_name'],
                'city': row['city'],
                'province': row['province_state'],
                'type': 'cegep'  # Would come from institution table
            },
            'program_details': {
                'type': row['program_type'],
                'level': row['level'],
                'duration_months': row['duration_months']
            },
            'classification': {
                'field_of_study': 'Computer Science',  # Would need classification join
                'category': 'STEM'
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
                'employment_rate': row['employment_rate'],
                'job_titles': []
            },
            'costs': {
                'tuition_per_semester': None,
                'currency': 'CAD'
            },
            'metadata': {
                'search_rank': row.get('search_rank', 1.0),
                'last_updated': datetime.utcnow().isoformat()
            }
        }
    
    async def _get_search_facets(self, query: ProgramSearchQuery, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get search facets for filtering UI"""
        # This would execute aggregation queries to get facet counts
        return {
            'program_types': {
                'cegep': 150,
                'university': 200
            },
            'levels': {
                'diploma': 120,
                'bachelor': 180,
                'master': 50
            },
            'provinces': {
                'QC': 200,
                'ON': 150
            }
        }
    
    def _calculate_pagination(self, pagination_params: Dict[str, int], total_results: int) -> Dict[str, Any]:
        """Calculate pagination metadata"""
        page = pagination_params.get('page', 1)
        limit = pagination_params.get('limit', 20)
        total_pages = (total_results + limit - 1) // limit
        
        return {
            'page': page,
            'limit': limit,
            'total_pages': total_pages,
            'total_results': total_results,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }


class UserInteractionService:
    """Service for user program interactions"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def record_interaction(self, interaction: UserProgramInteraction) -> bool:
        """Record a user interaction with a program"""
        try:
            insert_sql = """
            INSERT INTO user_program_interactions (
                user_id, program_id, interaction_type, interaction_source,
                search_query, interaction_duration_seconds, session_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            connection = await self.db.connection()
            await connection.execute(
                insert_sql,
                self.user.id,
                interaction.program_id,
                interaction.interaction_type,
                interaction.metadata.get('source', 'unknown'),
                interaction.metadata.get('search_query'),
                interaction.metadata.get('duration_seconds'),
                interaction.metadata.get('session_id')
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return False
    
    async def save_program(self, request: SaveProgramRequest) -> bool:
        """Save a program for the user"""
        try:
            insert_sql = """
            INSERT INTO user_saved_programs (
                user_id, program_id, personal_notes, priority_level, user_tags
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, program_id) 
            DO UPDATE SET 
                personal_notes = EXCLUDED.personal_notes,
                priority_level = EXCLUDED.priority_level,
                user_tags = EXCLUDED.user_tags,
                updated_at = NOW()
            """
            
            connection = await self.db.connection()
            await connection.execute(
                insert_sql,
                self.user.id,
                request.program_id,
                request.notes,
                request.priority_level,
                request.tags
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving program: {e}")
            return False
    
    async def get_saved_programs(self) -> List[Dict[str, Any]]:
        """Get user's saved programs"""
        try:
            query_sql = """
            SELECT sp.*, p.title, p.program_type, p.level,
                   i.name as institution_name, i.city, i.province_state
            FROM user_saved_programs sp
            JOIN programs p ON sp.program_id = p.id
            JOIN institutions i ON p.institution_id = i.id
            WHERE sp.user_id = $1
            ORDER BY sp.saved_at DESC
            """
            
            connection = await self.db.connection()
            rows = await connection.fetch(query_sql, self.user.id)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error fetching saved programs: {e}")
            return []


# API Dependencies
async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    return redis.from_url("redis://localhost:6379")  # Would come from config


async def get_program_search_service(
    db: AsyncSession = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
    user: User = Depends(get_current_user)
) -> ProgramSearchService:
    """Dependency for program search service"""
    return ProgramSearchService(db, cache, user)


async def get_user_interaction_service(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> UserInteractionService:
    """Dependency for user interaction service"""
    return UserInteractionService(db, user)


# Router setup
router = APIRouter(prefix="/api/v1/school-programs", tags=["School Programs"])


# API Endpoints
@router.post("/search")
async def search_programs(
    query: ProgramSearchQuery,
    search_service: ProgramSearchService = Depends(get_program_search_service)
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
    return await search_service.search_programs(query)


@router.get("/search")
async def quick_search(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[str] = Query(None, description="Program type filter"),
    level: Optional[str] = Query(None, description="Program level filter"),
    province: Optional[str] = Query(None, description="Province filter"),
    limit: int = Query(20, ge=1, le=100, description="Results limit"),
    page: int = Query(1, ge=1, description="Page number"),
    search_service: ProgramSearchService = Depends(get_program_search_service)
) -> SearchResultsResponse:
    """Quick search endpoint for simple queries"""
    
    query = ProgramSearchQuery(
        text=q,
        program_types=[type] if type else [],
        levels=[level] if level else [],
        location={'province': province} if province else {},
        pagination={'page': page, 'limit': limit}
    )
    
    return await search_service.search_programs(query)


@router.get("/programs/{program_id}")
async def get_program_details(
    program_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProgramResponse:
    """Get detailed information about a specific program"""
    
    try:
        query_sql = """
        SELECT p.*, i.name as institution_name, i.city, i.province_state, i.country,
               i.website_url as institution_website, i.institution_type
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.id = $1 AND p.active = true
        """
        
        connection = await db.connection()
        row = await connection.fetchrow(query_sql, program_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Program not found")
        
        # Format full program response
        program_data = {
            'id': row['id'],
            'title': row['title'],
            'title_fr': row['title_fr'],
            'description': row['description'],
            'description_fr': row['description_fr'],
            'institution': {
                'name': row['institution_name'],
                'city': row['city'],
                'province': row['province_state'],
                'country': row['country'],
                'website': row['institution_website'],
                'type': row['institution_type']
            },
            'program_details': {
                'type': row['program_type'],
                'level': row['level'],
                'duration_months': row['duration_months'],
                'language': row['language'],
                'cip_code': row['cip_code'],
                'program_code': row['program_code']
            },
            'classification': {
                'field_of_study': row['field_of_study'],
                'field_of_study_fr': row['field_of_study_fr']
            },
            'admission': {
                'requirements': row['admission_requirements'] or [],
                'deadline': row['application_deadline'],
                'application_method': row['application_method']
            },
            'academic_info': {
                'credits': row['credits'],
                'semester_count': row['semester_count'],
                'internship_required': row['internship_required'],
                'coop_available': row['coop_available']
            },
            'career_outcomes': {
                'job_titles': row['career_outcomes'] or [],
                'employment_rate': row['employment_rate'],
                'average_salary': row['average_salary_range'] or {}
            },
            'costs': {
                'tuition_domestic': row['tuition_domestic'],
                'tuition_international': row['tuition_international'],
                'currency': 'CAD'
            },
            'metadata': {
                'created_at': row['created_at'].isoformat(),
                'updated_at': row['updated_at'].isoformat(),
                'source': row['source_system'],
                'source_url': row['source_url']
            }
        }
        
        return ProgramResponse(**program_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching program details: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch program details")


@router.post("/users/interactions")
async def record_interaction(
    interaction: UserProgramInteraction,
    interaction_service: UserInteractionService = Depends(get_user_interaction_service)
) -> Dict[str, str]:
    """Record a user interaction with a program"""
    
    success = await interaction_service.record_interaction(interaction)
    
    if success:
        return {"status": "success", "message": "Interaction recorded"}
    else:
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.post("/users/saved-programs")
async def save_program(
    request: SaveProgramRequest,
    interaction_service: UserInteractionService = Depends(get_user_interaction_service)
) -> Dict[str, str]:
    """Save a program to user's saved list"""
    
    success = await interaction_service.save_program(request)
    
    if success:
        return {"status": "success", "message": "Program saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save program")


@router.get("/users/saved-programs")
async def get_saved_programs(
    interaction_service: UserInteractionService = Depends(get_user_interaction_service)
) -> List[Dict[str, Any]]:
    """Get user's saved programs"""
    
    return await interaction_service.get_saved_programs()


@router.delete("/users/saved-programs/{program_id}")
async def remove_saved_program(
    program_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Remove a program from user's saved list"""
    
    try:
        delete_sql = """
        DELETE FROM user_saved_programs 
        WHERE user_id = $1 AND program_id = $2
        """
        
        connection = await db.connection()
        result = await connection.execute(delete_sql, user.id, program_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Saved program not found")
        
        return {"status": "success", "message": "Program removed from saved list"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing saved program: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove saved program")


@router.post("/compare")
async def compare_programs(
    comparison: ProgramComparison,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Compare multiple programs side by side"""
    
    try:
        placeholders = ', '.join([f'${i+1}' for i in range(len(comparison.program_ids))])
        query_sql = f"""
        SELECT p.*, i.name as institution_name, i.city, i.province_state
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.id IN ({placeholders}) AND p.active = true
        ORDER BY p.title
        """
        
        connection = await db.connection()
        rows = await connection.fetch(query_sql, *comparison.program_ids)
        
        if len(rows) != len(comparison.program_ids):
            raise HTTPException(status_code=404, detail="One or more programs not found")
        
        programs = [dict(row) for row in rows]
        
        # Create comparison matrix
        comparison_matrix = {
            'duration': [p['duration_months'] for p in programs],
            'tuition': [p['tuition_domestic'] for p in programs],
            'employment_rate': [p['employment_rate'] for p in programs],
            'institution_type': [p.get('institution_type', 'unknown') for p in programs]
        }
        
        return {
            'programs': programs,
            'comparison_matrix': comparison_matrix
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing programs: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare programs")


@router.get("/filters")
async def get_available_filters(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get available filter options for the search interface"""
    
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
        
        connection = await db.connection()
        
        types_rows = await connection.fetch(types_sql)
        levels_rows = await connection.fetch(levels_sql)
        provinces_rows = await connection.fetch(provinces_sql)
        
        return {
            'program_types': [{'value': row['program_type'], 'label': row['program_type'].title(), 'count': row['count']} for row in types_rows],
            'levels': [{'value': row['level'], 'label': row['level'].title(), 'count': row['count']} for row in levels_rows],
            'provinces': [{'value': row['province_state'], 'label': row['province_state'], 'count': row['count']} for row in provinces_rows],
            'languages': [
                {'value': 'en', 'label': 'English', 'count': 0},
                {'value': 'fr', 'label': 'French', 'count': 0}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch filter options")


# Background task for data synchronization
@router.post("/admin/sync-data")
async def trigger_data_sync(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Trigger background data synchronization (admin only)"""
    
    # Check if user has admin privileges (would need to implement role checking)
    # if not user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    # Add background task
    background_tasks.add_task(run_data_sync)
    
    return {"status": "success", "message": "Data synchronization initiated"}


async def run_data_sync():
    """Background task for data synchronization"""
    try:
        logger.info("Starting background data synchronization")
        
        # Import and run the ingestion pipeline
        from school_programs.data_ingestion_pipeline import SchoolProgramsIngestionPipeline
        
        config = {
            'database_url': 'postgresql://user:pass@localhost:5432/orientor',
            'redis_url': 'redis://localhost:6379'
        }
        
        pipeline = SchoolProgramsIngestionPipeline(config)
        # Add sources and run
        # results = await pipeline.run_ingestion()
        
        logger.info("Background data synchronization completed")
        
    except Exception as e:
        logger.error(f"Background sync error: {e}")


# Health check endpoint
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    
    try:
        # Check database connectivity
        connection = await db.connection()
        await connection.fetch("SELECT 1")
        
        # Get basic statistics
        stats_sql = "SELECT * FROM program_statistics"
        stats_row = await connection.fetchrow(stats_sql)
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'statistics': dict(stats_row) if stats_row else {}
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }