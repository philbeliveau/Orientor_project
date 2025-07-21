# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from typing import Optional, Dict, Any
# import requests
# import json
# import logging
# import os
# from app.utils.database import get_db
# from app.models import User, UserProfile, UserSkill
# from app.utils.auth import get_current_user_unified as get_current_user, create_access_token
# from datetime import timedelta

# # Configure logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# # Get environment variables
# REACTIVE_RESUME_API_URL = os.getenv("REACTIVE_RESUME_API_URL", "http://localhost:3100/api")
# REACTIVE_RESUME_JWT_SECRET = os.getenv("REACTIVE_RESUME_JWT_SECRET", os.getenv("JWT_SECRET_KEY"))
# FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3100")

# router = APIRouter(prefix="", tags=["resume"])

# def map_profile_to_resume(profile: UserProfile, skills: UserSkill, user: User) -> Dict[str, Any]:
#     """
#     Maps the Orientor user profile data to the Reactive Resume format
#     """
#     # Format interests from comma-separated string to list if available
#     interests_list = []
#     if profile.interests:
#         interests_list = [interest.strip() for interest in profile.interests.split(',')]
    
#     # Format hobbies from text to list if available
#     hobbies_list = []
#     if profile.hobbies:
#         hobbies_list = [hobby.strip() for hobby in profile.hobbies.split(',')]
    
#     # Map skills from user_skills to resume format
#     resume_skills = []
    
#     if skills:
#         # Map only skills that have values
#         skill_mapping = {
#             "creativity": "Creativity",
#             "leadership": "Leadership",
#             "digital_literacy": "Digital Literacy",
#             "critical_thinking": "Critical Thinking",
#             "problem_solving": "Problem Solving"
#         }
        
#         for skill_key, skill_name in skill_mapping.items():
#             skill_value = getattr(skills, skill_key)
#             if skill_value is not None:
#                 # Convert skill rating from 0-5 scale to level string
#                 level = ""
#                 if skill_value >= 4.0:
#                     level = "Expert"
#                 elif skill_value >= 3.0:
#                     level = "Advanced"
#                 elif skill_value >= 2.0:
#                     level = "intermediate"
#                 else:
#                     level = "Beginner"
                
#                 resume_skills.append({
#                     "name": skill_name,
#                     "level": level,
#                     "keywords": []
#                 })
    
#     # Build the resume data structure according to Reactive Resume schema
#     resume_data = {
#         "basics": {
#             "name": profile.name or "",
#             "email": user.email,
#             "location": {
#                 "city": "",
#                 "region": profile.state_province or "",
#                 "country": profile.country or ""
#             },
#             "summary": profile.story or "My professional summary"
#         },
#         "education": [
#             {
#                 "institution": "",
#                 "area": profile.major or "",
#                 "studyType": "Bachelor's",
#                 "score": str(profile.gpa) if profile.gpa else "",
#                 "date": {
#                     "start": "",
#                     "end": ""
#                 }
#             }
#         ],
#         "skills": resume_skills,
#         "interests": [{"name": interest} for interest in interests_list],
#         "metadata": {
#             "protected": False,
#             "template": "kakuna"
#         }
#     }
    
#     return resume_data

# @router.get("/generate-token")
# def generate_resume_token(current_user: User = Depends(get_current_user)):
#     """
#     Generates a JWT token for authentication with Reactive Resume
#     """
#     try:
#         # Create JWT token with same secret as your main app
#         # but formatted for Reactive Resume's expected payload
#         access_token_expires = timedelta(minutes=120)  # longer expiry for resume editing
#         access_token = create_access_token(
#             data={"sub": current_user.email, "user_id": current_user.id},
#             expires_delta=access_token_expires
#         )
        
#         logger.info(f"Generated resume token for user ID: {current_user.id}")
#         return {"token": access_token}
#     except Exception as e:
#         logger.error(f"Error generating resume token: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate resume token: {str(e)}")

# @router.post("/create")
# async def create_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """
#     Creates a new resume in Reactive Resume using profile data
#     """
#     try:
#         logger.info(f"Creating resume for user ID: {current_user.id}")
        
#         # Get user profile and skills
#         profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
#         skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        
#         if not profile:
#             logger.warning(f"No profile found for user ID: {current_user.id}")
#             raise HTTPException(status_code=404, detail="User profile not found")
        
#         # Map profile data to resume format
#         resume_data = map_profile_to_resume(profile, skills, current_user)
        
#         # Get authentication token for Reactive Resume
#         token_response = generate_resume_token(current_user)
#         token = token_response["token"]
        
#         # Make API call to Reactive Resume
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }
        
#         # First, check if user exists in Reactive Resume, or create them
#         user_check_url = f"{REACTIVE_RESUME_API_URL}/user"
        
#         try:
#             # Create or update resume through Reactive Resume API
#             create_resume_url = f"{REACTIVE_RESUME_API_URL}/resumes"
            
#             response = requests.post(
#                 create_resume_url,
#                 headers=headers,
#                 json=resume_data
#             )
            
#             response.raise_for_status()
#             resume_data = response.json()
            
#             logger.info(f"Successfully created resume for user ID: {current_user.id}")
            
#             # Return both the resume data and a URL to edit it
#             resume_id = resume_data.get("id")
#             edit_url = f"resume/editor/{resume_id}"
            
#             return {
#                 "resume": resume_data,
#                 "edit_url": edit_url
#             }
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error communicating with Reactive Resume API: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Failed to create resume: {str(e)}")
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error creating resume: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to create resume: {str(e)}")

# @router.get("/list")
# async def list_resumes(current_user: User = Depends(get_current_user)):
#     """
#     Lists all resumes for the current user from Reactive Resume
#     """
#     try:
#         logger.info(f"Listing resumes for user ID: {current_user.id}")
#         logger.info(f"Using Reactive Resume API URL: {REACTIVE_RESUME_API_URL}")
        
#         # Get authentication token for Reactive Resume
#         token_response = generate_resume_token(current_user)
#         token = token_response["token"]
#         logger.info(f"Generated token for Reactive Resume: {token[:10]}...")
        
#         # Make API call to Reactive Resume
#         headers = {
#             "Authorization": f"Bearer {token}"
#         }
        
#         list_url = f"{REACTIVE_RESUME_API_URL}/resumes"
#         logger.info(f"Making request to Reactive Resume at: {list_url}")
        
#         try:
#             response = requests.get(list_url, headers=headers)
#             logger.info(f"Reactive Resume response status: {response.status_code}")
#             logger.info(f"Reactive Resume response headers: {response.headers}")
#             logger.info(f"Reactive Resume response body: {response.text[:500]}...")  # Log first 500 chars of response
            
#             # Check if response is empty
#             if not response.text.strip():
#                 logger.error("Received empty response from Reactive Resume")
#                 raise HTTPException(
#                     status_code=500,
#                     detail="Received empty response from Reactive Resume service"
#                 )
            
#             response.raise_for_status()
            
#             try:
#                 resumes = response.json()
#                 logger.info(f"Successfully parsed JSON response: {resumes}")
#             except json.JSONDecodeError as e:
#                 logger.error(f"Failed to parse JSON response: {str(e)}")
#                 logger.error(f"Raw response: {response.text}")
#                 raise HTTPException(
#                     status_code=500,
#                     detail=f"Invalid JSON response from Reactive Resume service: {str(e)}"
#                 )
            
#             logger.info(f"Successfully listed resumes for user ID: {current_user.id}")
#             return {"resumes": resumes}
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error communicating with Reactive Resume API: {str(e)}")
#             if hasattr(e, 'response') and e.response is not None:
#                 logger.error(f"Response status: {e.response.status_code}")
#                 logger.error(f"Response headers: {e.response.headers}")
#                 logger.error(f"Response body: {e.response.text}")
            
#             # Check if the service is simply not running
#             if isinstance(e, requests.exceptions.ConnectionError):
#                 logger.error("Connection error - Reactive Resume service may not be running")
#                 raise HTTPException(
#                     status_code=503, 
#                     detail="Reactive Resume service is not available. Please ensure the service is running."
#                 )
            
#             raise HTTPException(status_code=500, detail=f"Failed to list resumes: {str(e)}")
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error listing resumes: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to list resumes: {str(e)}")

# @router.get("")
# async def get_resumes(current_user: User = Depends(get_current_user)):
#     """
#     Root endpoint to list all resumes for the current user
#     """
#     return await list_resumes(current_user) 