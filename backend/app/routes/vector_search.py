import os
import openai
from pinecone import Pinecone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import logging
from ..models import SavedRecommendation
from ..routes.user import get_current_user
from ..schemas.space import SavedRecommendationCreate
from ..utils.database import get_db
from sqlalchemy.orm import Session
import re
from typing import List, Optional, Dict


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
from openai import AsyncOpenAI

# Initialize the asynchronous OpenAI client
client = AsyncOpenAI()

# Setup API
router = APIRouter(prefix="/vector", tags=["vector"])

def get_pinecone_index():
    """Get or initialize Pinecone index with proper error handling"""
    try:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")
            
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        if not pinecone_environment:
            raise ValueError("PINECONE_ENVIRONMENT environment variable is not set")
            
        index_name = "oasis-minilm-index"
        
        logger.info(f"Initializing Pinecone with environment: {pinecone_environment}")
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(index_name)
        return index
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vector search service unavailable: {str(e)}"
        )

def try_parse_float(value: str) -> Optional[float]:
    """Try to parse a string to float, return None if fails"""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None

def extract_fields_from_text(text: str) -> Dict[str, str]:
    """
    Extracts all key-value pairs from the raw Pinecone embedded text using robust pattern matching.
    """
    fields = {}

    # Replace unusual whitespace with normal space
    text = text.replace("\xa0", " ")

    # Normalize common field delimiters
    field_pattern = re.compile(r'([\w\s\-:]+):\s+([^.:|]+(?:\|[^.:]+)*)')
    matches = field_pattern.findall(text)

    for key, value in matches:
        key_clean = (
            key.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("__", "_")
            .lower()
        )
        fields[key_clean] = value.strip()

    return fields

# Models
class SearchResult(BaseModel):
    id: str
    score: float
    oasis_code: str
    label: str
    lead_statement: Optional[str] = None
    main_duties: Optional[str] = None
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    all_fields: Optional[Dict[str, str]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

@router.post("/search", response_model=SearchResponse)
async def search_embeddings(request: SearchRequest):
    """
    Search for OaSIS records using semantic similarity with Pinecone's integrated embeddings
    """
    try:
        logger.info(f"Searching with query: {request.query}")
        
        # Get Pinecone index with proper error handling
        index = get_pinecone_index()
        
        # Format query payload for integrated embeddings
        query_payload = {
            "inputs": {
                "text": request.query
            },
            "top_k": request.top_k
        }
        
        # Query Pinecone using integrated embeddings
        try:
            pinecone_response = index.search(
                namespace="", 
                query=query_payload
            )
            logger.info("Received response from Pinecone")
            logger.debug(f"Pinecone response: {pinecone_response}")
            
            # Extract hits from the response
            hits = pinecone_response.result.hits if hasattr(pinecone_response, 'result') else []
            logger.info(f"Found {len(hits)} matches")
            
            if not hits:
                return SearchResponse(query=request.query, results=[])
            
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error querying vector database: {str(e)}"
            )

        results = []
        for hit in hits:
            oasis_code = hit['_id'].split('-')[1] if '-' in hit['_id'] else ""
            fields = hit.get('fields', {})
            text = fields.get('text', '')

            # print(f'oasis_code: {oasis_code}')
            # print(f'fields: {fields}')
            # print(f'text: {text}')

            parsed_fields = {}
            for match in re.finditer(r"([^:\n\r]+?):\s*(.*?)(?=  [A-Z][a-z]+:|$)", text):
                # raw_key = match.group(1).strip()
                # value = match.group(2).strip()
                # parsed_fields[raw_key] = value
                parsed_fields = extract_fields_from_text(text)
            print(f'parsed_fields: {parsed_fields}')


            label = parsed_fields.get("oasis_label__final_x") or parsed_fields.get("label") or ""
            lead_statement = parsed_fields.get("Lead statement", "")
            main_duties = parsed_fields.get("Main duties", "")

            result = SearchResult(
                id=hit['_id'],
                score=float(hit['_score']),
                oasis_code=oasis_code,
                label=label,
                lead_statement=lead_statement,
                main_duties=main_duties,
                creativity=try_parse_float(parsed_fields.get("Creativity")),
                leadership=try_parse_float(parsed_fields.get("Leadership")),
                digital_literacy=try_parse_float(parsed_fields.get("Digital Literacy")),
                critical_thinking=try_parse_float(parsed_fields.get("Critical Thinking")),
                problem_solving=try_parse_float(parsed_fields.get("Problem Solving")),
                all_fields=parsed_fields
            )
            results.append(result)

        return SearchResponse(query=request.query, results=results)
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

@router.post("/search/save", status_code=status.HTTP_201_CREATED)
async def save_search_result(
    recommendation: SavedRecommendationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Save a search result as a recommendation in the user's space
    """
    try:
        # Check if this recommendation is already saved
        existing = db.query(SavedRecommendation).filter(
            SavedRecommendation.user_id == current_user.id,
            SavedRecommendation.oasis_code == recommendation.oasis_code
        ).first()
        
        if existing:
            return {"message": "This recommendation is already saved", "id": existing.id}
        
        # Extract skill values from text if not provided
        if (not recommendation.role_creativity or 
            not recommendation.role_leadership or
            not recommendation.role_digital_literacy or
            not recommendation.role_critical_thinking or
            not recommendation.role_problem_solving):
            
            # Helper function to extract skill values using regex
            def extract_skill_value(text, skill_name):
                pattern = f"{skill_name.replace('_', ' ').title()}: (\\d+)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return float(match.group(1))
                return None
            
            # Try to extract from description or main_duties
            full_text = ""
            if recommendation.description:
                full_text += recommendation.description + " "
            if recommendation.main_duties:
                full_text += recommendation.main_duties
                
            # Extract role skill values
            if not recommendation.role_creativity:
                recommendation.role_creativity = extract_skill_value(full_text, "Creativity")
            if not recommendation.role_leadership:
                recommendation.role_leadership = extract_skill_value(full_text, "Leadership")
            if not recommendation.role_digital_literacy:
                recommendation.role_digital_literacy = extract_skill_value(full_text, "Digital Literacy")
            if not recommendation.role_critical_thinking:
                recommendation.role_critical_thinking = extract_skill_value(full_text, "Critical Thinking")
            if not recommendation.role_problem_solving:
                recommendation.role_problem_solving = extract_skill_value(full_text, "Problem Solving")
        
        # Create new saved recommendation
        new_recommendation = SavedRecommendation(
            user_id=current_user.id,
            oasis_code=recommendation.oasis_code,
            label=recommendation.label,
            description=recommendation.description,
            main_duties=recommendation.main_duties,
            role_creativity=recommendation.role_creativity,
            role_leadership=recommendation.role_leadership,
            role_digital_literacy=recommendation.role_digital_literacy,
            role_critical_thinking=recommendation.role_critical_thinking,
            role_problem_solving=recommendation.role_problem_solving
        )
        
        db.add(new_recommendation)
        db.commit()
        db.refresh(new_recommendation)
        
        return {"message": "Recommendation saved successfully", "id": new_recommendation.id}
        
    except Exception as e:
        logger.error(f"Error saving recommendation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error saving recommendation: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Check if the vector search service is healthy
    """
    try:
        logger.info("Checking Pinecone health...")
        stats = index.describe_index_stats()
        vector_count = stats.get("total_vector_count", 0)
        logger.info(f"Pinecone index contains {vector_count} vectors")
        return {
            "status": "healthy",
            "vector_count": vector_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vector search service unhealthy: {str(e)}") 