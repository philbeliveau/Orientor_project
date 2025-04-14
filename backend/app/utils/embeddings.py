import logging
import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..models import User, UserProfile, SuggestedPeers
from typing import List, Dict, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence_transformers not available. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Model configuration
DEFAULT_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

def get_embedding_model(model_name: Optional[str] = None) -> Any:
    """Load and return the embedding model."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("sentence_transformers is required. Install with: pip install sentence-transformers")
    
    model_name = model_name or DEFAULT_MODEL_NAME
    logger.info(f"Loading embedding model: {model_name}")
    return SentenceTransformer(model_name)

def create_profile_text(profile: UserProfile) -> str:
    """Create a text representation of a user profile for embedding."""
    parts = []
    
    if profile.name:
        parts.append(f"Name: {profile.name}")
    if profile.major:
        parts.append(f"Major: {profile.major}")
    if profile.hobbies:
        parts.append(f"Hobbies: {profile.hobbies}")
    if profile.interests:
        parts.append(f"Interests: {profile.interests}")
    if profile.unique_quality:
        parts.append(f"Unique Quality: {profile.unique_quality}")
    if profile.story:
        parts.append(f"Story: {profile.story}")
    if profile.favorite_movie:
        parts.append(f"Favorite Movie: {profile.favorite_movie}")
    if profile.favorite_book:
        parts.append(f"Favorite Book: {profile.favorite_book}")
    
    return "\n".join(parts)

def generate_and_store_embeddings(db: Session, model_name: Optional[str] = None) -> int:
    """
    Generate embeddings for users without them and store in the database.
    Returns the count of profiles processed.
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        logger.error("sentence_transformers not available. Cannot generate embeddings.")
        return 0
    
    try:
        model = get_embedding_model(model_name)
        
        # Fetch profiles that need embeddings
        profiles = db.query(UserProfile).filter(text("embedding IS NULL")).all()
        
        if not profiles:
            logger.info("No profiles found that need embeddings.")
            return 0
        
        logger.info(f"Generating embeddings for {len(profiles)} profiles...")
        count = 0
        
        for profile in profiles:
            # Create text representation of the profile
            profile_text = create_profile_text(profile)
            
            if not profile_text.strip():
                logger.warning(f"Profile for user_id {profile.user_id} has no text content. Skipping.")
                continue
            
            # Generate embedding
            embedding_vector = model.encode(profile_text)
            
            # Update database
            db.execute(
                text("UPDATE user_profiles SET embedding = :embedding WHERE id = :id"),
                {"embedding": embedding_vector.tolist(), "id": profile.id}
            )
            count += 1
            
            # Log progress periodically
            if count % 100 == 0:
                logger.info(f"Processed {count}/{len(profiles)} profiles...")
        
        db.commit()
        logger.info(f"Successfully generated embeddings for {count} profiles.")
        return count
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating embeddings: {str(e)}")
        raise

def find_and_store_similar_peers(db: Session, batch_size: int = 100, top_n: int = 5) -> int:
    """
    Find similar peers for each user and store them in the suggested_peers table.
    Returns the count of users processed.
    """
    try:
        # Get all users with embeddings
        user_ids_query = db.execute(
            text("SELECT user_id FROM user_profiles WHERE embedding IS NOT NULL")
        )
        user_ids = [row[0] for row in user_ids_query.fetchall()]
        
        if not user_ids:
            logger.info("No users found with embeddings.")
            return 0
        
        logger.info(f"Finding similar peers for {len(user_ids)} users...")
        total_processed = 0
        
        # Process in batches to avoid memory issues
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i+batch_size]
            
            for uid in batch:
                # Find top N similar users using cosine similarity
                similar_users = db.execute(
                    text("""
                        SELECT up2.user_id,
                               1 - (up1.embedding <=> up2.embedding) AS similarity
                        FROM user_profiles up1
                        JOIN user_profiles up2 ON up1.user_id != up2.user_id
                        WHERE up1.user_id = :user_id
                          AND up2.embedding IS NOT NULL
                        ORDER BY similarity DESC
                        LIMIT :limit
                    """),
                    {"user_id": uid, "limit": top_n}
                ).fetchall()
                
                # Store results
                for peer_id, similarity in similar_users:
                    db.execute(
                        text("""
                            INSERT INTO suggested_peers (user_id, suggested_id, similarity)
                            VALUES (:user_id, :suggested_id, :similarity)
                            ON CONFLICT (user_id, suggested_id) 
                            DO UPDATE SET similarity = :similarity, updated_at = NOW()
                        """),
                        {"user_id": uid, "suggested_id": peer_id, "similarity": similarity}
                    )
                
                total_processed += 1
            
            # Commit after each batch
            db.commit()
            logger.info(f"Processed {total_processed}/{len(user_ids)} users...")
        
        logger.info(f"Successfully found similar peers for {total_processed} users.")
        return total_processed
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error finding similar peers: {str(e)}")
        raise

def refresh_all_embeddings_and_peers(db: Session, model_name: Optional[str] = None) -> Dict[str, int]:
    """
    Full refresh of all embeddings and peer suggestions.
    Returns counts of operations performed.
    """
    start_time = time.time()
    
    try:
        # Clear existing embeddings
        db.execute(text("UPDATE user_profiles SET embedding = NULL"))
        db.commit()
        
        # Clear existing peer suggestions
        db.execute(text("DELETE FROM suggested_peers"))
        db.commit()
        
        # Generate new embeddings
        profiles_count = generate_and_store_embeddings(db, model_name)
        
        # Find and store similar peers
        peers_count = find_and_store_similar_peers(db) if profiles_count > 0 else 0
        
        elapsed_time = time.time() - start_time
        logger.info(f"Refresh completed in {elapsed_time:.2f} seconds")
        
        return {
            "profiles_processed": profiles_count,
            "users_with_peers": peers_count,
            "elapsed_seconds": round(elapsed_time, 2)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in refresh operation: {str(e)}")
        raise 