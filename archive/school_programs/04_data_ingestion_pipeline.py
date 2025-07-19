"""
School Programs Data Ingestion Pipeline

This module provides a comprehensive data ingestion pipeline for CEGEP and university
program data from multiple sources. Designed to be modular, scalable, and fault-tolerant.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urljoin
import hashlib
import json

import aiohttp
import asyncpg
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Data Models
class ProgramData(BaseModel):
    """Normalized program data model"""
    title: str
    title_fr: Optional[str] = None
    description: Optional[str] = None
    description_fr: Optional[str] = None
    institution_name: str
    institution_type: str = Field(..., regex="^(cegep|university|college)$")
    program_type: str
    level: str
    duration_months: Optional[int] = None
    language: List[str] = Field(default_factory=lambda: ["en"])
    cip_code: Optional[str] = None
    program_code: Optional[str] = None
    admission_requirements: List[str] = Field(default_factory=list)
    career_outcomes: List[str] = Field(default_factory=list)
    tuition_cost: Optional[float] = None
    source_system: str
    source_id: str
    source_url: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('language', pre=True)
    def validate_language(cls, v):
        if isinstance(v, str):
            return [v]
        return v or ["en"]


class InstitutionData(BaseModel):
    """Normalized institution data model"""
    name: str
    name_fr: Optional[str] = None
    institution_type: str = Field(..., regex="^(cegep|university|college)$")
    country: str = "CA"
    province_state: str
    city: str
    website_url: Optional[str] = None
    source_system: str
    source_id: str


@dataclass
class IngestionResult:
    """Result of data ingestion operation"""
    source: str
    success: bool
    programs_processed: int = 0
    institutions_processed: int = 0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Abstract Base Classes
class DataSource(ABC):
    """Abstract base class for data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = AsyncRateLimiter(
            max_requests=config.get('rate_limit', 60),
            time_window=60  # 1 minute
        )
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch program data from the source"""
        pass
    
    @abstractmethod
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch institution data from the source"""
        pass
    
    async def health_check(self) -> bool:
        """Check if the data source is available"""
        try:
            # Default implementation - override if needed
            return True
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return False


class AsyncRateLimiter:
    """Async rate limiter to respect API limits"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = datetime.utcnow()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if (now - req_time).seconds < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]).seconds
            await asyncio.sleep(sleep_time)
            return await self.acquire()
        
        self.requests.append(now)
    
    async def __aenter__(self):
        await self.acquire()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# Specific Data Source Implementations
class SRAMCEGEPSource(DataSource):
    """SRAM CEGEP data source implementation"""
    
    BASE_URL = "https://www.sram.qc.ca"
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Scrape CEGEP programs from SRAM"""
        programs = []
        
        try:
            # Fetch the main programs page
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/en/programs") as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
                    html_content = await response.text()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract program links
            program_links = soup.find_all('a', class_='program-link')
            
            for link in program_links[:50]:  # Limit for example
                async with self.rate_limiter:
                    program_data = await self._scrape_program_details(link['href'])
                    if program_data:
                        programs.append(program_data)
                        
                await asyncio.sleep(1)  # Be respectful
        
        except Exception as e:
            logger.error(f"Error fetching SRAM programs: {e}")
            raise
        
        logger.info(f"Fetched {len(programs)} programs from SRAM")
        return programs
    
    async def _scrape_program_details(self, program_url: str) -> Optional[ProgramData]:
        """Scrape individual program details"""
        try:
            full_url = urljoin(self.BASE_URL, program_url)
            
            async with self.session.get(full_url) as response:
                if response.status != 200:
                    return None
                html_content = await response.text()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract program information
            title = soup.find('h1', class_='program-title')
            title_text = title.text.strip() if title else "Unknown Program"
            
            description = soup.find('div', class_='program-description')
            description_text = description.text.strip() if description else None
            
            # Extract duration (typically in format like "3 years")
            duration_elem = soup.find('span', class_='duration')
            duration_months = None
            if duration_elem:
                duration_text = duration_elem.text
                if 'year' in duration_text.lower():
                    years = int(duration_text.split()[0])
                    duration_months = years * 12
            
            # Extract institution
            institution_elem = soup.find('span', class_='institution-name')
            institution_name = institution_elem.text.strip() if institution_elem else "Unknown Institution"
            
            # Generate a unique source ID
            source_id = hashlib.md5(full_url.encode()).hexdigest()
            
            return ProgramData(
                title=title_text,
                description=description_text,
                institution_name=institution_name,
                institution_type="cegep",
                program_type="technical",  # Most SRAM programs are technical
                level="diploma",
                duration_months=duration_months,
                language=["en", "fr"],
                source_system="sram",
                source_id=source_id,
                source_url=full_url
            )
            
        except Exception as e:
            logger.error(f"Error scraping program {program_url}: {e}")
            return None
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch CEGEP institutions from SRAM"""
        institutions = []
        
        try:
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/en/colleges") as response:
                    html_content = await response.text()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            college_cards = soup.find_all('div', class_='college-card')
            
            for card in college_cards:
                name_elem = card.find('h3', class_='college-name')
                if not name_elem:
                    continue
                
                name = name_elem.text.strip()
                
                # Extract location
                location_elem = card.find('span', class_='college-location')
                city = "Montreal"  # Default
                if location_elem:
                    location_parts = location_elem.text.split(',')
                    if location_parts:
                        city = location_parts[0].strip()
                
                # Extract website
                website_elem = card.find('a', class_='college-website')
                website = website_elem['href'] if website_elem else None
                
                source_id = hashlib.md5(name.encode()).hexdigest()
                
                institutions.append(InstitutionData(
                    name=name,
                    institution_type="cegep",
                    country="CA",
                    province_state="QC",
                    city=city,
                    website_url=website,
                    source_system="sram",
                    source_id=source_id
                ))
        
        except Exception as e:
            logger.error(f"Error fetching SRAM institutions: {e}")
            raise
        
        logger.info(f"Fetched {len(institutions)} institutions from SRAM")
        return institutions


class DonneesQuebecSource(DataSource):
    """Données Québec CKAN API source"""
    
    BASE_URL = "https://www.donneesquebec.ca/recherche/api/3/action"
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch education datasets from Données Québec"""
        programs = []
        
        try:
            # Search for education-related datasets
            search_params = {
                'q': 'education',
                'rows': 100,
                'facet.field': ['organization', 'tags'],
                'fq': 'tags:education'
            }
            
            async with self.rate_limiter:
                async with self.session.get(
                    f"{self.BASE_URL}/package_search",
                    params=search_params
                ) as response:
                    data = await response.json()
            
            if not data.get('success'):
                raise Exception("API request failed")
            
            datasets = data['result']['results']
            
            for dataset in datasets:
                # Process each dataset that might contain program information
                for resource in dataset.get('resources', []):
                    if resource.get('format', '').lower() in ['csv', 'json']:
                        resource_programs = await self._process_resource(resource)
                        programs.extend(resource_programs)
        
        except Exception as e:
            logger.error(f"Error fetching Données Québec programs: {e}")
            raise
        
        logger.info(f"Fetched {len(programs)} programs from Données Québec")
        return programs
    
    async def _process_resource(self, resource: Dict) -> List[ProgramData]:
        """Process a specific resource that might contain program data"""
        programs = []
        
        try:
            resource_url = resource.get('url')
            if not resource_url:
                return programs
            
            async with self.rate_limiter:
                async with self.session.get(resource_url) as response:
                    if resource.get('format', '').lower() == 'json':
                        data = await response.json()
                    else:
                        # For CSV and other formats, we'd need additional processing
                        return programs
            
            # Process JSON data looking for program-like information
            # This is highly dependent on the actual data structure
            if isinstance(data, list):
                for item in data:
                    program = self._extract_program_from_item(item)
                    if program:
                        programs.append(program)
        
        except Exception as e:
            logger.error(f"Error processing resource {resource.get('id')}: {e}")
        
        return programs
    
    def _extract_program_from_item(self, item: Dict) -> Optional[ProgramData]:
        """Extract program data from a data item"""
        # This would need to be customized based on actual data structure
        # For now, returning None as we'd need to analyze the actual data format
        return None
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch institution data from Données Québec"""
        # Similar implementation to fetch_programs but focused on institution data
        return []


class CollegeScorecardSource(DataSource):
    """US College Scorecard API source"""
    
    BASE_URL = "https://api.data.gov/ed/collegescorecard/v1"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("College Scorecard API key required")
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch programs from College Scorecard API"""
        programs = []
        
        try:
            params = {
                'api_key': self.api_key,
                'fields': 'school.name,school.city,school.state,programs.cip_4_digit',
                'per_page': 100,
                'page': 0
            }
            
            while True:
                async with self.rate_limiter:
                    async with self.session.get(
                        f"{self.BASE_URL}/schools",
                        params=params
                    ) as response:
                        data = await response.json()
                
                if 'results' not in data:
                    break
                
                for school in data['results']:
                    school_programs = self._extract_programs_from_school(school)
                    programs.extend(school_programs)
                
                # Check if there are more pages
                if len(data['results']) < params['per_page']:
                    break
                
                params['page'] += 1
                
                # Limit to prevent excessive API calls in example
                if params['page'] >= 5:
                    break
        
        except Exception as e:
            logger.error(f"Error fetching College Scorecard programs: {e}")
            raise
        
        logger.info(f"Fetched {len(programs)} programs from College Scorecard")
        return programs
    
    def _extract_programs_from_school(self, school: Dict) -> List[ProgramData]:
        """Extract program data from school information"""
        programs = []
        
        school_name = school.get('school', {}).get('name', 'Unknown School')
        city = school.get('school', {}).get('city', 'Unknown City')
        state = school.get('school', {}).get('state', 'Unknown State')
        
        # Extract programs from CIP codes
        cip_programs = school.get('programs', {}).get('cip_4_digit', [])
        
        for cip_data in cip_programs:
            if not cip_data.get('code'):
                continue
            
            cip_code = cip_data['code']
            
            # Create program entry
            source_id = f"{school.get('id', 'unknown')}_{cip_code}"
            
            programs.append(ProgramData(
                title=f"Program {cip_code}",  # Would need CIP code lookup for actual title
                institution_name=school_name,
                institution_type="university",
                program_type="academic",
                level="bachelor",  # Default assumption
                cip_code=cip_code,
                source_system="college_scorecard",
                source_id=source_id
            ))
        
        return programs
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch institutions from College Scorecard"""
        institutions = []
        
        try:
            params = {
                'api_key': self.api_key,
                'fields': 'school.name,school.city,school.state,school.school_url',
                'per_page': 100,
                'page': 0
            }
            
            while True:
                async with self.rate_limiter:
                    async with self.session.get(
                        f"{self.BASE_URL}/schools",
                        params=params
                    ) as response:
                        data = await response.json()
                
                if 'results' not in data:
                    break
                
                for school in data['results']:
                    school_data = school.get('school', {})
                    
                    institutions.append(InstitutionData(
                        name=school_data.get('name', 'Unknown School'),
                        institution_type="university",
                        country="US",
                        province_state=school_data.get('state', 'Unknown'),
                        city=school_data.get('city', 'Unknown'),
                        website_url=school_data.get('school_url'),
                        source_system="college_scorecard",
                        source_id=str(school.get('id', 'unknown'))
                    ))
                
                if len(data['results']) < params['per_page']:
                    break
                
                params['page'] += 1
                if params['page'] >= 5:  # Limit for example
                    break
        
        except Exception as e:
            logger.error(f"Error fetching College Scorecard institutions: {e}")
            raise
        
        logger.info(f"Fetched {len(institutions)} institutions from College Scorecard")
        return institutions


# Data Processing Pipeline
class DataProcessor:
    """Process and normalize data from multiple sources"""
    
    def __init__(self):
        self.deduplication_cache = set()
    
    def normalize_program_data(self, programs: List[ProgramData]) -> List[ProgramData]:
        """Normalize and deduplicate program data"""
        normalized = []
        
        for program in programs:
            # Create a hash for deduplication
            program_hash = self._generate_program_hash(program)
            
            if program_hash in self.deduplication_cache:
                continue
            
            self.deduplication_cache.add(program_hash)
            
            # Normalize the program data
            normalized_program = self._normalize_single_program(program)
            normalized.append(normalized_program)
        
        return normalized
    
    def _generate_program_hash(self, program: ProgramData) -> str:
        """Generate a hash for program deduplication"""
        key_fields = f"{program.title}_{program.institution_name}_{program.program_type}"
        return hashlib.md5(key_fields.lower().encode()).hexdigest()
    
    def _normalize_single_program(self, program: ProgramData) -> ProgramData:
        """Normalize a single program's data"""
        # Standardize program titles
        normalized_title = program.title.strip().title()
        
        # Standardize institution names
        normalized_institution = program.institution_name.strip()
        
        # Ensure consistent language codes
        normalized_languages = []
        for lang in program.language:
            if lang.lower() in ['en', 'english']:
                normalized_languages.append('en')
            elif lang.lower() in ['fr', 'french', 'français']:
                normalized_languages.append('fr')
            else:
                normalized_languages.append(lang.lower())
        
        # Create normalized program
        return ProgramData(
            title=normalized_title,
            title_fr=program.title_fr,
            description=program.description,
            description_fr=program.description_fr,
            institution_name=normalized_institution,
            institution_type=program.institution_type.lower(),
            program_type=program.program_type.lower(),
            level=program.level.lower(),
            duration_months=program.duration_months,
            language=list(set(normalized_languages)),  # Remove duplicates
            cip_code=program.cip_code,
            program_code=program.program_code,
            admission_requirements=program.admission_requirements,
            career_outcomes=program.career_outcomes,
            tuition_cost=program.tuition_cost,
            source_system=program.source_system,
            source_id=program.source_id,
            source_url=program.source_url,
            last_updated=program.last_updated
        )


# Database Operations
class DatabaseManager:
    """Manage database operations for program data"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
    
    async def upsert_programs(self, programs: List[ProgramData]) -> int:
        """Insert or update programs in the database"""
        if not self.pool:
            raise Exception("Database pool not initialized")
        
        count = 0
        
        async with self.pool.acquire() as conn:
            for program in programs:
                await conn.execute("""
                    INSERT INTO programs (
                        title, title_fr, description, description_fr,
                        institution_name, institution_type, program_type, level,
                        duration_months, language, cip_code, program_code,
                        admission_requirements, career_outcomes, tuition_cost,
                        source_system, source_id, source_url, last_updated
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
                    )
                    ON CONFLICT (source_system, source_id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        title_fr = EXCLUDED.title_fr,
                        description = EXCLUDED.description,
                        description_fr = EXCLUDED.description_fr,
                        last_updated = EXCLUDED.last_updated
                """, 
                program.title, program.title_fr, program.description, program.description_fr,
                program.institution_name, program.institution_type, program.program_type, program.level,
                program.duration_months, program.language, program.cip_code, program.program_code,
                json.dumps(program.admission_requirements), json.dumps(program.career_outcomes), 
                program.tuition_cost, program.source_system, program.source_id, program.source_url, 
                program.last_updated)
                count += 1
        
        return count


# Main Ingestion Pipeline
class SchoolProgramsIngestionPipeline:
    """Main pipeline for ingesting school program data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources: List[DataSource] = []
        self.processor = DataProcessor()
        self.db_manager = DatabaseManager(config['database_url'])
        self.cache = redis.from_url(config.get('redis_url', 'redis://localhost:6379'))
        
    def add_data_source(self, source_class: type, source_config: Dict[str, Any]):
        """Add a data source to the pipeline"""
        source = source_class(source_config)
        self.data_sources.append(source)
    
    async def run_ingestion(self) -> List[IngestionResult]:
        """Run the complete data ingestion pipeline"""
        await self.db_manager.initialize()
        results = []
        
        try:
            for source in self.data_sources:
                result = await self._ingest_from_source(source)
                results.append(result)
                
                # Cache the result for monitoring
                await self.cache.setex(
                    f"ingestion_result:{source.name}",
                    3600,  # 1 hour
                    json.dumps(result.__dict__, default=str)
                )
        
        finally:
            await self.db_manager.close()
            await self.cache.close()
        
        return results
    
    async def _ingest_from_source(self, source: DataSource) -> IngestionResult:
        """Ingest data from a specific source"""
        start_time = datetime.utcnow()
        result = IngestionResult(source=source.name, success=False)
        
        try:
            # Check source health
            if not await source.health_check():
                result.errors.append("Source health check failed")
                return result
            
            async with source:
                # Fetch programs
                logger.info(f"Fetching programs from {source.name}")
                programs = await source.fetch_programs()
                
                # Normalize data
                logger.info(f"Normalizing {len(programs)} programs from {source.name}")
                normalized_programs = self.processor.normalize_program_data(programs)
                
                # Store in database
                logger.info(f"Storing {len(normalized_programs)} programs from {source.name}")
                stored_count = await self.db_manager.upsert_programs(normalized_programs)
                
                result.programs_processed = stored_count
                result.success = True
                
        except Exception as e:
            logger.error(f"Error ingesting from {source.name}: {e}")
            result.errors.append(str(e))
        
        finally:
            end_time = datetime.utcnow()
            result.duration_seconds = (end_time - start_time).total_seconds()
        
        return result


# Main execution function
async def main():
    """Main function to run the ingestion pipeline"""
    
    # Configuration
    config = {
        'database_url': 'postgresql://user:pass@localhost:5432/orientor',
        'redis_url': 'redis://localhost:6379',
        'college_scorecard_api_key': 'YOUR_API_KEY_HERE'  # Would come from environment
    }
    
    # Initialize pipeline
    pipeline = SchoolProgramsIngestionPipeline(config)
    
    # Add data sources
    pipeline.add_data_source(SRAMCEGEPSource, {'rate_limit': 30})  # 30 requests per minute
    pipeline.add_data_source(DonneesQuebecSource, {'rate_limit': 60})
    
    # Only add College Scorecard if API key is available
    if config.get('college_scorecard_api_key') and config['college_scorecard_api_key'] != 'YOUR_API_KEY_HERE':
        pipeline.add_data_source(CollegeScorecardSource, {
            'api_key': config['college_scorecard_api_key'],
            'rate_limit': 1000  # 1000 requests per hour
        })
    
    # Run ingestion
    logger.info("Starting school programs ingestion pipeline")
    results = await pipeline.run_ingestion()
    
    # Log results
    for result in results:
        logger.info(f"Ingestion result for {result.source}: "
                   f"Success={result.success}, "
                   f"Programs={result.programs_processed}, "
                   f"Duration={result.duration_seconds:.2f}s")
        
        if result.errors:
            logger.error(f"Errors in {result.source}: {result.errors}")


if __name__ == "__main__":
    asyncio.run(main())