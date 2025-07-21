from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from ..utils.database import get_db
from ..models.user import User
from ..models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog, CareerProfileAggregate
from ..schemas.course import (
    CourseCreate, CourseUpdate, Course as CourseSchema,
    PsychologicalInsightCreate, PsychologicalInsight as PsychologicalInsightSchema,
    CareerSignalCreate, CareerSignal as CareerSignalSchema,
    ConversationLogCreate, ConversationLog as ConversationLogSchema,
    CourseAnalysisRequest, CourseAnalysisResponse,
    PsychologicalProfileResponse, CareerSignalsResponse,
    TargetedAnalysisRequest, TargetedAnalysisResponse, ConversationResponseRequest, ConversationAnalysisResponse
)
from ..services.course_analysis_service import CourseAnalysisService
from ..services.llm_course_service import LLMCourseService
from ..services.esco_integration_service import ESCOIntegrationService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["courses"])

# Import the unified authentication system
from ..utils.auth import get_current_user_unified as get_current_user

@router.post("/courses", response_model=CourseSchema)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new course with automatic subject categorization.
    """
    try:
        # Auto-categorize subject if not provided
        if not course.subject_category and course.course_name:
            course.subject_category = await CourseAnalysisService.categorize_course(
                course.course_name, course.description
            )
        
        # Create course in database
        db_course = Course(
            user_id=current_user.id,
            **course.dict()
        )
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        
        logger.info(f"Created course {db_course.id} for user {current_user.id}")
        return db_course
        
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create course"
        )

@router.get("/courses", response_model=List[CourseSchema])
async def get_user_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    semester: Optional[str] = None,
    year: Optional[int] = None,
    subject_category: Optional[str] = None
):
    """
    Get all courses for the current user with optional filtering.
    """
    query = db.query(Course).filter(Course.user_id == current_user.id)
    
    if semester:
        query = query.filter(Course.semester == semester)
    if year:
        query = query.filter(Course.year == year)
    if subject_category:
        query = query.filter(Course.subject_category == subject_category)
    
    courses = query.order_by(Course.created_at.desc()).all()
    return courses

@router.get("/courses/{course_id}", response_model=CourseSchema)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific course by ID.
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course

@router.put("/courses/{course_id}", response_model=CourseSchema)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a course.
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update fields
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a course and all related data.
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(course)
    db.commit()

@router.post("/courses/{course_id}/targeted-analysis", response_model=TargetedAnalysisResponse)
async def start_targeted_analysis(
    course_id: int,
    request: TargetedAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger career-focused LLM conversation for a specific course.
    """
    # Verify course exists and belongs to user
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    try:
        # Generate session ID for this conversation
        session_id = str(uuid4())
        
        # Get course context and user history
        context = await CourseAnalysisService.build_analysis_context(
            course, current_user, db, request.focus_areas
        )
        
        # Generate targeted questions using LLM
        questions = await LLMCourseService.generate_targeted_questions(
            course, context, request.focus_areas
        )
        
        # Store initial conversation log
        conversation_log = ConversationLog(
            user_id=current_user.id,
            course_id=course_id,
            session_id=session_id,
            question_intent="assess_engagement",
            question_text=f"Starting targeted analysis session for {course.course_name}",
            llm_metadata={"session_type": "targeted_analysis", "focus_areas": request.focus_areas}
        )
        db.add(conversation_log)
        db.commit()
        
        return TargetedAnalysisResponse(
            session_id=session_id,
            conversation_started=True,
            next_questions=questions,
            context_insights=context.get("initial_insights")
        )
        
    except Exception as e:
        logger.error(f"Error starting targeted analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start analysis session"
        )

@router.post("/conversations/{session_id}/respond", response_model=ConversationAnalysisResponse)
async def respond_to_question(
    session_id: str,
    request: ConversationResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process user response and generate follow-up questions or insights.
    """
    try:
        # Find the conversation session
        conversation = db.query(ConversationLog).filter(
            ConversationLog.session_id == session_id,
            ConversationLog.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
        # Process the response with LLM
        analysis_result = await LLMCourseService.analyze_response(
            request.response, request.question_id, session_id, db
        )
        
        # Store the response
        response_log = ConversationLog(
            user_id=current_user.id,
            course_id=conversation.course_id,
            session_id=session_id,
            question_intent=analysis_result.get("question_intent", "unknown"),
            question_text=request.question_id,
            response=request.response,
            extracted_insights=analysis_result.get("insights"),
            sentiment_analysis=analysis_result.get("sentiment"),
            career_implications=analysis_result.get("career_implications")
        )
        db.add(response_log)
        
        # Extract psychological insights if significant
        if analysis_result.get("insights"):
            for insight in analysis_result["insights"]:
                psych_insight = PsychologicalInsight(
                    user_id=current_user.id,
                    course_id=conversation.course_id,
                    insight_type=insight["type"],
                    insight_value=insight["value"],
                    confidence_score=insight.get("confidence", 0.7),
                    evidence_source=f"session:{session_id}, response:{request.response[:100]}"
                )
                db.add(psych_insight)
        
        # Generate career signals if applicable
        if analysis_result.get("career_signals"):
            for signal in analysis_result["career_signals"]:
                career_signal = CareerSignal(
                    user_id=current_user.id,
                    course_id=conversation.course_id,
                    signal_type=signal["type"],
                    strength_score=signal["strength"],
                    evidence_source=f"session:{session_id}, analysis",
                    pattern_metadata=signal.get("metadata")
                )
                db.add(career_signal)
        
        db.commit()
        
        return {
            "next_questions": analysis_result.get("next_questions", []),
            "insights_discovered": analysis_result.get("insights", []),
            "session_complete": analysis_result.get("session_complete", False),
            "career_recommendations": analysis_result.get("career_recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process response"
        )

@router.get("/psychological-profile/{user_id}", response_model=PsychologicalProfileResponse)
async def get_psychological_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated psychological insights for career mapping.
    """
    # Verify user access (can only view own profile for now)
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get all psychological insights for the user
        insights = db.query(PsychologicalInsight).filter(
            PsychologicalInsight.user_id == user_id
        ).all()
        
        # Get career signals
        signals = db.query(CareerSignal).filter(
            CareerSignal.user_id == user_id
        ).all()
        
        # Group insights by course
        insights_by_course = {}
        for insight in insights:
            if insight.course_id not in insights_by_course:
                insights_by_course[insight.course_id] = []
            insights_by_course[insight.course_id].append(insight)
        
        # Generate profile summary and ESCO recommendations
        profile_summary = await CourseAnalysisService.generate_profile_summary(
            insights, signals
        )
        
        esco_recommendations = await ESCOIntegrationService.generate_career_paths(
            profile_summary, signals
        )
        
        return PsychologicalProfileResponse(
            user_id=user_id,
            profile_summary=profile_summary,
            insights_by_course=insights_by_course,
            career_signals=signals,
            esco_recommendations=esco_recommendations,
            confidence_score=profile_summary.get("confidence_score", 0.5),
            last_updated=max([i.updated_at for i in insights] + [s.updated_at for s in signals])
        )
        
    except Exception as e:
        logger.error(f"Error generating psychological profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate profile"
        )

@router.get("/career-signals/{user_id}", response_model=CareerSignalsResponse)
async def get_career_signals(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract patterns for ESCO tree traversal.
    """
    # Verify user access
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get career signals with trend analysis
        signals = db.query(CareerSignal).filter(
            CareerSignal.user_id == user_id
        ).order_by(CareerSignal.created_at.desc()).all()
        
        # Analyze patterns across signals
        pattern_analysis = await CourseAnalysisService.analyze_signal_patterns(signals)
        
        # Generate ESCO tree paths
        esco_paths = await ESCOIntegrationService.generate_tree_paths(signals)
        
        # Identify trends
        trend_indicators = await CourseAnalysisService.identify_trends(signals)
        
        # Generate recommendations
        recommendations = await CourseAnalysisService.generate_recommendations(
            signals, pattern_analysis, esco_paths
        )
        
        return CareerSignalsResponse(
            user_id=user_id,
            signals=signals,
            pattern_analysis=pattern_analysis,
            esco_tree_paths=esco_paths,
            trend_indicators=trend_indicators,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error extracting career signals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract career signals"
        )

@router.get("/courses/{course_id}/insights", response_model=List[PsychologicalInsightSchema])
async def get_course_insights(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all psychological insights for a specific course.
    """
    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    insights = db.query(PsychologicalInsight).filter(
        PsychologicalInsight.course_id == course_id
    ).order_by(PsychologicalInsight.extracted_at.desc()).all()
    
    return insights

@router.get("/conversations/{session_id}/summary")
async def get_conversation_summary(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of insights and recommendations from a conversation session.
    """
    # Get all conversation logs for this session
    logs = db.query(ConversationLog).filter(
        ConversationLog.session_id == session_id,
        ConversationLog.user_id == current_user.id
    ).order_by(ConversationLog.created_at.asc()).all()
    
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found"
        )
    
    # Generate summary using LLM
    summary = await LLMCourseService.generate_session_summary(logs)
    
    return {
        "session_id": session_id,
        "summary": summary,
        "total_questions": len(logs),
        "insights_count": sum(1 for log in logs if log.extracted_insights),
        "key_discoveries": summary.get("key_discoveries", []),
        "career_recommendations": summary.get("career_recommendations", []),
        "next_steps": summary.get("next_steps", [])
    }