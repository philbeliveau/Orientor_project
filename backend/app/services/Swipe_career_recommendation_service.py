import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pickle
import random
import json
from app.services.Oasisembedding_service import parse_embedding, get_user_oasis_embedding
from pinecone import Pinecone
import re
from app.models.user_profile import UserProfile
import ast
import uuid
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def try_parse_float(value: Any) -> Optional[float]:
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.strip())
        return None
    except (ValueError, AttributeError, TypeError):
        return None


def extract_fields_from_text(text: str) -> Dict[str, str]:
    fields = {}

    # Try parsing as JSON (stringified dict from Pinecone metadata['text'])
    if isinstance(text, str):
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):  # basic JSON-like heuristic
            try:
                parsed = ast.literal_eval(text) if "'" in text else json.loads(text)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        key_clean = (
                            k.strip()
                             .replace(" ", "_")
                             .replace("-", "_")
                             .replace("__", "_")
                             .lower()
                        )
                        fields[key_clean] = str(v).strip()
                    return fields
            except Exception as e:
                print(f"[extract_fields_from_text] JSON parse failed: {e}")

    # Fallback to regex-based parsing
    text = text.replace("\xa0", " ")
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

# Production-grade path resolution for ML models
def get_model_path():
    """Get correct path for career recommendation model."""
    # Railway deployment path
    railway_path = "/app/app/models/career_recommender_model.pkl"
    if os.path.exists(railway_path):
        return railway_path
    
    # Local development path
    local_model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    local_path = os.path.join(local_model_dir, "career_recommender_model.pkl")
    return local_path

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
CAREER_MODEL_PATH = get_model_path()

# Load models if they exist
CAREER_MODEL = None
MODEL_LOADED = False
try:
    if os.path.exists(CAREER_MODEL_PATH):
        with open(CAREER_MODEL_PATH, 'rb') as f:
            CAREER_MODEL = pickle.load(f)
        logger.info("Career recommendation model loaded successfully")
        MODEL_LOADED = True
    else:
        logger.warning(f"Career recommendation model not found at {CAREER_MODEL_PATH}, using fallback method")
        MODEL_LOADED = False
except Exception as e:
    logger.error(f"Error loading career recommendation model: {str(e)}")
    MODEL_LOADED = False

# Extended list of career options with more diverse roles across multiple domains
# This list is for fallback only if Pinecone is unavailable
CAREER_OPTIONS = [
    # Technology Domain
    {"id": 1, "title": "Software Engineer", "description": "Develops software solutions for various applications and systems. Works with programming languages to create, test, and maintain software.", "domain": "technology"},
    {"id": 2, "title": "Data Scientist", "description": "Analyzes and interprets complex data to help guide business decisions. Uses statistical analysis, machine learning, and data visualization.", "domain": "technology"},
    {"id": 3, "title": "UX Designer", "description": "Creates user-friendly interfaces and experiences for products. Conducts user research and testing to optimize digital experiences.", "domain": "technology"},
    {"id": 4, "title": "DevOps Engineer", "description": "Manages the infrastructure and deployment pipelines. Automates processes and ensures smooth operation of tech systems.", "domain": "technology"},
    {"id": 5, "title": "AI Engineer", "description": "Develops artificial intelligence systems and applications. Works on machine learning models, neural networks, and AI algorithms.", "domain": "technology"},
    {"id": 6, "title": "Cybersecurity Specialist", "description": "Protects systems from threats and vulnerabilities. Conducts security assessments, monitors systems, and responds to incidents.", "domain": "technology"},
    {"id": 7, "title": "Cloud Architect", "description": "Designs and implements cloud computing solutions. Creates robust, scalable, and secure cloud infrastructure.", "domain": "technology"},
    
    # Business Domain
    {"id": 8, "title": "Product Manager", "description": "Oversees product development from conception to launch. Coordinates teams, sets roadmaps, and ensures products meet user needs.", "domain": "business"},
    {"id": 9, "title": "Digital Marketing Manager", "description": "Develops and implements online marketing strategies. Uses SEO, social media, content marketing, and analytics to drive growth.", "domain": "business"},
    {"id": 10, "title": "Business Analyst", "description": "Analyzes business needs and helps implement solutions. Bridges the gap between business stakeholders and technology teams.", "domain": "business"},
    {"id": 11, "title": "Financial Analyst", "description": "Analyzes financial data and market trends to guide investment decisions and business strategy.", "domain": "business"},
    {"id": 12, "title": "Management Consultant", "description": "Helps organizations improve performance through analysis of existing problems and development of plans for improvement.", "domain": "business"},
    
    # Healthcare Domain
    {"id": 13, "title": "Medical Researcher", "description": "Conducts research to improve human health, developing new treatments and understanding diseases.", "domain": "healthcare"},
    {"id": 14, "title": "Nurse Practitioner", "description": "Provides advanced nursing care, often serving as primary healthcare providers.", "domain": "healthcare"},
    {"id": 15, "title": "Health Informatics Specialist", "description": "Manages and analyzes healthcare data to improve patient care and operational efficiency.", "domain": "healthcare"},
    {"id": 16, "title": "Biomedical Engineer", "description": "Designs and develops medical equipment and devices to solve clinical problems.", "domain": "healthcare"},
    
    # Education Domain
    {"id": 17, "title": "Educational Technologist", "description": "Develops and implements technology solutions for educational settings to enhance learning.", "domain": "education"},
    {"id": 18, "title": "Curriculum Developer", "description": "Creates educational content and programs based on research, standards, and educational theory.", "domain": "education"},
    {"id": 19, "title": "Higher Education Administrator", "description": "Manages operations, programs, and services at colleges and universities.", "domain": "education"},
    
    # Creative Domain
    {"id": 20, "title": "Content Creator", "description": "Produces engaging digital content across various platforms including video, audio, and written material.", "domain": "creative"},
    {"id": 21, "title": "Game Developer", "description": "Designs and creates video games, combining technical skills with creative storytelling.", "domain": "creative"},
    {"id": 22, "title": "Digital Artist", "description": "Creates visual art using digital tools and technologies for various media and applications.", "domain": "creative"},
    
    # Science & Research Domain
    {"id": 23, "title": "Environmental Scientist", "description": "Studies environmental conditions and develops solutions to environmental problems.", "domain": "science"},
    {"id": 24, "title": "Research Scientist", "description": "Conducts experiments and investigations to expand scientific knowledge in a specific field.", "domain": "science"},
    {"id": 25, "title": "Data Analyst", "description": "Collects, processes, and performs statistical analyses on large datasets to identify patterns and trends.", "domain": "science"},
    
    # Engineering Domain
    {"id": 26, "title": "Civil Engineer", "description": "Designs and oversees construction of infrastructure projects like buildings, roads, and bridges.", "domain": "engineering"},
    {"id": 27, "title": "Mechanical Engineer", "description": "Designs, develops, and tests mechanical devices and systems.", "domain": "engineering"},
    {"id": 28, "title": "Electrical Engineer", "description": "Designs and develops electrical systems and equipment for various applications.", "domain": "engineering"},
    
    # Finance Domain
    {"id": 29, "title": "Investment Banker", "description": "Helps companies and governments raise capital and provides financial advisory services.", "domain": "finance"},
    {"id": 30, "title": "Financial Planner", "description": "Helps individuals and organizations create strategies to achieve financial goals.", "domain": "finance"}
]

# Mapping of domains to career IDs for quick lookup
DOMAIN_TO_CAREERS = {}
for career in CAREER_OPTIONS:
    domain = career.get("domain", "other")
    if domain not in DOMAIN_TO_CAREERS:
        DOMAIN_TO_CAREERS[domain] = []
    DOMAIN_TO_CAREERS[domain].append(career["id"])

# Default user embeddings for various interests (to use when a user has no embedding)
# Using 1024 dimensions which is the standard for all-mpnet-base-v2
# Generating more realistic embeddings with proper normalization and domain-specific characteristics

# Function to create a more realistic embedding vector with domain-specific patterns
def create_domain_embedding(seed=42, dim=1024):
    """
    Create a realistic embedding vector with proper normalization.
    Each domain has a unique seed to ensure different but consistent vectors.
    """
    np.random.seed(seed)
    # Generate a random vector with normal distribution
    vector = np.random.normal(0, 0.1, dim)
    # Normalize to unit length (cosine similarity ready)
    vector = vector / np.linalg.norm(vector)
    return vector.tolist()

# Generate more realistic embeddings for each domain
DEFAULT_USER_EMBEDDINGS = {
    # Each domain has a unique seed to create distinct but consistent vectors
    "tech": create_domain_embedding(seed=42),  # Technology focused
    "creative": create_domain_embedding(seed=43),  # Creative/design focused
    "business": create_domain_embedding(seed=44),  # Business/management focused
    "science": create_domain_embedding(seed=45),  # Science/research focused
    "healthcare": create_domain_embedding(seed=46),  # Healthcare focused
    "education": create_domain_embedding(seed=47),  # Education focused
    "engineering": create_domain_embedding(seed=48),  # Engineering focused
    "finance": create_domain_embedding(seed=49)  # Finance focused
}

def get_user_embedding(db: Session, user_id: int, use_oasis: bool = False) -> Optional[List[float]]:
    """
    Get the embedding for a user by first trying to use the stored embedding,
    then falling back to generating it on-the-fly
    
    Args:
        db: Database session
        user_id: ID of the user
        use_oasis: Whether to use OaSIS embeddings (default: False)
        
    Returns:
        User embedding or None if not found
    """
    try:
        # Si l'utilisation d'OaSIS est demandée, essayer d'abord d'obtenir l'embedding OaSIS
        if use_oasis:
            logger.info(f"Tentative de récupération de l'embedding OaSIS pour l'utilisateur {user_id}")
            oasis_embedding = get_user_oasis_embedding(db, user_id)
            if oasis_embedding is not None:
                logger.info(f"Embedding OaSIS trouvé pour l'utilisateur {user_id}")
                return oasis_embedding.tolist()
            else:
                logger.warning(f"Aucun embedding OaSIS trouvé pour l'utilisateur {user_id}, retour à l'embedding standard")
        
        # First try to get the stored embedding from the database
        query = text("""
            SELECT embedding, name, job_title, industry, skills, interests
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if result:
            logger.info(f"Found user profile for user {user_id}:")
            logger.info(f"Name: {result.name}")
            logger.info(f"Job Title: {result.job_title}")
            logger.info(f"Industry: {result.industry}")
            logger.info(f"Skills: {result.skills}")
            logger.info(f"interests: {result.interests}")
            
            if result.embedding:
                logger.info(f"Found stored embedding for user {user_id}")
                # Parse the embedding from the database
                if isinstance(result.embedding, str):
                    try:
                        # Handle string representation of list
                        embedding = [float(x) for x in result.embedding.strip('[]').split(',')]
                        logger.info(f"Successfully parsed stored embedding for user {user_id}")
                        logger.info(f"Embedding size: {len(embedding)}")
                        logger.info(f"First 5 values: {embedding[:5]}")
                        return embedding
                    except Exception as e:
                        logger.error(f"Error parsing stored embedding: {str(e)}")
                elif isinstance(result.embedding, list):
                    logger.info(f"Using stored embedding list for user {user_id}")
                    logger.info(f"Embedding size: {len(result.embedding)}")
                    logger.info(f"First 5 values: {result.embedding[:5]}")
                    return result.embedding
            else:
                logger.warning(f"No stored embedding found for user {user_id}")
        else:
            logger.warning(f"No user profile found for user {user_id}")
        
        logger.info(f"Generating new embedding for user {user_id}")
        
        # If no stored embedding, get user profile and generate new embedding
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.warning(f"No profile found for user {user_id}")
            return None
            
        # Clean and format skills and interests
        def clean_array(arr):
            if not arr:
                return []
            if isinstance(arr, str):
                # Split by comma and clean each item
                return [item.strip() for item in arr.split(',') if item.strip()]
            if isinstance(arr, list):
                # Clean each item without splitting characters
                return [item.strip() for item in arr if item and isinstance(item, str)]
            return []

        # Generate embedding from profile data
        profile_data = {
            "name": profile.name,
            "age": profile.age,
            "sex": profile.sex,
            "major": profile.major,
            "year": profile.year,
            "gpa": profile.gpa,
            "hobbies": clean_array(profile.hobbies),
            "country": profile.country,
            "state_province": profile.state_province,
            "unique_quality": profile.unique_quality,
            "story": profile.story,
            "favorite_movie": profile.favorite_movie,
            "favorite_book": profile.favorite_book,
            "favorite_celebrities": profile.favorite_celebrities,
            "learning_style": profile.learning_style,
            "interests": clean_array(profile.interests),
            "job_title": profile.job_title,
            "industry": profile.industry,
            "years_experience": profile.years_experience,
            "education_level": profile.education_level,
            "career_goals": profile.career_goals,
            "skills": clean_array(profile.skills)
        }
        
        # Add debug logging
        logger.info(f"Generating new embedding for user {user_id} with profile data:")
        logger.info(f"Job Title: {profile_data['job_title']}")
        logger.info(f"Industry: {profile_data['industry']}")
        logger.info(f"Skills: {profile_data['skills']}")
        logger.info(f"interests: {profile_data['interests']}")
        
        embedding = parse_embedding(profile_data)
        if embedding is not None:
            logger.info(f"Generated new embedding for user {user_id}")
            logger.info(f"Embedding size: {len(embedding)}")
            logger.info(f"First 5 values: {embedding[:5]}")
            return embedding.tolist()
            
        # If embedding generation fails, try to get a pre-generated embedding
        try:
            embedding_path = os.path.join(MODEL_DIR, f"user_{user_id}_embedding.pkl")
            if os.path.exists(embedding_path):
                with open(embedding_path, 'rb') as f:
                    user_embedding = pickle.load(f)
                logger.info(f"Loaded pre-generated embedding for user {user_id}")
                return user_embedding
        except Exception as e:
            logger.warning(f"Could not load pre-generated embedding: {str(e)}")
        
        # If all else fails, use a default embedding based on interests
        if profile_data['interests']:
            interests = " ".join(profile_data['interests']).lower()
            logger.info(f"Using interests-based default embedding: {interests}")
            if any(term in interests for term in ["tech", "software", "programming"]):
                logger.info(f"Using tech default embedding for user {user_id}")
                return DEFAULT_USER_EMBEDDINGS["tech"]
            elif any(term in interests for term in ["art", "design", "creative"]):
                logger.info(f"Using creative default embedding for user {user_id}")
                return DEFAULT_USER_EMBEDDINGS["creative"]
            elif any(term in interests for term in ["business", "management", "finance"]):
                logger.info(f"Using business default embedding for user {user_id}")
                return DEFAULT_USER_EMBEDDINGS["business"]
            elif any(term in interests for term in ["science", "research"]):
                logger.info(f"Using science default embedding for user {user_id}")
                return DEFAULT_USER_EMBEDDINGS["science"]
            elif any(term in interests for term in ["health", "medical"]):
                logger.info(f"Using healthcare default embedding for user {user_id}")
                return DEFAULT_USER_EMBEDDINGS["healthcare"]
        
        # If no profile or no matching interests, use a random default embedding
        embedding = random.choice(list(DEFAULT_USER_EMBEDDINGS.values()))
        logger.info(f"Using random default embedding for user {user_id}")
        return embedding
        
    except Exception as e:
        logger.error(f"Error getting user embedding: {str(e)}")
        return None

def get_pinecone_career_recommendations(embedding: List[float], limit: int = 30) -> List[Dict[str, Any]]:
    """
    Get career recommendations using Pinecone vector search
    
    Args:
        embedding: User embedding
        limit: Maximum number of recommendations
        
    Returns:
        List of career recommendations
    """
    try:
        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        
        if not pinecone_api_key or not pinecone_environment:
            logger.error("Pinecone API key or environment not set")
            return []
        
        logger.info(f"Initializing Pinecone with environment: {pinecone_environment}")
        
        # Initialize Pinecone client
        pc = Pinecone(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        
        # Get the index
        # index = pc.Index("oasis-minilm-index")
        index = pc.Index("oasis-384-custom")
        logger.info("Got Pinecone index")
        
        # Ensure embedding is the right format and size
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        logger.info(f"Querying Pinecone with embedding size: {len(embedding)}")
        logger.info(f"First 5 values of query embedding: {embedding[:5]}")
        
        # Query Pinecone
        try:
            # Log avant la requête Pinecone
            logger.info(f"Requête Pinecone avec paramètres de diversification")
            
            # Augmenter le nombre de résultats pour permettre une diversification post-traitement
            # Nous récupérons plus de résultats que nécessaire pour pouvoir les filtrer ensuite
            expanded_limit = min(limit * 3, 100)  # Triple le nombre de résultats, max 100
            
            # Utiliser les paramètres de diversité de Pinecone si disponibles
            query_results = index.query(
                namespace="",
                vector=embedding,
                top_k=expanded_limit,
                include_metadata=True,
                # Paramètres de diversité de Pinecone
                include_values=True,  # Inclure les vecteurs pour post-traitement
                sparse_vector=None,   # Pourrait être utilisé pour la diversification hybride
                # Paramètre alpha pour équilibrer pertinence et diversité (si supporté)
                alpha=0.3  # Valeur entre 0 et 1, où plus la valeur est élevée, plus la diversité est favorisée
            )
            
            logger.info(f"Got query results from Pinecone: {query_results}")
            
            matches = []
            if isinstance(query_results, dict):
                matches = query_results.get('matches', [])
            elif hasattr(query_results, 'matches'):
                matches = query_results.matches
            elif hasattr(query_results, 'result') and hasattr(query_results.result, 'matches'):
                matches = query_results.result.matches
            
            if not matches:
                logger.warning("No matches found in Pinecone response")
                return []
            
            logger.info(f"Found {len(matches)} matches in Pinecone response")
            
            # Analyser et diversifier les résultats
            domains = {}
            scores = []
            domain_matches = {}  # Regrouper les matches par domaine
            
            for match in matches:
                match_score = match.get('score', 0.0) if isinstance(match, dict) else getattr(match, 'score', 0.0)
                scores.append(match_score)
                
                # Extraire le domaine si disponible
                metadata = {}
                if isinstance(match, dict):
                    metadata = match.get('metadata', {})
                elif hasattr(match, 'metadata'):
                    metadata = match.metadata
                
                text = metadata.get('text', '') if isinstance(metadata, dict) else getattr(metadata, 'text', '')
                parsed_fields = extract_fields_from_text(text)
                
                # Identifier le domaine/secteur avec fallback plus robuste
                domain = (
                    parsed_fields.get("domain", "") or
                    parsed_fields.get("sector", "") or
                    parsed_fields.get("industry", "") or
                    parsed_fields.get("field", "") or
                    "unknown"
                )
                
                # Normaliser le nom du domaine
                domain = domain.lower().strip()
                if not domain or domain == "null" or domain == "none":
                    domain = "unknown"
                
                # Compter les occurrences de domaine
                domains[domain] = domains.get(domain, 0) + 1
                
                # Regrouper les matches par domaine
                if domain not in domain_matches:
                    domain_matches[domain] = []
                domain_matches[domain].append((match, match_score, parsed_fields))
            
            # Log pour analyser la diversité
            logger.info(f"Distribution des scores: min={min(scores) if scores else 0}, max={max(scores) if scores else 0}, avg={sum(scores)/len(scores) if scores else 0}")
            logger.info(f"Distribution des domaines: {domains}")
            logger.info(f"Nombre de domaines uniques: {len(domains)}")
            
            # Mécanisme de diversification post-recherche
            diversified_matches = []
            
            # 1. Trier les domaines par nombre de résultats (pour prioriser les domaines populaires)
            sorted_domains = sorted(domain_matches.keys(), key=lambda d: len(domain_matches[d]), reverse=True)
            
            # 2. Calculer combien de résultats prendre de chaque domaine
            total_domains = len(sorted_domains)
            if total_domains == 0:
                return []
                
            # Assurer un minimum de résultats par domaine
            min_per_domain = 1
            remaining_slots = limit - (min_per_domain * total_domains)
            
            # Si pas assez de slots pour le minimum par domaine, ajuster
            if remaining_slots < 0:
                # Prendre autant de domaines que possible avec au moins 1 résultat chacun
                sorted_domains = sorted_domains[:limit]
                total_domains = len(sorted_domains)
                remaining_slots = limit - total_domains
            
            # Distribuer les slots restants proportionnellement à la popularité des domaines
            domain_slots = {domain: min_per_domain for domain in sorted_domains}
            
            if remaining_slots > 0 and total_domains > 0:
                # Calculer le total des matches pour les domaines sélectionnés
                total_matches = sum(len(domain_matches[d]) for d in sorted_domains)
                
                # Distribuer proportionnellement
                for domain in sorted_domains:
                    if total_matches > 0:
                        proportion = len(domain_matches[domain]) / total_matches
                        additional_slots = max(1, int(remaining_slots * proportion))
                        domain_slots[domain] += min(additional_slots, len(domain_matches[domain]) - min_per_domain)
            
            # 3. Sélectionner les meilleurs résultats de chaque domaine
            for domain in sorted_domains:
                # Trier les matches de ce domaine par score
                domain_results = sorted(domain_matches[domain], key=lambda x: x[1], reverse=True)
                
                # Prendre les N meilleurs résultats selon les slots alloués
                slots = min(domain_slots[domain], len(domain_results))
                for i in range(slots):
                    diversified_matches.append(domain_results[i])
            
            # 4. Si nous n'avons pas assez de résultats, compléter avec les meilleurs scores restants
            if len(diversified_matches) < limit:
                # Trier tous les matches par score
                all_sorted = sorted(
                    [(m, s, f) for d in domain_matches.values() for m, s, f in d if (m, s, f) not in diversified_matches],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Ajouter les meilleurs jusqu'à atteindre la limite
                remaining_needed = limit - len(diversified_matches)
                diversified_matches.extend(all_sorted[:remaining_needed])
            
            # 5. Trier les résultats finaux par score
            diversified_matches.sort(key=lambda x: x[1], reverse=True)
            
            # Limiter au nombre demandé
            diversified_matches = diversified_matches[:limit]
            
            logger.info(f"Après diversification: {len(diversified_matches)} résultats de {len(domains)} domaines différents")
            
            # Remplacer les matches originaux par les matches diversifiés
            matches = [match for match, _, _ in diversified_matches]
            
            # Extract results
            recommendations = []
            for i, match in enumerate(matches):
                # Handle different match formats
                match_id = match.get('id', None) if isinstance(match, dict) else getattr(match, 'id', None)
                match_score = match.get('score', 0.0) if isinstance(match, dict) else getattr(match, 'score', 0.0)
                
                if not match_id:
                    continue
                    
                # Extract OASIS code from the ID
                oasis_code = match_id.split('-')[1] if '-' in match_id else match_id
                
                # Get metadata
                metadata = {}
                if isinstance(match, dict):
                    metadata = match.get('metadata', {})
                elif hasattr(match, 'metadata'):
                    metadata = match.metadata
                
                # Parse text for additional fields
                text = metadata.get('text', '') if isinstance(metadata, dict) else getattr(metadata, 'text', '')
                parsed_fields = extract_fields_from_text(text)
                logger.info(f'Extracted fields from text: {parsed_fields}')
                
                # Create result object with all fields
                recommendation = {
                    "id": i + 1,
                    "oasis_code": oasis_code,
                    "title": parsed_fields.get("oasis_label__final_x", "") or parsed_fields.get("label", "") or f"Job {oasis_code}",
                    "description": parsed_fields.get("lead_statement", "") or parsed_fields.get("description", "") or "No description available",
                    "main_duties": parsed_fields.get("main_duties", ""),
                    "score": float(match_score),
                    "creativity": try_parse_float(parsed_fields.get("creativity")),
                    "leadership": try_parse_float(parsed_fields.get("leadership")),
                    "digital_literacy": try_parse_float(parsed_fields.get("digital_literacy")),
                    "critical_thinking": try_parse_float(parsed_fields.get("critical_thinking")),
                    "problem_solving": try_parse_float(parsed_fields.get("problem_solving")),
                    "analytical_thinking": try_parse_float(parsed_fields.get("analytical_thinking")),
                    "attention_to_detail": try_parse_float(parsed_fields.get("attention_to_detail")),
                    "collaboration": try_parse_float(parsed_fields.get("collaboration")),
                    "adaptability": try_parse_float(parsed_fields.get("adaptability")),
                    "independence": try_parse_float(parsed_fields.get("independence")),
                    "evaluation": try_parse_float(parsed_fields.get("evaluation")),
                    "decision_making": try_parse_float(parsed_fields.get("decision_making")),
                    "stress_tolerance": try_parse_float(parsed_fields.get("stress_tolerance")),
                    "all_fields": parsed_fields
                }
                
                logger.info(f'Created recommendation object: {recommendation}')
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            return []
            
    except Exception as e:
        logger.error(f"Error getting Pinecone career recommendations: {str(e)}")
        return []

def get_career_recommendations_fallback(limit: int = 30, user_id: int = None, db: Session = None) -> List[Dict[str, Any]]:
    """
    Get fallback career recommendations when Pinecone is unavailable.
    Uses a combination of user profile data and RIASEC code for personalization.
    
    Args:
        limit: Maximum number of recommendations
        user_id: ID of the user (optional)
        db: Database session (optional)
        
    Returns:
        List of career recommendations
    """
    try:
        # Initialize domain weights
        domain_weights = {
            "technology": 1.0,
            "business": 1.0,
            "healthcare": 1.0,
            "education": 1.0,
            "creative": 1.0,
            "science": 1.0,
            "engineering": 1.0,
            "finance": 1.0
        }
        
        # If we have user_id and db, try to personalize based on user profile
        if user_id and db:
            try:
                # Get user profile
                profile_query = text("""
                    SELECT up.*, gr.top_3_code as riasec_code
                    FROM user_profiles up
                    LEFT JOIN gca_results gr ON up.user_id = gr.user_id
                    WHERE up.user_id = :user_id
                    ORDER BY gr.created_at DESC
                    LIMIT 1
                """)
                user_profile = db.execute(profile_query, {"user_id": user_id}).fetchone()
                
                if user_profile:
                    logger.info(f"Found user profile for personalization: {user_profile}")
                    
                    # 1. Analyser le titre de poste actuel
                    if user_profile.job_title:
                        job_title = user_profile.job_title.lower()
                        # Correspondances approximatives entre titres de poste et domaines
                        if any(tech in job_title for tech in ["software", "developer", "engineer", "data", "analyst", "it"]):
                            domain_weights["technology"] += 1.0
                        if any(biz in job_title for biz in ["manager", "director", "consultant", "analyst", "coordinator"]):
                            domain_weights["business"] += 1.0
                        if any(health in job_title for health in ["nurse", "doctor", "medical", "health", "therapist"]):
                            domain_weights["healthcare"] += 1.0
                        if any(edu in job_title for edu in ["teacher", "professor", "educator", "instructor"]):
                            domain_weights["education"] += 1.0
                        if any(creative in job_title for creative in ["designer", "artist", "writer", "creator"]):
                            domain_weights["creative"] += 1.0
                        if any(sci in job_title for sci in ["scientist", "researcher", "analyst", "specialist"]):
                            domain_weights["science"] += 1.0
                        if any(eng in job_title for eng in ["engineer", "architect", "technician"]):
                            domain_weights["engineering"] += 1.0
                        if any(fin in job_title for fin in ["financial", "accountant", "banker", "advisor"]):
                            domain_weights["finance"] += 1.0
                    
                    # 2. Analyser l'industrie
                    if user_profile.industry:
                        industry = user_profile.industry.lower()
                        # Correspondances approximatives entre industries et domaines
                        if any(tech in industry for tech in ["technology", "software", "it", "digital"]):
                            domain_weights["technology"] += 1.0
                        if any(biz in industry for biz in ["business", "consulting", "retail", "marketing"]):
                            domain_weights["business"] += 1.0
                        if any(health in industry for health in ["healthcare", "medical", "pharmaceutical"]):
                            domain_weights["healthcare"] += 1.0
                        if any(edu in industry for edu in ["education", "academic", "school"]):
                            domain_weights["education"] += 1.0
                        if any(creative in industry for creative in ["media", "entertainment", "design", "arts"]):
                            domain_weights["creative"] += 1.0
                        if any(sci in industry for sci in ["research", "science", "laboratory"]):
                            domain_weights["science"] += 1.0
                        if any(eng in industry for eng in ["engineering", "manufacturing", "construction"]):
                            domain_weights["engineering"] += 1.0
                        if any(fin in industry for fin in ["finance", "banking", "insurance"]):
                            domain_weights["finance"] += 1.0
                    
                    # 3. Analyser les intérêts
                    if user_profile.interests:
                        interests = user_profile.interests.lower() if isinstance(user_profile.interests, str) else str(user_profile.interests).lower()
                        # Correspondances approximatives entre intérêts et domaines
                        if any(tech in interests for tech in ["technology", "computers", "programming", "digital"]):
                            domain_weights["technology"] += 1.0
                        if any(biz in interests for biz in ["business", "management", "entrepreneurship"]):
                            domain_weights["business"] += 1.0
                        if any(health in interests for health in ["health", "medicine", "wellness"]):
                            domain_weights["healthcare"] += 1.0
                        if any(edu in interests for edu in ["teaching", "learning", "education"]):
                            domain_weights["education"] += 1.0
                        if any(creative in interests for creative in ["art", "design", "music", "writing"]):
                            domain_weights["creative"] += 1.0
                        if any(sci in interests for sci in ["science", "research", "analysis"]):
                            domain_weights["science"] += 1.0
                        if any(eng in interests for eng in ["engineering", "building", "construction"]):
                            domain_weights["engineering"] += 1.0
                        if any(fin in interests for fin in ["finance", "investing", "economics", "money"]):
                            domain_weights["finance"] += 1.0
                    
                    # 4. Analyser les compétences
                    if user_profile.skills:
                        skills = user_profile.skills.lower() if isinstance(user_profile.skills, str) else str(user_profile.skills).lower()
                        # Correspondances approximatives entre compétences et domaines
                        if any(tech in skills for tech in ["programming", "coding", "software", "data", "analytics"]):
                            domain_weights["technology"] += 1.0
                        if any(biz in skills for biz in ["management", "leadership", "strategy", "marketing"]):
                            domain_weights["business"] += 1.0
                        if any(health in skills for health in ["medical", "patient", "healthcare", "clinical"]):
                            domain_weights["healthcare"] += 1.0
                        if any(edu in skills for edu in ["teaching", "curriculum", "instruction", "education"]):
                            domain_weights["education"] += 1.0
                        if any(creative in skills for creative in ["design", "creative", "writing", "content"]):
                            domain_weights["creative"] += 1.0
                        if any(sci in skills for sci in ["research", "analysis", "laboratory", "scientific"]):
                            domain_weights["science"] += 1.0
                        if any(eng in skills for eng in ["engineering", "mechanical", "electrical", "design"]):
                            domain_weights["engineering"] += 1.0
                        if any(fin in skills for fin in ["financial", "accounting", "budgeting", "investment"]):
                            domain_weights["finance"] += 1.0
                    
                    # 5. Ajuster les poids en fonction du code RIASEC
                    if user_profile.riasec_code:
                        riasec_code = user_profile.riasec_code
                        logger.info(f"Code RIASEC trouvé: {riasec_code}")
                        
                        # Ajuster les poids des domaines en fonction du code RIASEC
                        if 'R' in riasec_code:  # Réaliste
                            domain_weights["engineering"] += 1.5
                            domain_weights["technology"] += 0.8
                        if 'I' in riasec_code:  # Investigateur
                            domain_weights["science"] += 1.5
                            domain_weights["technology"] += 0.8
                        if 'A' in riasec_code:  # Artistique
                            domain_weights["creative"] += 1.5
                            domain_weights["technology"] += 0.5
                        if 'S' in riasec_code:  # Social
                            domain_weights["education"] += 1.5
                            domain_weights["healthcare"] += 1.0
                        if 'E' in riasec_code:  # Entreprenant
                            domain_weights["business"] += 1.5
                            domain_weights["finance"] += 0.8
                        if 'C' in riasec_code:  # Conventionnel
                            domain_weights["finance"] += 1.5
                            domain_weights["business"] += 0.8
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du profil pour fallback: {str(e)}")
        
        logger.info(f"Poids des domaines après personnalisation: {domain_weights}")
        
        # Sélectionner des carrières en fonction des poids des domaines
        selected_careers = []
        remaining_slots = limit
        
        # Normaliser les poids pour obtenir des proportions
        total_weight = sum(domain_weights.values())
        if total_weight > 0:
            normalized_weights = {domain: weight/total_weight for domain, weight in domain_weights.items()}
        else:
            normalized_weights = {domain: 1.0/len(domain_weights) for domain in domain_weights}
        
        # Calculer le nombre de carrières à sélectionner par domaine
        domain_slots = {}
        for domain, weight in normalized_weights.items():
            # Assurer au moins une carrière par domaine avec un poids non nul
            if weight > 0:
                domain_slots[domain] = max(1, int(limit * weight))
            else:
                domain_slots[domain] = 0
        
        # Ajuster si le total dépasse la limite
        total_slots = sum(domain_slots.values())
        if total_slots > limit:
            # Réduire proportionnellement
            excess = total_slots - limit
            for domain in sorted(domain_slots.keys(), key=lambda d: domain_slots[d]):
                if domain_slots[domain] > 1 and excess > 0:
                    reduction = min(domain_slots[domain] - 1, excess)
                    domain_slots[domain] -= reduction
                    excess -= reduction
                if excess == 0:
                    break
        
        # Sélectionner les carrières par domaine
        for domain, slots in domain_slots.items():
            if slots <= 0:
                continue
                
            if domain in DOMAIN_TO_CAREERS:
                domain_careers = [c for c in CAREER_OPTIONS if c["id"] in DOMAIN_TO_CAREERS[domain]]
                # Si pas assez de carrières dans ce domaine, prendre ce qui est disponible
                num_to_select = min(slots, len(domain_careers))
                if num_to_select > 0:
                    domain_selected = random.sample(domain_careers, num_to_select)
                    selected_careers.extend(domain_selected)
        
        # Si nous n'avons pas assez de carrières, compléter avec des sélections aléatoires
        if len(selected_careers) < limit:
            remaining_careers = [c for c in CAREER_OPTIONS if c not in selected_careers]
            additional_needed = min(limit - len(selected_careers), len(remaining_careers))
            if additional_needed > 0:
                selected_careers.extend(random.sample(remaining_careers, additional_needed))
        
        # Limiter au nombre demandé (au cas où)
        selected_careers = selected_careers[:limit]
        
        # Ajouter des scores personnalisés en fonction des poids des domaines
        recommendations = []
        for career in selected_careers:
            career_copy = career.copy()
            domain = career.get("domain", "other")
            # Score de base entre 0.5 et 0.7
            base_score = random.uniform(0.5, 0.7)
            # Bonus basé sur le poids du domaine (jusqu'à 0.3 supplémentaire)
            domain_bonus = min(0.3, domain_weights.get(domain, 0) / 10)
            career_copy["score"] = round(base_score + domain_bonus, 2)
            recommendations.append(career_copy)
        
        # Trier par score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Retour de {len(recommendations)} recommandations de fallback personnalisées")
        logger.info(f"Distribution des domaines dans les recommandations: {Counter(r.get('domain', 'unknown') for r in recommendations)}")
        return recommendations
    except Exception as e:
        logger.error(f"Error getting fallback career recommendations: {str(e)}")
        return []

def get_career_recommendations(db: Session, user_id: int, limit: int = 30, use_oasis: bool = True) -> List[Dict[str, Any]]:
    """
    Get personalized career recommendations for a user using their existing embedding.
    If no embedding exists, raises an error.
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of recommendations
        use_oasis: Whether to use OaSIS embeddings (default: True)
        
    Returns:
        List of career recommendations
        
    Raises:
        ValueError: If no embedding exists for the user
    """
    try:
        # Get user embedding from the database
        logger.info(f"Getting career recommendations for user {user_id}, use_oasis={use_oasis}")
        
        # Déterminer quelle colonne d'embedding utiliser
        embedding_column = "oasis_embedding" if use_oasis else "embedding"
        
        # Query the user_profiles table for the embedding
        query = text(f"""
            SELECT {embedding_column}
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result or not getattr(result, embedding_column, None):
            logger.error(f"No {embedding_column} found for user {user_id}")
            
            # Si l'embedding OaSIS n'est pas trouvé mais demandé, essayer l'embedding standard
            if use_oasis:
                logger.info(f"Falling back to standard embedding for user {user_id}")
                return get_career_recommendations(db, user_id, limit, use_oasis=True)
            else:
                raise ValueError(f"No embedding found for user {user_id}. Please complete your profile first.")
            
        # Parse the embedding from the database
        embedding = parse_embedding(getattr(result, embedding_column))
        if embedding is None:
            logger.error(f"Failed to parse {embedding_column} for user {user_id}")
            
            # Si l'embedding OaSIS n'est pas valide mais demandé, essayer l'embedding standard
            if use_oasis:
                logger.info(f"Falling back to standard embedding for user {user_id} due to parse error")
                return get_career_recommendations(db, user_id, limit, use_oasis=True)
            else:
                raise ValueError(f"Invalid embedding format for user {user_id}")
            
        logger.info(f"Got {embedding_column} for user {user_id}, size: {len(embedding)}")
        logger.info(f"First 5 values of {embedding_column}: {embedding[:5]}")
        
        # Get recommendations from Pinecone
        recommendations = get_pinecone_career_recommendations(embedding, limit)
        
        if not recommendations:
            logger.warning(f"No recommendations found from Pinecone for user {user_id}")
            return []
            
        logger.info(f"Got {len(recommendations)} recommendations from Pinecone")
        logger.info(f"First recommendation: {recommendations[0] if recommendations else 'None'}")
        
        return recommendations
        
    except ValueError as e:
        # Re-raise ValueError for missing/invalid embeddings
        raise
    except Exception as e:
        logger.error(f"Error getting career recommendations: {str(e)}")
        raise

def save_career_recommendation(db: Session, user_id: int, career_id: int) -> bool:
    """
    Save a career recommendation for a user with all fields
    
    Args:
        db: Database session
        user_id: ID of the user
        career_id: ID of the career
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Starting save_career_recommendation for user {user_id}, career_id {career_id}")
        
        # Try to get the career details from Pinecone first
        recommendations = get_career_recommendations(db, user_id, 30)  # Fetch all recommendations
        logger.info(f"Got {len(recommendations)} recommendations")
        
        career_details = next((c for c in recommendations if c["id"] == career_id), None)
        
        if not career_details:
            logger.error(f"Career ID {career_id} not found in recommendations for user {user_id}")
            return False
            
        logger.info(f"Found career details: {career_details}")
        
        # Generate an oasis code from the Pinecone result
        oasis_code = career_details.get("oasis_code", f"career_{career_id}")
        if not oasis_code.startswith("career_"):
            oasis_code = f"career_{oasis_code}"
        
        logger.info(f"Using oasis_code: {oasis_code}")
        
        # Check if already saved
        query = text("""
            SELECT 1
            FROM saved_recommendations
            WHERE user_id = :user_id AND oasis_code = :oasis_code
        """)
        
        exists = db.execute(query, {"user_id": user_id, "oasis_code": oasis_code}).fetchone()
        
        if exists:
            logger.info(f"Career {oasis_code} already saved for user {user_id}")
            return True
        
        # Insert new saved recommendation with all fields
        query = text("""
            INSERT INTO saved_recommendations (
                user_id, oasis_code, label, description, main_duties,
                role_creativity, role_leadership, role_digital_literacy,
                role_critical_thinking, role_problem_solving,
                analytical_thinking, attention_to_detail, collaboration,
                adaptability, independence, evaluation, decision_making,
                stress_tolerance, all_fields
            ) VALUES (
                :user_id, :oasis_code, :label, :description, :main_duties,
                :role_creativity, :role_leadership, :role_digital_literacy,
                :role_critical_thinking, :role_problem_solving,
                :analytical_thinking, :attention_to_detail, :collaboration,
                :adaptability, :independence, :evaluation, :decision_making,
                :stress_tolerance, :all_fields
            )
        """)
        
        # Use the pre-extracted fields from career_details with try_parse_float for numeric fields
        values = {
            "user_id": user_id,
            "oasis_code": oasis_code,
            "label": career_details.get("title", ""),
            "description": career_details.get("description", ""),
            "main_duties": career_details.get("main_duties", ""),
            "role_creativity": try_parse_float(career_details.get("creativity")),
            "role_leadership": try_parse_float(career_details.get("leadership")),
            "role_digital_literacy": try_parse_float(career_details.get("digital_literacy")),
            "role_critical_thinking": try_parse_float(career_details.get("critical_thinking")),
            "role_problem_solving": try_parse_float(career_details.get("problem_solving")),
            "analytical_thinking": try_parse_float(career_details.get("analytical_thinking")),
            "attention_to_detail": try_parse_float(career_details.get("attention_to_detail")),
            "collaboration": try_parse_float(career_details.get("collaboration")),
            "adaptability": try_parse_float(career_details.get("adaptability")),
            "independence": try_parse_float(career_details.get("independence")),
            "evaluation": try_parse_float(career_details.get("evaluation")),
            "decision_making": try_parse_float(career_details.get("decision_making")),
            "stress_tolerance": try_parse_float(career_details.get("stress_tolerance")),
            "all_fields": json.dumps(career_details.get("all_fields", {}))
        }
        logger.info(f"Preparing to save career with values: {values}")
        
        try:
            db.execute(query, values)
            db.commit()
            logger.info(f"Successfully saved career {oasis_code} for user {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while saving career: {str(e)}")
            raise
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error in save_career_recommendation: {str(e)}")
        return False

def get_saved_careers(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get saved career recommendations for a user with all fields
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of saved career recommendations with all fields
    """
    try:
        # Get all saved recommendations for the user with all fields
        query = text("""
            SELECT 
                sr.id as id,
                sr.oasis_code as oasis_code,
                sr.label as title,
                sr.description as description,
                sr.main_duties as main_duties,
                sr.role_creativity as role_creativity,
                sr.role_leadership as role_leadership,
                sr.role_digital_literacy as role_digital_literacy,
                sr.role_critical_thinking as role_critical_thinking,
                sr.role_problem_solving as role_problem_solving,
                sr.analytical_thinking as analytical_thinking,
                sr.attention_to_detail as attention_to_detail,
                sr.collaboration as collaboration,
                sr.adaptability as adaptability,
                sr.independence as independence,
                sr.evaluation as evaluation,
                sr.decision_making as decision_making,
                sr.stress_tolerance as stress_tolerance,
                sr.all_fields as all_fields,
                sr.saved_at as saved_at
            FROM saved_recommendations sr
            WHERE sr.user_id = :user_id
            ORDER BY sr.saved_at DESC
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        saved_careers = []
        for row in result:
            # Convert all_fields from JSON string to dict if it exists
            all_fields = {}
            if row.all_fields:
                try:
                    # Check if all_fields is already a dict (from SQLAlchemy JSON column)
                    if isinstance(row.all_fields, dict):
                        all_fields = row.all_fields
                    else:
                        # It's a string, so parse it
                        all_fields = json.loads(row.all_fields)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Error decoding all_fields for career {row.id}: {e}")
            
            career = {
                "id": row.id,
                "oasis_code": row.oasis_code,
                "title": row.title,
                "description": row.description,
                "main_duties": row.main_duties,
                "role_creativity": row.role_creativity,
                "role_leadership": row.role_leadership,
                "role_digital_literacy": row.role_digital_literacy,
                "role_critical_thinking": row.role_critical_thinking,
                "role_problem_solving": row.role_problem_solving,
                "analytical_thinking": row.analytical_thinking,
                "attention_to_detail": row.attention_to_detail,
                "collaboration": row.collaboration,
                "adaptability": row.adaptability,
                "independence": row.independence,
                "evaluation": row.evaluation,
                "decision_making": row.decision_making,
                "stress_tolerance": row.stress_tolerance,
                "all_fields": all_fields,
                "saved_at": row.saved_at,
                "source": "find_your_way" if row.oasis_code and row.oasis_code.startswith("career_") else "recommendation"
            }
            saved_careers.append(career)
            logger.info(f"Retrieved career: {career['title']} with fields: {career}")
        
        logger.info(f"Retrieved {len(saved_careers)} saved careers for user {user_id}")
        return saved_careers
    except Exception as e:
        logger.error(f"Error getting saved careers: {str(e)}")
        return []