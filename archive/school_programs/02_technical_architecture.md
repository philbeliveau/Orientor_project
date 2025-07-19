# School Programs Integration - Technical Architecture

## System Overview

This document outlines the technical architecture for integrating CEGEP and university program banks into the Orientor platform. The system follows a microservices architecture with clear separation of concerns and modular design principles.

## Architecture Principles

### 1. Modular Design
- Each data source has its own service module (< 500 lines per file)
- Clear interfaces between components
- Pluggable data providers
- Independent scaling of services

### 2. Data Source Independence  
- Never depend on a single data provider
- Graceful degradation when sources are unavailable
- Consistent internal data model regardless of source
- Easy addition of new data sources

### 3. Performance & Scalability
- Local caching to reduce API calls
- Asynchronous data processing
- Rate limiting compliance
- Horizontal scaling capabilities

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
│                     (FastAPI Router)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│                 Program Search Service                         │
│           (Business Logic & Orchestration)                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│                 Data Integration Layer                         │
├─────────────────────┼───────────────────────────────────────────┤
│   CEGEP Service     │    University Service    │  Classification │
│                     │                          │    Service      │
├─────────────────────┼──────────────────────────┼─────────────────┤
│ • SRAM Scraper      │ • College Scorecard API  │ • CIP Codes     │
│ • Données QC API    │ • Waterloo API           │ • ISCED Mapping │
│ • ISQ Integration   │ • HESA Data              │ • Custom Taxonomy│
└─────────────────────┴──────────────────────────┴─────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│                    Data Storage Layer                          │
├─────────────────────┼───────────────────────────────────────────┤
│   PostgreSQL        │         Redis Cache       │   Vector DB   │
│ (Primary Storage)   │      (Performance)        │  (Semantic    │
│                     │                           │   Search)     │
└─────────────────────┴───────────────────────────┴───────────────┘
```

## Service Layer Design

### 1. Program Search Service (`services/program_search.py`)

**Responsibilities:**
- Orchestrate searches across multiple data sources
- Merge and rank results
- Handle user preferences and filters
- Generate recommendations

**Key Methods:**
```python
class ProgramSearchService:
    async def search_programs(self, query: SearchQuery) -> SearchResults
    async def get_program_details(self, program_id: str) -> ProgramDetails
    async def get_recommendations(self, user_profile: UserProfile) -> List[Program]
    async def filter_by_location(self, programs: List[Program], location: Location) -> List[Program]
```

### 2. CEGEP Integration Service (`services/cegep_service.py`)

**Responsibilities:**
- Interface with Quebec CEGEP data sources
- Normalize CEGEP program data
- Handle French/English translations
- Manage scraping schedules

**Data Sources:**
- SRAM program directory (web scraping)
- Données Québec CKAN API
- ISQ research database (when available)

**Key Methods:**
```python
class CEGEPService:
    async def fetch_programs(self) -> List[CEGEPProgram]
    async def get_program_by_code(self, code: str) -> CEGEPProgram
    async def search_by_field(self, field: str) -> List[CEGEPProgram]
    async def update_program_cache(self) -> None
```

### 3. University Integration Service (`services/university_service.py`)

**Responsibilities:**
- Interface with university APIs and databases
- Normalize university program data
- Handle multiple classification systems
- Manage API rate limits

**Data Sources:**
- US College Scorecard API
- University of Waterloo API  
- Statistics Canada CIP
- HESA UK data

**Key Methods:**
```python
class UniversityService:
    async def fetch_programs(self, country: str = None) -> List[UniversityProgram]
    async def get_program_by_cip(self, cip_code: str) -> UniversityProgram
    async def search_by_institution(self, institution: str) -> List[UniversityProgram]
    async def sync_external_apis(self) -> None
```

### 4. Classification Service (`services/classification_service.py`)

**Responsibilities:**
- Manage program classification systems
- Handle code translations (CIP, ISCED, custom)
- Provide semantic program matching
- Maintain taxonomy consistency

**Key Methods:**
```python
class ClassificationService:
    def get_cip_hierarchy(self, code: str) -> CIPHierarchy
    def map_isced_to_cip(self, isced_code: str) -> str
    def find_related_programs(self, program: Program) -> List[Program]
    def categorize_program(self, program: Program) -> List[Category]
```

## Database Schema

### Core Tables

#### programs
```sql
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    description TEXT,
    institution_id UUID REFERENCES institutions(id),
    program_type VARCHAR NOT NULL, -- 'cegep', 'university', 'college'
    level VARCHAR NOT NULL, -- 'certificate', 'diploma', 'bachelor', 'master', 'phd'
    duration_months INTEGER,
    language VARCHAR NOT NULL DEFAULT 'en',
    cip_code VARCHAR,
    isced_code VARCHAR,
    custom_category VARCHAR,
    admission_requirements JSONB,
    career_outcomes JSONB,
    prerequisites JSONB,
    tuition_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_system VARCHAR NOT NULL,
    source_id VARCHAR NOT NULL,
    source_url VARCHAR,
    last_synced TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true
);

CREATE INDEX idx_programs_cip ON programs(cip_code);
CREATE INDEX idx_programs_type ON programs(program_type);
CREATE INDEX idx_programs_institution ON programs(institution_id);
CREATE INDEX idx_programs_search ON programs USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));
```

#### institutions
```sql
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    name_fr VARCHAR,
    institution_type VARCHAR NOT NULL, -- 'cegep', 'university', 'college'
    country VARCHAR NOT NULL,
    province_state VARCHAR,
    city VARCHAR,
    postal_code VARCHAR,
    website_url VARCHAR,
    accreditation_status VARCHAR,
    student_count INTEGER,
    established_year INTEGER,
    languages_offered VARCHAR[] DEFAULT ARRAY['en'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_system VARCHAR NOT NULL,
    source_id VARCHAR NOT NULL,
    active BOOLEAN DEFAULT true
);

CREATE INDEX idx_institutions_type ON institutions(institution_type);
CREATE INDEX idx_institutions_location ON institutions(country, province_state, city);
```

#### program_classifications
```sql
CREATE TABLE program_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    classification_system VARCHAR NOT NULL, -- 'cip', 'isced', 'custom'
    code VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    level INTEGER, -- hierarchy level
    parent_code VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_classifications_program ON program_classifications(program_id);
CREATE INDEX idx_classifications_system_code ON program_classifications(classification_system, code);
```

#### program_search_cache
```sql
CREATE TABLE program_search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_hash VARCHAR NOT NULL UNIQUE,
    search_params JSONB NOT NULL,
    results JSONB NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_search_cache_hash ON program_search_cache(search_hash);
CREATE INDEX idx_search_cache_expires ON program_search_cache(expires_at);
```

### Orientor Integration Tables

#### user_program_preferences
```sql
CREATE TABLE user_program_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    preferred_locations VARCHAR[] DEFAULT ARRAY[],
    preferred_languages VARCHAR[] DEFAULT ARRAY['en'],
    program_types VARCHAR[] DEFAULT ARRAY[], -- 'cegep', 'university'
    program_levels VARCHAR[] DEFAULT ARRAY[], -- 'certificate', 'diploma', etc.
    max_duration_months INTEGER,
    budget_range JSONB, -- {min: 0, max: 50000, currency: 'CAD'}
    field_interests VARCHAR[] DEFAULT ARRAY[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_user ON user_program_preferences(user_id);
```

#### user_program_interactions
```sql
CREATE TABLE user_program_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    interaction_type VARCHAR NOT NULL, -- 'viewed', 'saved', 'applied', 'dismissed'
    interaction_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_interactions_user ON user_program_interactions(user_id);
CREATE INDEX idx_interactions_program ON user_program_interactions(program_id);
CREATE INDEX idx_interactions_type ON user_program_interactions(interaction_type);
```

## API Integration Architecture

### 1. Rate Limiting Strategy

```python
class RateLimitedClient:
    def __init__(self, base_url: str, max_requests_per_hour: int = 1000):
        self.base_url = base_url
        self.rate_limiter = AsyncRateLimiter(max_requests_per_hour)
        self.session = aiohttp.ClientSession()
    
    async def get(self, endpoint: str, **kwargs):
        async with self.rate_limiter:
            response = await self.session.get(f"{self.base_url}/{endpoint}", **kwargs)
            return await response.json()
```

### 2. Caching Strategy

```python
class CacheManager:
    def __init__(self):
        self.redis = redis.Redis()
        self.default_ttl = 3600  # 1 hour
    
    async def get_or_fetch(self, key: str, fetch_func: Callable, ttl: int = None):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        data = await fetch_func()
        await self.redis.setex(key, ttl or self.default_ttl, json.dumps(data))
        return data
```

### 3. Data Synchronization

```python
class DataSyncScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        # Daily sync for dynamic content
        self.scheduler.add_job(
            self.sync_all_sources,
            'cron',
            hour=2,  # 2 AM
            id='daily_sync'
        )
        
        # Weekly sync for static content
        self.scheduler.add_job(
            self.full_refresh,
            'cron',
            day_of_week=0,  # Sunday
            hour=1,  # 1 AM
            id='weekly_refresh'
        )
        
        self.scheduler.start()
```

## Error Handling & Resilience

### 1. Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = await func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            raise e
```

### 2. Fallback Mechanisms

```python
class DataSourceOrchestrator:
    def __init__(self):
        self.primary_sources = [CEGEPService(), UniversityService()]
        self.fallback_sources = [CachedDataService(), StaticDataService()]
    
    async def search_programs(self, query: SearchQuery) -> SearchResults:
        for source in self.primary_sources:
            try:
                results = await source.search(query)
                if results.count > 0:
                    return results
            except Exception as e:
                logger.warning(f"Primary source {source.__class__.__name__} failed: {e}")
        
        # Fallback to cached/static data
        for source in self.fallback_sources:
            try:
                results = await source.search(query)
                if results.count > 0:
                    return results
            except Exception as e:
                logger.error(f"Fallback source {source.__class__.__name__} failed: {e}")
        
        return SearchResults(programs=[], count=0, message="No results available")
```

## Performance Optimization

### 1. Database Indexing Strategy

```sql
-- Full-text search optimization
CREATE INDEX idx_programs_fts ON programs 
USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Geographic search optimization
CREATE INDEX idx_institutions_geography ON institutions 
USING btree(country, province_state, city);

-- Category-based filtering
CREATE INDEX idx_programs_category ON programs(program_type, level, cip_code);

-- User interaction analytics
CREATE INDEX idx_interactions_analytics ON user_program_interactions(user_id, created_at, interaction_type);
```

### 2. Query Optimization

```python
class OptimizedProgramSearch:
    async def search_with_filters(self, query: SearchQuery) -> SearchResults:
        # Use prepared statements for common queries
        base_query = """
        SELECT p.*, i.name as institution_name, i.city, i.province_state
        FROM programs p
        JOIN institutions i ON p.institution_id = i.id
        WHERE p.active = true
        """
        
        conditions = []
        params = {}
        
        # Add dynamic filters
        if query.program_type:
            conditions.append("p.program_type = ANY(%(program_types)s)")
            params['program_types'] = query.program_type
        
        if query.location:
            conditions.append("i.country = %(country)s")
            params['country'] = query.location.country
        
        if query.text:
            conditions.append("to_tsvector('english', p.title || ' ' || COALESCE(p.description, '')) @@ plainto_tsquery(%(search_text)s)")
            params['search_text'] = query.text
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY p.updated_at DESC LIMIT %(limit)s OFFSET %(offset)s"
        params['limit'] = query.limit or 20
        params['offset'] = query.offset or 0
        
        return await self.db.fetch_all(base_query, params)
```

## Security Considerations

### 1. API Key Management

```python
class SecureAPIKeyManager:
    def __init__(self):
        self.keys = {}
        self.load_keys_from_env()
    
    def load_keys_from_env(self):
        """Load API keys from environment variables, never hardcode"""
        self.keys = {
            'college_scorecard': os.getenv('COLLEGE_SCORECARD_API_KEY'),
            'waterloo': os.getenv('WATERLOO_API_KEY'),
            'custom_sources': os.getenv('CUSTOM_SOURCES_API_KEY')
        }
    
    def get_key(self, service: str) -> str:
        key = self.keys.get(service)
        if not key:
            raise ValueError(f"API key for {service} not configured")
        return key
```

### 2. Data Validation

```python
class ProgramDataValidator:
    @staticmethod
    def validate_program(data: dict) -> ProgramCreate:
        """Validate and sanitize program data from external sources"""
        try:
            # Sanitize HTML content
            if 'description' in data:
                data['description'] = bleach.clean(data['description'])
            
            # Validate required fields
            required_fields = ['title', 'institution_id', 'program_type']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f"Missing required field: {field}")
            
            # Validate enum values
            valid_types = ['cegep', 'university', 'college']
            if data['program_type'] not in valid_types:
                raise ValidationError(f"Invalid program_type: {data['program_type']}")
            
            return ProgramCreate(**data)
        except Exception as e:
            logger.error(f"Program validation failed: {e}")
            raise ValidationError(f"Invalid program data: {e}")
```

## Monitoring & Observability

### 1. Health Checks

```python
class SystemHealthCheck:
    async def check_health(self) -> HealthStatus:
        health = HealthStatus()
        
        # Check database connectivity
        try:
            await self.db.fetch_one("SELECT 1")
            health.database = "healthy"
        except Exception as e:
            health.database = f"unhealthy: {e}"
        
        # Check external APIs
        for service_name, service in self.external_services.items():
            try:
                await service.ping()
                health.external_services[service_name] = "healthy"
            except Exception as e:
                health.external_services[service_name] = f"unhealthy: {e}"
        
        # Check cache
        try:
            await self.cache.ping()
            health.cache = "healthy"
        except Exception as e:
            health.cache = f"unhealthy: {e}"
        
        return health
```

### 2. Metrics Collection

```python
class MetricsCollector:
    def __init__(self):
        self.request_counter = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
        self.response_histogram = Histogram('response_time_seconds', 'Response time')
        self.error_counter = Counter('api_errors_total', 'Total API errors', ['endpoint', 'error_type'])
    
    def record_request(self, endpoint: str, method: str, response_time: float, error: str = None):
        self.request_counter.labels(endpoint=endpoint, method=method).inc()
        self.response_histogram.observe(response_time)
        
        if error:
            self.error_counter.labels(endpoint=endpoint, error_type=error).inc()
```

## Deployment Architecture

### 1. Container Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/orientor
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: orientor
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  cache:
    image: redis:7-alpine
    restart: unless-stopped

  worker:
    build: .
    command: celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/orientor
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    restart: unless-stopped

volumes:
  postgres_data:
```

## Next Steps

1. **Implementation Phase 1**: Core services and database schema
2. **API Development**: REST endpoints for program search
3. **Data Integration**: Connect to identified external sources
4. **Testing Strategy**: Comprehensive unit and integration tests
5. **Performance Optimization**: Caching and query optimization
6. **Documentation**: API documentation and deployment guides

This architecture provides a solid foundation for integrating school program data while maintaining scalability, reliability, and maintainability principles aligned with the Orientor platform's existing architecture.