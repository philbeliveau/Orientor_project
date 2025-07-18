from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.database import get_db
from app.models import User, UserProfile
from app.schemas.user import UserCreate, UserOut, UserUpdate, UserLogin, PasswordUpdate
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.schemas.user import UserLogin  # Import the new schema
from fastapi import Security, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status  # Import status
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.debug(f"Authenticating token: {token[:10]}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug("Attempting to decode JWT token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.error("No 'sub' claim found in token payload")
            raise credentials_exception
        logger.debug(f"Token is for email: {email}")
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    
    logger.debug(f"Looking up user in database for email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.error(f"User not found for email: {email}")
        raise credentials_exception
    logger.debug(f"Successfully authenticated user ID: {user.id}")
    return user

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to register user with email: {user.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        
        # Create new user
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            onboarding_completed=False,
            created_at=datetime.utcnow()
        )
        
        # Add and commit the user first to get the user_id
        db.add(db_user)
        db.flush()
        logger.info(f"Created user with ID: {db_user.id}")
        
        # Create an empty UserProfile for the new user
        user_profile = UserProfile(
            user_id=db_user.id,
            favorite_movie="",
            favorite_book="",
            favorite_celebrities="",
            learning_style="",
            interests="",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add and commit the profile
        db.add(user_profile)
        db.commit()
        logger.info(f"Created profile for user ID: {db_user.id}")
        
        return db_user
    except SQLAlchemyError as e:
        logger.error(f"Database error during user registration: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for email: {user.email}")
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
        
        logger.info(f"Successful login for user ID: {db_user.id}")
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_id": db_user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.put("/update", response_model=UserOut)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Updating user ID: {current_user.id}")
        db_user = db.query(User).filter(User.id == current_user.id).first()
        
        if not db_user:
            logger.error(f"User not found for ID: {current_user.id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_update.email:
            # Check if email is already taken
            existing_user = db.query(User).filter(User.email == user_update.email).first()
            if existing_user and existing_user.id != current_user.id:
                logger.warning(f"Email update failed - already in use: {user_update.email}")
                raise HTTPException(status_code=400, detail="Email already registered")
            db_user.email = user_update.email
        
        if user_update.password:
            db_user.hashed_password = pwd_context.hash(user_update.password)
        
        db.commit()
        logger.info(f"Successfully updated user ID: {current_user.id}")
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.put("/change-password")
def change_password(password_update: PasswordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Password change attempt for user ID: {current_user.id}")
        db_user = db.query(User).filter(User.id == current_user.id).first()
        
        if not db_user or not pwd_context.verify(password_update.old_password, db_user.hashed_password):
            logger.warning(f"Invalid password change attempt for user ID: {current_user.id}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        db_user.hashed_password = pwd_context.hash(password_update.new_password)
        db.commit()
        
        logger.info(f"Successfully changed password for user ID: {current_user.id}")
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

@router.get("/onboarding-status", response_model=dict)
def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the user has completed the onboarding process.
    Uses both the database field and personality profile as fallback.
    """
    logger.info(f"Checking onboarding status for user ID: {current_user.id}")
    
    # Check if onboarding_completed field exists and is True
    if hasattr(current_user, 'onboarding_completed') and current_user.onboarding_completed:
        return {"onboarding_completed": True}
    
    # Fallback: Check if user has a personality profile
    try:
        from ..models.personality_profiles import PersonalityProfile
        personality_profile = db.query(PersonalityProfile).filter(
            PersonalityProfile.user_id == current_user.id
        ).first()
        
        has_profile = personality_profile is not None
        
        # If they have a profile but onboarding_completed is False, update it
        if has_profile and hasattr(current_user, 'onboarding_completed') and not current_user.onboarding_completed:
            current_user.onboarding_completed = True
            db.commit()
            logger.info(f"Updated onboarding_completed for user {current_user.id} based on personality profile")
        
        return {"onboarding_completed": has_profile}
        
    except Exception as e:
        logger.error(f"Error checking personality profile: {e}")
        # If we can't check, return False for safety
        return {"onboarding_completed": False}