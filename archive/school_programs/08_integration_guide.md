# School Programs Integration Guide

## Overview

This guide provides step-by-step instructions for integrating the school programs functionality into the Orientor platform. The integration includes CEGEP and university program data from multiple sources, with a complete search interface and user interaction system.

## Project Structure

```
./school_programs/
├── 01_research_findings.md          # Comprehensive research on data sources
├── 02_technical_architecture.md     # System architecture and design
├── 03_api_specifications.md         # REST API endpoint documentation
├── 04_data_ingestion_pipeline.py    # Data ingestion from external sources
├── 05_database_schema.sql           # Complete database schema
├── 06_fastapi_service.py            # FastAPI service implementation
├── 07_react_components.tsx          # React frontend components
└── 08_integration_guide.md          # This integration guide
```

## Phase 1: Database Setup

### 1.1 Create Database Schema

Run the database schema to set up all required tables:

```bash
# Connect to your PostgreSQL database
psql -U orientor_user -d orientor -f ./school_programs/05_database_schema.sql
```

**Key tables created:**
- `institutions` - Educational institutions (CEGEPs, universities)
- `programs` - Academic programs with full details
- `program_classifications` - Program classification hierarchies
- `user_program_preferences` - User search preferences
- `user_program_interactions` - User behavior tracking
- `user_saved_programs` - User's saved program list
- `user_program_recommendations` - AI-generated recommendations

### 1.2 Verify Schema Installation

```sql
-- Check if all tables are created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%program%' OR table_name = 'institutions';

-- Verify the search function exists
SELECT proname FROM pg_proc WHERE proname = 'search_programs';

-- Check materialized view
SELECT * FROM program_statistics;
```

## Phase 2: Backend Integration

### 2.1 Install Dependencies

Add required Python packages to your `requirements.txt`:

```txt
# Existing Orientor dependencies...

# School Programs Integration
aiohttp>=3.8.0
beautifulsoup4>=4.11.0
redis>=4.5.0
asyncpg>=0.28.0
pydantic>=1.10.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2.2 Environment Configuration

Add to your `.env` file:

```env
# School Programs Configuration
COLLEGE_SCORECARD_API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379
SCHOOL_PROGRAMS_CACHE_TTL=3600

# Data Source Rate Limits
SRAM_RATE_LIMIT=30
DONNEES_QC_RATE_LIMIT=60
COLLEGE_SCORECARD_RATE_LIMIT=1000
```

### 2.3 FastAPI Router Integration

Add the school programs router to your main FastAPI application:

```python
# app/main.py
from fastapi import FastAPI
from school_programs.fastapi_service import router as school_programs_router

app = FastAPI(title="Orientor API")

# Add school programs router
app.include_router(school_programs_router)

# Existing routers...
```

### 2.4 Database Connection Setup

Ensure your database connection supports the new schema:

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Update connection string if needed
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/orientor"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Phase 3: Data Ingestion Setup

### 3.1 Configure Data Sources

Create a configuration file for data sources:

```python
# config/school_programs.py
SCHOOL_PROGRAMS_CONFIG = {
    'database_url': DATABASE_URL,
    'redis_url': REDIS_URL,
    'sources': {
        'sram': {
            'enabled': True,
            'rate_limit': 30,  # requests per minute
            'base_url': 'https://www.sram.qc.ca'
        },
        'donnees_quebec': {
            'enabled': True,
            'rate_limit': 60,
            'base_url': 'https://www.donneesquebec.ca/recherche/api/3/action'
        },
        'college_scorecard': {
            'enabled': bool(COLLEGE_SCORECARD_API_KEY),
            'api_key': COLLEGE_SCORECARD_API_KEY,
            'rate_limit': 1000,  # requests per hour
            'base_url': 'https://api.data.gov/ed/collegescorecard/v1'
        }
    }
}
```

### 3.2 Set Up Data Ingestion Pipeline

Create a background task for regular data synchronization:

```python
# app/tasks/school_programs_sync.py
import asyncio
from celery import Celery
from school_programs.data_ingestion_pipeline import SchoolProgramsIngestionPipeline
from config.school_programs import SCHOOL_PROGRAMS_CONFIG

celery_app = Celery('orientor')

@celery_app.task
async def sync_school_programs():
    """Background task to sync school program data"""
    pipeline = SchoolProgramsIngestionPipeline(SCHOOL_PROGRAMS_CONFIG)
    
    # Add data sources
    if SCHOOL_PROGRAMS_CONFIG['sources']['sram']['enabled']:
        from school_programs.data_ingestion_pipeline import SRAMCEGEPSource
        pipeline.add_data_source(SRAMCEGEPSource, SCHOOL_PROGRAMS_CONFIG['sources']['sram'])
    
    if SCHOOL_PROGRAMS_CONFIG['sources']['college_scorecard']['enabled']:
        from school_programs.data_ingestion_pipeline import CollegeScorecardSource
        pipeline.add_data_source(CollegeScorecardSource, SCHOOL_PROGRAMS_CONFIG['sources']['college_scorecard'])
    
    # Run ingestion
    results = await pipeline.run_ingestion()
    
    return {
        'status': 'completed',
        'results': [r.__dict__ for r in results]
    }

# Schedule daily sync
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'sync-school-programs': {
        'task': 'app.tasks.school_programs_sync.sync_school_programs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### 3.3 Manual Data Sync

For initial data population, run the ingestion pipeline manually:

```python
# scripts/populate_school_programs.py
import asyncio
from school_programs.data_ingestion_pipeline import SchoolProgramsIngestionPipeline, SRAMCEGEPSource

async def main():
    config = {
        'database_url': 'postgresql://user:pass@localhost:5432/orientor',
        'redis_url': 'redis://localhost:6379'
    }
    
    pipeline = SchoolProgramsIngestionPipeline(config)
    pipeline.add_data_source(SRAMCEGEPSource, {'rate_limit': 30})
    
    results = await pipeline.run_ingestion()
    
    for result in results:
        print(f"Source: {result.source}")
        print(f"Success: {result.success}")
        print(f"Programs processed: {result.programs_processed}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 4: Frontend Integration

### 4.1 Install Frontend Dependencies

Add to your `package.json`:

```json
{
  "dependencies": {
    "lucide-react": "^0.263.1",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-select": "^1.2.2",
    "@radix-ui/react-tabs": "^1.0.4"
  }
}
```

Install dependencies:
```bash
npm install
```

### 4.2 Add to Navigation

Update your main navigation to include school programs:

```tsx
// components/Navigation.tsx
import { GraduationCap } from 'lucide-react';

const navigationItems = [
  // Existing items...
  {
    name: 'Programs',
    href: '/programs',
    icon: GraduationCap,
    description: 'Find CEGEP and university programs'
  }
];
```

### 4.3 Create Route

Add the school programs route to your app:

```tsx
// app/programs/page.tsx
import SchoolProgramsSearch from '@/school_programs/react_components';

export default function ProgramsPage() {
  return (
    <div className="min-h-screen bg-background">
      <SchoolProgramsSearch />
    </div>
  );
}
```

### 4.4 Add to User Dashboard

Integrate with the user dashboard:

```tsx
// components/Dashboard.tsx
import { BookmarkIcon, SearchIcon } from 'lucide-react';

const DashboardCard = ({ title, description, href, icon: Icon }) => (
  <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push(href)}>
    <div className="flex items-center space-x-4">
      <Icon className="h-8 w-8 text-primary" />
      <div>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-muted-foreground">{description}</p>
      </div>
    </div>
  </Card>
);

// Add to dashboard
<DashboardCard
  title="Explore Programs"
  description="Find CEGEP and university programs that match your interests"
  href="/programs"
  icon={SearchIcon}
/>

<DashboardCard
  title="Saved Programs"
  description="View your saved programs and application deadlines"
  href="/programs/saved"
  icon={BookmarkIcon}
/>
```

## Phase 5: User Profile Integration

### 5.1 Connect with Holland Profiles

Integrate school program recommendations with existing Holland RIASEC profiles:

```python
# services/program_recommendations.py
from typing import List
from app.models.user import User
from app.services.holland_service import get_user_holland_profile

class ProgramRecommendationService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_personality_based_recommendations(self, user: User) -> List[dict]:
        """Get program recommendations based on user's Holland profile"""
        
        # Get user's Holland profile
        holland_profile = await get_user_holland_profile(user.id)
        
        if not holland_profile:
            return []
        
        # Map Holland codes to program types and fields
        holland_to_programs = {
            'R': ['engineering', 'technology', 'applied_sciences'],  # Realistic
            'I': ['sciences', 'research', 'medical'],                # Investigative
            'A': ['arts', 'design', 'media', 'communications'],      # Artistic
            'S': ['education', 'social_work', 'healthcare'],         # Social
            'E': ['business', 'management', 'entrepreneurship'],     # Enterprising
            'C': ['administration', 'finance', 'accounting']         # Conventional
        }
        
        # Get top 3 Holland codes
        top_codes = holland_profile['top_3_code']
        recommended_fields = []
        
        for code in top_codes:
            recommended_fields.extend(holland_to_programs.get(code, []))
        
        # Search for programs in recommended fields
        search_query = """
        SELECT p.*, i.name as institution_name
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.field_of_study IN (%s)
        AND p.active = true
        ORDER BY p.employment_rate DESC NULLS LAST
        LIMIT 20
        """ % ','.join([f"'{field}'" for field in recommended_fields])
        
        results = await self.db.fetch_all(search_query)
        
        return [dict(row) for row in results]
```

### 5.2 User Preferences Sync

Sync user preferences from other parts of the platform:

```python
# services/user_preferences_sync.py
async def sync_user_preferences_to_programs(user_id: int):
    """Sync user preferences from profile to program preferences"""
    
    # Get user profile
    profile_query = "SELECT * FROM user_profiles WHERE user_id = $1"
    profile = await db.fetchrow(profile_query, user_id)
    
    if not profile:
        return
    
    # Create or update program preferences
    preferences = {
        'preferred_languages': ['en', 'fr'] if profile['country'] == 'CA' else ['en'],
        'preferred_provinces': [profile['state_province']] if profile['state_province'] else [],
        'fields_of_interest': profile['interests'].split(',') if profile['interests'] else [],
        'target_career_fields': profile['career_goals'].split(',') if profile['career_goals'] else []
    }
    
    upsert_query = """
    INSERT INTO user_program_preferences (user_id, preferred_languages, preferred_provinces, fields_of_interest, target_career_fields)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (user_id) DO UPDATE SET
        preferred_languages = EXCLUDED.preferred_languages,
        preferred_provinces = EXCLUDED.preferred_provinces,
        fields_of_interest = EXCLUDED.fields_of_interest,
        target_career_fields = EXCLUDED.target_career_fields,
        updated_at = NOW()
    """
    
    await db.execute(upsert_query, user_id, **preferences)
```

## Phase 6: Analytics and Monitoring

### 6.1 Set Up Analytics Dashboard

Create an admin dashboard for monitoring the school programs integration:

```python
# app/routers/admin/school_programs.py
from fastapi import APIRouter, Depends
from app.core.auth import get_admin_user

router = APIRouter(prefix="/admin/school-programs", tags=["Admin - School Programs"])

@router.get("/analytics")
async def get_analytics(admin_user = Depends(get_admin_user)):
    """Get school programs analytics dashboard data"""
    
    analytics_query = """
    SELECT 
        COUNT(*) as total_programs,
        COUNT(DISTINCT institution_id) as total_institutions,
        COUNT(*) FILTER (WHERE program_type = 'cegep') as cegep_programs,
        COUNT(*) FILTER (WHERE program_type = 'university') as university_programs,
        AVG(employment_rate) FILTER (WHERE employment_rate IS NOT NULL) as avg_employment_rate,
        
        -- User engagement
        (SELECT COUNT(*) FROM user_program_interactions WHERE created_at > NOW() - INTERVAL '30 days') as interactions_30d,
        (SELECT COUNT(DISTINCT user_id) FROM user_program_interactions WHERE created_at > NOW() - INTERVAL '30 days') as active_users_30d,
        (SELECT COUNT(*) FROM user_saved_programs) as total_saved_programs,
        
        -- Data freshness
        MAX(last_synced) as last_data_sync,
        COUNT(*) FILTER (WHERE last_synced < NOW() - INTERVAL '7 days') as stale_programs
        
    FROM programs 
    WHERE active = true
    """
    
    result = await db.fetchrow(analytics_query)
    return dict(result)

@router.get("/data-sources")
async def get_data_source_status():
    """Get status of all data sources"""
    
    status_query = """
    SELECT 
        source_name,
        MAX(started_at) as last_sync,
        status,
        records_processed,
        errors_encountered
    FROM data_source_sync_log
    WHERE started_at > NOW() - INTERVAL '7 days'
    GROUP BY source_name, status, records_processed, errors_encountered
    ORDER BY last_sync DESC
    """
    
    results = await db.fetch_all(status_query)
    return [dict(row) for row in results]
```

### 6.2 Health Monitoring

Set up health checks and alerts:

```python
# monitoring/school_programs_health.py
import asyncio
from datetime import datetime, timedelta

async def check_data_freshness():
    """Check if program data is fresh"""
    
    stale_threshold = datetime.utcnow() - timedelta(days=7)
    
    stale_query = """
    SELECT COUNT(*) as stale_count
    FROM programs 
    WHERE active = true 
    AND (last_synced < $1 OR last_synced IS NULL)
    """
    
    result = await db.fetchrow(stale_query, stale_threshold)
    stale_count = result['stale_count']
    
    if stale_count > 100:  # Alert threshold
        await send_alert(f"Warning: {stale_count} programs have stale data")
    
    return stale_count

async def check_search_performance():
    """Check search performance"""
    
    # Test search performance
    start_time = datetime.utcnow()
    
    test_query = """
    SELECT * FROM search_programs('computer science', ARRAY[]::TEXT[], ARRAY[]::TEXT[], 
                                  ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], 
                                  NULL, NULL, 10, 0)
    """
    
    await db.fetch_all(test_query)
    
    search_time = (datetime.utcnow() - start_time).total_seconds()
    
    if search_time > 2.0:  # Alert if search takes > 2 seconds
        await send_alert(f"Warning: Search performance degraded - {search_time:.2f}s")
    
    return search_time
```

## Phase 7: Testing

### 7.1 Unit Tests

Create comprehensive unit tests:

```python
# tests/test_school_programs.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_programs():
    """Test program search functionality"""
    
    response = client.post(
        "/api/v1/school-programs/search",
        json={
            "text": "computer science",
            "program_types": ["university"],
            "pagination": {"page": 1, "limit": 10}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert "facets" in data

def test_get_program_details():
    """Test program details retrieval"""
    
    # First, get a program ID from search
    search_response = client.post(
        "/api/v1/school-programs/search",
        json={"text": "engineering", "pagination": {"limit": 1}},
        headers={"Authorization": "Bearer test_token"}
    )
    
    programs = search_response.json()["results"]
    if programs:
        program_id = programs[0]["id"]
        
        response = client.get(
            f"/api/v1/school-programs/programs/{program_id}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == program_id

def test_save_program():
    """Test saving a program"""
    
    response = client.post(
        "/api/v1/school-programs/users/saved-programs",
        json={
            "program_id": "test-program-id",
            "notes": "Interested in this program"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### 7.2 Integration Tests

Test the complete data flow:

```python
# tests/test_integration.py
import asyncio
import pytest
from school_programs.data_ingestion_pipeline import SchoolProgramsIngestionPipeline

@pytest.mark.asyncio
async def test_data_ingestion_pipeline():
    """Test the complete data ingestion pipeline"""
    
    config = {
        'database_url': 'postgresql://test_user:test_pass@localhost:5432/test_orientor',
        'redis_url': 'redis://localhost:6379/1'
    }
    
    pipeline = SchoolProgramsIngestionPipeline(config)
    
    # Mock data source for testing
    class MockDataSource:
        async def fetch_programs(self):
            return [
                ProgramData(
                    title="Test Program",
                    institution_name="Test University",
                    institution_type="university",
                    program_type="academic",
                    level="bachelor",
                    source_system="test",
                    source_id="test_001"
                )
            ]
        
        async def fetch_institutions(self):
            return []
        
        async def health_check(self):
            return True
    
    pipeline.data_sources = [MockDataSource()]
    
    results = await pipeline.run_ingestion()
    
    assert len(results) == 1
    assert results[0].success == True
    assert results[0].programs_processed > 0
```

## Phase 8: Deployment

### 8.1 Production Configuration

Set up production environment variables:

```env
# Production .env
DATABASE_URL=postgresql://orientor_user:secure_password@db.orientor.com:5432/orientor
REDIS_URL=redis://cache.orientor.com:6379
COLLEGE_SCORECARD_API_KEY=your_production_api_key

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO

# Performance
SCHOOL_PROGRAMS_CACHE_TTL=3600
MAX_SEARCH_RESULTS=100
SEARCH_TIMEOUT_SECONDS=10
```

### 8.2 Docker Configuration

Update your Docker setup:

```dockerfile
# Dockerfile additions
# Install additional dependencies for school programs
RUN pip install aiohttp beautifulsoup4 redis asyncpg

# Copy school programs modules
COPY school_programs/ /app/school_programs/
```

```yaml
# docker-compose.yml additions
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 8.3 Database Migration

Create an Alembic migration for the new schema:

```python
# alembic/versions/add_school_programs.py
"""Add school programs tables

Revision ID: school_programs_001
Revises: previous_revision
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'school_programs_001'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Execute the school programs schema
    with open('school_programs/05_database_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Split and execute individual statements
    statements = schema_sql.split(';')
    for statement in statements:
        if statement.strip():
            op.execute(statement)

def downgrade():
    # Drop all school programs tables
    tables_to_drop = [
        'user_program_recommendations',
        'program_comparisons',
        'user_saved_programs',
        'user_program_interactions',
        'user_program_preferences',
        'program_search_cache',
        'data_source_sync_log',
        'program_classifications',
        'programs',
        'institutions'
    ]
    
    for table in tables_to_drop:
        op.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
    
    # Drop views and functions
    op.execute('DROP VIEW IF EXISTS active_programs CASCADE')
    op.execute('DROP VIEW IF EXISTS searchable_programs CASCADE')
    op.execute('DROP VIEW IF EXISTS user_interaction_summary CASCADE')
    op.execute('DROP FUNCTION IF EXISTS search_programs CASCADE')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column CASCADE')
```

## Phase 9: Go-Live Checklist

### 9.1 Pre-Launch Verification

- [ ] Database schema installed successfully
- [ ] All API endpoints return expected responses
- [ ] Frontend components render correctly
- [ ] Data ingestion pipeline runs without errors
- [ ] Search performance meets requirements (< 1s average)
- [ ] User authentication and authorization work
- [ ] Analytics and monitoring dashboards functional
- [ ] Error handling and logging configured
- [ ] Cache invalidation working properly
- [ ] Background tasks scheduled correctly

### 9.2 Performance Verification

```bash
# Test API performance
curl -X POST "https://api.orientor.com/api/v1/school-programs/search" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"text": "computer science", "pagination": {"limit": 20}}' \
     -w "Time: %{time_total}s\n"

# Test database performance
psql -d orientor -c "EXPLAIN ANALYZE SELECT * FROM search_programs('engineering', ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], NULL, NULL, 20, 0);"
```

### 9.3 Data Quality Check

```sql
-- Verify data quality
SELECT 
    COUNT(*) as total_programs,
    COUNT(*) FILTER (WHERE title IS NOT NULL) as programs_with_titles,
    COUNT(*) FILTER (WHERE institution_id IS NOT NULL) as programs_with_institutions,
    COUNT(*) FILTER (WHERE last_synced > NOW() - INTERVAL '7 days') as recently_synced,
    COUNT(DISTINCT source_system) as data_sources
FROM programs WHERE active = true;

-- Check for duplicates
SELECT title, institution_id, COUNT(*) 
FROM programs 
WHERE active = true 
GROUP BY title, institution_id 
HAVING COUNT(*) > 1;
```

## Phase 10: Post-Launch Monitoring

### 10.1 Key Metrics to Monitor

1. **Search Performance**
   - Average search response time
   - Search success rate
   - Cache hit ratio

2. **User Engagement**
   - Daily active users
   - Program views per session
   - Save-to-view ratio
   - Search-to-interaction conversion

3. **Data Quality**
   - Data freshness (programs synced in last 7 days)
   - Error rates in data ingestion
   - Coverage (programs per institution)

4. **System Health**
   - API response times
   - Database query performance
   - Redis cache performance
   - Background job success rates

### 10.2 Alerting Rules

Set up alerts for:
- Search response time > 2 seconds
- Data sync failures
- More than 100 stale programs
- API error rate > 5%
- Cache hit ratio < 70%

### 10.3 Regular Maintenance Tasks

**Daily:**
- Monitor data sync jobs
- Check search performance metrics
- Review error logs

**Weekly:**
- Analyze user engagement metrics
- Review data quality reports
- Update program classification mappings

**Monthly:**
- Review and optimize database queries
- Update API rate limits based on usage
- Analyze recommendation effectiveness
- Plan new data source integrations

## Troubleshooting

### Common Issues

1. **Search Returns No Results**
   - Check if data ingestion completed successfully
   - Verify search_vector is properly generated
   - Test with simpler queries

2. **Slow Search Performance**
   - Check database indexes
   - Analyze query execution plans
   - Increase cache TTL
   - Consider database connection pooling

3. **Data Ingestion Failures**
   - Check external API availability
   - Verify rate limiting compliance
   - Review error logs for specific issues
   - Test with smaller data sets

4. **Frontend Loading Issues**
   - Check API connectivity
   - Verify authentication tokens
   - Review browser console for errors
   - Test with different browsers

### Support Contacts

- **Backend Issues**: backend-team@orientor.com
- **Frontend Issues**: frontend-team@orientor.com
- **Data Issues**: data-team@orientor.com
- **Infrastructure**: devops-team@orientor.com

---

This integration guide provides a comprehensive roadmap for implementing the school programs functionality in the Orientor platform. Follow each phase sequentially for the best results, and don't hesitate to reach out for support during implementation.