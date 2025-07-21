import os
import openai
# import pinecone
from pinecone import Pinecone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import logging
from ..models import SavedRecommendation, User
from ..utils.auth import get_current_user_unified as get_current_user
from ..schemas.space import SavedRecommendationCreate
from ..utils.database import get_db
from sqlalchemy.orm import Session
import re
from typing import List, Optional, Dict
from sqlalchemy import text



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
            
        # index_name = "oasis-minilm-index"
        index_name = "oasis-384-custom"
        
        logger.info(f"Initializing Pinecone with environment: {pinecone_environment}")
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(index_name)
        # pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        # index = pinecone.Index(index_name)
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

    # Extract cognitive traits using a more specific pattern
    cognitive_traits = [
        "analytical_thinking",
        "attention_to_detail",
        "collaboration",
        "adaptability",
        "independence",
        "evaluation",
        "decision_making",
        "stress_tolerance"
    ]

    for trait in cognitive_traits:
        # Try both with and without underscores
        trait_name = trait.replace("_", " ").title()
        pattern = f"{trait_name}:\\s*(\\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[trait] = match.group(1)

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
    stress_tolerance: Optional[float] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    all_fields: Optional[Dict[str, str]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 30

class SuggestedPeer(BaseModel):
    user_id: int
    name: str
    major: Optional[str] = None
    year: Optional[int] = None
    similarity: float
    hobbies: Optional[str] = None
    interests: Optional[str] = None

class SuggestedPeersResponse(BaseModel):
    peers: List[SuggestedPeer]

from sentence_transformers import SentenceTransformer

# Global variable for lazy loading
_embedding_model = None

def get_embedding_model():
    """Get or initialize the embedding model with lazy loading"""
    global _embedding_model
    if _embedding_model is None:
        try:
            logger.info("Loading vector search embedding model...")
            # Force CPU to avoid MPS issues on macOS
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
            logger.info("Vector search embedding model loaded successfully on CPU")
        except Exception as e:
            logger.error(f"Error loading vector search embedding model: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Embedding model unavailable: {str(e)}"
            )
    return _embedding_model

@router.post("/search", response_model=SearchResponse)
async def search_embeddings(request: SearchRequest):
    """
    Search for OaSIS records using semantic similarity with locally generated MiniLM embeddings
    """
    try:
        logger.info(f"Searching with query: {request.query}")
        index = get_pinecone_index()

        # Compute query embedding
        embedding_model = get_embedding_model()
        query_embedding = embedding_model.encode(
            request.query,
            normalize_embeddings=True
        ).tolist()

        # Query Pinecone index with the vector
        try:
            pinecone_response = index.query(
                vector=query_embedding,
                top_k=request.top_k,
                include_metadata=True
            )
            logger.info("Received response from Pinecone")

        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error querying vector database: {str(e)}"
            )

        hits = pinecone_response.get("matches", [])
        logger.info(f"Found {len(hits)} matches")

        results = []
        for hit in hits:
            metadata = hit.get("metadata", {})
            text = metadata.get("text", "")
            parsed_fields = extract_fields_from_text(text)

            label = parsed_fields.get("oasis_label__final_x") or parsed_fields.get("label") or ""
            lead_statement = parsed_fields.get("lead_statement", "")
            main_duties = parsed_fields.get("main_duties", "")

            result = SearchResult(
                id=hit["id"],
                score=float(hit["score"]),
                oasis_code=hit["id"].split("-")[1] if "-" in hit["id"] else "",
                label=label,
                lead_statement=lead_statement,
                main_duties=main_duties,
                creativity=try_parse_float(parsed_fields.get("creativity")),
                leadership=try_parse_float(parsed_fields.get("leadership")),
                digital_literacy=try_parse_float(parsed_fields.get("digital_literacy")),
                critical_thinking=try_parse_float(parsed_fields.get("critical_thinking")),
                problem_solving=try_parse_float(parsed_fields.get("problem_solving")),
                stress_tolerance=try_parse_float(parsed_fields.get("stress_tolerance")),
                analytical_thinking=try_parse_float(parsed_fields.get("analytical_thinking")),
                attention_to_detail=try_parse_float(parsed_fields.get("attention_to_detail")),
                collaboration=try_parse_float(parsed_fields.get("collaboration")),
                adaptability=try_parse_float(parsed_fields.get("adaptability")),
                independence=try_parse_float(parsed_fields.get("independence")),
                evaluation=try_parse_float(parsed_fields.get("evaluation")),
                decision_making=try_parse_float(parsed_fields.get("decision_making")),
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
            not recommendation.role_problem_solving or 
            not recommendation.analytical_thinking or
            not recommendation.attention_to_detail or
            not recommendation.collaboration or
            not recommendation.adaptability or
            not recommendation.independence or
            not recommendation.evaluation or
            not recommendation.decision_making or
            not recommendation.stress_tolerance):
            
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
            
            # Extract cognitive traits
            if not recommendation.analytical_thinking:
                recommendation.analytical_thinking = extract_skill_value(full_text, "Analytical Thinking")
            if not recommendation.attention_to_detail:
                recommendation.attention_to_detail = extract_skill_value(full_text, "Attention to Detail")
            if not recommendation.collaboration:
                recommendation.collaboration = extract_skill_value(full_text, "Collaboration")
            if not recommendation.adaptability:
                recommendation.adaptability = extract_skill_value(full_text, "Adaptability")
            if not recommendation.independence:
                recommendation.independence = extract_skill_value(full_text, "Independence")
            if not recommendation.evaluation:
                recommendation.evaluation = extract_skill_value(full_text, "Evaluation")
            if not recommendation.decision_making:
                recommendation.decision_making = extract_skill_value(full_text, "Decision Making")
            if not recommendation.stress_tolerance:
                recommendation.stress_tolerance = extract_skill_value(full_text, "Stress Tolerance")
        
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
            role_problem_solving=recommendation.role_problem_solving,
            analytical_thinking=recommendation.analytical_thinking,
            attention_to_detail=recommendation.attention_to_detail,
            collaboration=recommendation.collaboration,
            adaptability=recommendation.adaptability,
            independence=recommendation.independence,
            evaluation=recommendation.evaluation,
            decision_making=recommendation.decision_making,
            stress_tolerance=recommendation.stress_tolerance,
            all_fields=recommendation.all_fields
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

@router.get("/suggested-peers", response_model=SuggestedPeersResponse)
async def get_suggested_peers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested peers for the current user"""
    try:
        # Get suggested peers from database
        query = text("""
            SELECT sp.suggested_id, sp.similarity,
                   up.name, up.major, up.year, up.hobbies
            FROM suggested_peers sp
            JOIN user_profiles up ON sp.suggested_id = up.user_id
            WHERE sp.user_id = :user_id
            ORDER BY sp.similarity DESC
        """)
        results = db.execute(query, {"user_id": current_user.id}).fetchall()
        
        # Format response
        peers = []
        for result in results:
            peer = SuggestedPeer(
                user_id=result.suggested_id,
                name=result.name,
                major=result.major,
                year=result.year,
                similarity=result.similarity,
                hobbies=result.hobbies
            )
            peers.append(peer)
        
        return SuggestedPeersResponse(peers=peers)
        
    except Exception as e:
        logger.error(f"Error getting suggested peers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_interNAL_SERVER_ERROR,
            detail="Failed to get suggested peers"
        )

@router.get("/debug")
async def debug_index():
    """
    Debug endpoint to check Pinecone index configuration
    """
    try:
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        return {
            "status": "success",
            "stats": stats,
            # "index_name": "oasis-minilm-index"
            "index_name": "oasis-384-custom"
        }
    except Exception as e:
        logger.error(f"Debug check failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        } 