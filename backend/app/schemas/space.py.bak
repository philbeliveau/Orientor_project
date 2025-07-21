from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# ===== SavedRecommendation Schemas =====
class SavedRecommendationBase(BaseModel):
    oasis_code: str
    label: str
    description: Optional[str] = None
    main_duties: Optional[str] = None
    role_creativity: Optional[float] = None
    role_leadership: Optional[float] = None
    role_digital_literacy: Optional[float] = None
    role_critical_thinking: Optional[float] = None
    role_problem_solving: Optional[float] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    stress_tolerance: Optional[float] = None
    user_analytical_thinking: Optional[float] = None
    user_attention_to_detail: Optional[float] = None
    user_collaboration: Optional[float] = None
    user_adaptability: Optional[float] = None
    user_independence: Optional[float] = None
    user_evaluation: Optional[float] = None
    user_decision_making: Optional[float] = None
    user_stress_tolerance: Optional[float] = None
    all_fields: Optional[Dict[str, Any]] = None

class SavedRecommendationCreate(SavedRecommendationBase):
    pass

class SavedRecommendation(SavedRecommendationBase):
    id: int
    user_id: int
    saved_at: datetime
    all_fields: Optional[Dict[str, Any]] = None
    personal_analysis: Optional[str] = None
    entry_qualifications: Optional[str] = None
    suggested_improvements: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True

# ===== UserNote Schemas =====
class UserNoteBase(BaseModel):
    content: str
    saved_recommendation_id: Optional[int] = None

class UserNoteCreate(UserNoteBase):
    pass

class UserNoteUpdate(BaseModel):
    content: Optional[str] = None

class UserNote(UserNoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# ===== UserSkill Schemas =====
class UserSkillBase(BaseModel):
    creativity: Optional[float] = Field(None, ge=0, le=5)
    leadership: Optional[float] = Field(None, ge=0, le=5)
    digital_literacy: Optional[float] = Field(None, ge=0, le=5)
    critical_thinking: Optional[float] = Field(None, ge=0, le=5)
    problem_solving: Optional[float] = Field(None, ge=0, le=5)
    analytical_thinking: Optional[float] = Field(None, ge=0, le=5)
    attention_to_detail: Optional[float] = Field(None, ge=0, le=5)
    collaboration: Optional[float] = Field(None, ge=0, le=5)
    adaptability: Optional[float] = Field(None, ge=0, le=5)
    independence: Optional[float] = Field(None, ge=0, le=5)
    evaluation: Optional[float] = Field(None, ge=0, le=5)
    decision_making: Optional[float] = Field(None, ge=0, le=5)
    stress_tolerance: Optional[float] = Field(None, ge=0, le=5)

class UserSkillUpdate(UserSkillBase):
    pass

# ===== Combined Schemas =====
class SkillComparison(BaseModel):
    user_skill: Optional[float] = None
    role_skill: Optional[float] = None

class SkillsComparison(BaseModel):
    creativity: SkillComparison
    leadership: SkillComparison
    digital_literacy: SkillComparison
    critical_thinking: SkillComparison
    problem_solving: SkillComparison

class CognitiveTraits(BaseModel):
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    stress_tolerance: Optional[float] = None


class RecommendationWithNotes(SavedRecommendation):
    notes: List[UserNote] = []
    skill_comparison: Optional[SkillsComparison] = None
    personal_analysis: Optional[str] = None
    entry_qualifications: Optional[str] = None
    suggested_improvements: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True 