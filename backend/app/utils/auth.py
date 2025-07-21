"""
Unified Authentication System for Orientor Platform

This module provides standardized authentication that:
- Accepts base64 tokens (frontend compatibility) 
- Returns proper SQLAlchemy User objects (database compatibility)
- Ensures consistent dependency injection across all routers

Usage:
    from app.utils.auth import get_current_user_unified
    
    @router.get("/endpoint")
    async def endpoint(current_user: User = Depends(get_current_user_unified)):
        # current_user is guaranteed to be a User object with .id, .email attributes
        return db.query(Model).filter(Model.user_id == current_user.id).all()
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
import base64
import logging

from app.utils.database import get_db
from app.models import User

# Configure logging
logger = logging.getLogger(__name__)

async def get_current_user_unified(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Unified authentication function that:
    - Accepts base64 tokens from frontend
    - Returns proper SQLAlchemy User objects for database operations
    - Provides consistent error handling
    
    Args:
        authorization: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User: SQLAlchemy User object with .id, .email, etc. attributes
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("🔒 No authorization token provided")
        raise HTTPException(status_code=401, detail="No authorization token")
    
    try:
        # Extract and decode base64 token
        token = authorization.split(" ")[1]
        decoded = base64.b64decode(token).decode()
        email, user_id, onboarding_completed, timestamp = decoded.split(":", 3)
        
        logger.debug(f"🔍 Authenticating user_id: {user_id}, email: {email}")
        
        # Fetch actual User object from database
        current_user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not current_user:
            logger.warning(f"🚫 User not found in database: user_id={user_id}")
            raise HTTPException(status_code=401, detail="User not found")
            
        # Verify email matches (additional security check)
        if current_user.email != email:
            logger.error(f"🚨 Email mismatch: token={email}, db={current_user.email}")
            raise HTTPException(status_code=401, detail="Token validation failed")
            
        logger.info(f"✅ Authentication successful: {current_user.email} (ID: {current_user.id})")
        return current_user
        
    except ValueError as e:
        logger.error(f"❌ Token decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token format")
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns User object if authenticated, None if not
    Useful for endpoints that work for both authenticated and anonymous users
    
    Args:
        authorization: Bearer token from Authorization header (optional)
        db: Database session
        
    Returns:
        Optional[User]: User object if authenticated, None if not authenticated
    """
    
    if not authorization or not authorization.startswith("Bearer "):
        logger.debug("🔓 No authentication provided - returning None")
        return None
        
    try:
        return await get_current_user_unified(authorization, db)
    except HTTPException:
        logger.debug("🔓 Authentication failed - returning None for optional auth")
        return None


def require_onboarding_complete(current_user: User) -> User:
    """
    Dependency that ensures user has completed onboarding
    Use this for endpoints that require full user setup
    
    Args:
        current_user: Authenticated user from get_current_user_unified
        
    Returns:
        User: The same user object if onboarding is complete
        
    Raises:
        HTTPException: 403 if onboarding not complete
    """
    
    # Check if user has completed onboarding (implementation depends on your User model)
    # This is a placeholder - adjust based on your actual onboarding field
    if hasattr(current_user, 'onboarding_completed') and not current_user.onboarding_completed:
        logger.warning(f"🚫 User {current_user.email} has not completed onboarding")
        raise HTTPException(
            status_code=403, 
            detail="Please complete onboarding to access this feature"
        )
        
    return current_user


# Convenience dependency for endpoints requiring completed onboarding
async def get_current_user_with_onboarding(
    current_user: User = Depends(get_current_user_unified)
) -> User:
    """
    Authentication + onboarding requirement in one dependency
    
    Usage:
        @router.get("/advanced-feature")
        async def advanced_feature(user: User = Depends(get_current_user_with_onboarding)):
            # User is authenticated AND has completed onboarding
    """
    return require_onboarding_complete(current_user)


# Legacy compatibility functions (for gradual migration)
async def get_current_user_legacy_compatible(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Legacy compatibility wrapper - returns the same dict format as before
    Use only for gradual migration of old endpoints
    
    DEPRECATED: Use get_current_user_unified instead
    """
    logger.warning("⚠️ Using deprecated legacy authentication - migrate to get_current_user_unified")
    
    user = await get_current_user_unified(authorization, db)
    
    # Return dict format for compatibility
    return {
        "id": user.id,
        "email": user.email,
        "name": user.email.split("@")[0] if user.email else "unknown",
        "onboarding_completed": getattr(user, 'onboarding_completed', True)
    }


# Export the main authentication functions
__all__ = [
    "get_current_user_unified",
    "get_current_user_optional", 
    "get_current_user_with_onboarding",
    "require_onboarding_complete"
]