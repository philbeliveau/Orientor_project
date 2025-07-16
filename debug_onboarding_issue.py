#!/usr/bin/env python3
"""
Debug script to check onboarding status for a user
This will help us understand what's actually happening in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import your app modules
try:
    from backend.app.utils.database import get_db, initialize_database
    from backend.app.models import User, UserProfile
    from backend.app.models.personality_profiles import PersonalityProfile, PersonalityAssessment
except ImportError:
    print("Could not import backend modules. Make sure you're in the right directory.")
    sys.exit(1)

def debug_user_onboarding_status():
    """Debug the onboarding status for all users"""
    
    print("🔍 Debugging Onboarding Status Issue")
    print("=" * 50)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        return
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"📊 Found {len(users)} users in database")
        print()
        
        for user in users:
            print(f"👤 User ID: {user.id}, Email: {user.email}")
            
            # Check for PersonalityProfile (what determines onboarding completion)
            personality_profiles = db.query(PersonalityProfile).filter(
                PersonalityProfile.user_id == user.id
            ).all()
            
            print(f"   📋 PersonalityProfile records: {len(personality_profiles)}")
            for profile in personality_profiles:
                print(f"      - Profile ID: {profile.id}, Type: {profile.profile_type}")
                print(f"        Created: {profile.created_at}")
                print(f"        Assessment ID: {profile.assessment_id}")
            
            # Check for PersonalityAssessment (tracks onboarding sessions)
            assessments = db.query(PersonalityAssessment).filter(
                PersonalityAssessment.user_id == user.id,
                PersonalityAssessment.assessment_type == "onboarding"
            ).all()
            
            print(f"   📝 Onboarding assessments: {len(assessments)}")
            for assessment in assessments:
                print(f"      - Assessment ID: {assessment.id}, Status: {assessment.status}")
                print(f"        Started: {assessment.started_at}")
                print(f"        Completed: {assessment.completed_at}")
                print(f"        Items: {assessment.completed_items}/{assessment.total_items}")
            
            # Simulate the backend status check logic
            has_personality_profile = len(personality_profiles) > 0
            has_started_assessment = len(assessments) > 0
            
            print(f"   🎯 Onboarding Status:")
            print(f"      - isComplete: {has_personality_profile}")
            print(f"      - hasStarted: {has_started_assessment}")
            
            if has_personality_profile:
                print(f"      ✅ User should skip onboarding (redirect to dashboard)")
            else:
                print(f"      ❌ User needs onboarding (redirect to onboarding page)")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def check_backend_status_endpoint():
    """Simulate the backend status endpoint logic"""
    
    print("\n🔧 Testing Backend Status Endpoint Logic")
    print("=" * 50)
    
    # This is what the /onboarding/status endpoint does
    test_cases = [
        {
            "name": "User with completed onboarding",
            "has_personality_profile": True,
            "has_assessment": True
        },
        {
            "name": "User who started but didn't complete onboarding", 
            "has_personality_profile": False,
            "has_assessment": True
        },
        {
            "name": "New user who never started onboarding",
            "has_personality_profile": False,
            "has_assessment": False
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 Test Case: {case['name']}")
        
        # Simulate the backend logic
        personality_profile = "exists" if case["has_personality_profile"] else None
        assessment = "exists" if case["has_assessment"] else None
        
        has_started = assessment is not None
        is_complete = personality_profile is not None
        
        status = {
            "isComplete": is_complete,
            "hasStarted": has_started,
            "currentStep": "profile_generation" if has_started and not is_complete else None,
            "completedAt": "2024-01-01" if personality_profile else None
        }
        
        print(f"   Backend Response: {status}")
        
        # Simulate frontend logic
        if status["isComplete"]:
            redirect = "/dashboard"
        else:
            redirect = "/onboarding"
            
        print(f"   Frontend Redirect: {redirect}")

if __name__ == "__main__":
    try:
        debug_user_onboarding_status()
        check_backend_status_endpoint()
    except KeyboardInterrupt:
        print("\n🛑 Debug interrupted by user")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()