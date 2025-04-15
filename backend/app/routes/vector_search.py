import os
import openai
from pinecone import Pinecone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import logging

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

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
index_name = "oasis-minilm-index"

logger.info(f"Initializing Pinecone with environment: {pinecone_environment}")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)
    logger.info("Successfully initialized Pinecone")
except Exception as e:
    logger.error(f"Error initializing Pinecone: {e}")
    # We'll handle errors later in the endpoint

def try_parse_float(value: str) -> Optional[float]:
    """Try to parse a string to float, return None if fails"""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None

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
            print(pinecone_response)
            
            # Extract hits from the response
            hits = pinecone_response.result.hits if hasattr(pinecone_response, 'result') else []
            logger.info(f"Found {len(hits)} matches")
            
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            raise HTTPException(status_code=500, detail=f"Error querying Pinecone: {str(e)}")

        # Format results
        results = {}
        for hit in hits:
            # Extract the OASIS code from the _id (format: oasis-{code}-{number})
            oasis_code = hit['_id'].split('-')[1] if len(hit['_id'].split('-')) > 1 else ""
            
            # Extract text fields from the response
            fields = hit.get('fields', {})
            text = fields.get('text', '')
            
            # Parse the text to extract label and other fields
            text_parts = text.split('. ')
            label = ""
            lead_statement = ""
            main_duties = ""
            creativity = None
            leadership = None
            digital_literacy = None
            critical_thinking = None
            problem_solving = None
            
            for part in text_parts:
                if part.startswith("Occupation: "):
                    label = part.replace("Occupation: ", "")
                elif part.startswith("Description: "):
                    lead_statement = part.replace("Description: ", "")
                elif part.startswith("Main duties: "):
                    main_duties = part.replace("Main duties: ", "")
                elif part.startswith("Creativity: "):
                    creativity = try_parse_float(part.replace("Creativity: ", ""))
                elif part.startswith("Leadership: "):
                    leadership = try_parse_float(part.replace("Leadership: ", ""))
                elif part.startswith("Digital Literacy: "):
                    digital_literacy = try_parse_float(part.replace("Digital Literacy: ", ""))
                elif part.startswith("Critical Thinking: "):
                    critical_thinking = try_parse_float(part.replace("Critical Thinking: ", ""))
                elif part.startswith("Problem Solving: "):
                    problem_solving = try_parse_float(part.replace("Problem Solving: ", ""))
                    
            if oasis_code not in results:
                results[oasis_code] = SearchResult(
                    id=hit['_id'],
                    score=float(hit['_score']),
                    oasis_code=oasis_code,
                    label=label,
                    lead_statement=lead_statement,
                    main_duties=main_duties,
                    creativity=creativity,
                    leadership=leadership,
                    digital_literacy=digital_literacy,
                    critical_thinking=critical_thinking,
                    problem_solving=problem_solving
                )

        return SearchResponse(
            query=request.query,
            results=list(results.values())
        )

    except Exception as e:
        logger.error(f"Error in search_embeddings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error performing vector search: {str(e)}")

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