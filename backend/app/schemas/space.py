from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from typing import Optional, Dict

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
    all_fields: Optional[Dict[str, str]] = None  # ✅ New addition to support full parsed info

class SavedRecommendationCreate(SavedRecommendationBase):
    pass

class SavedRecommendation(SavedRecommendationBase):
    id: int
    user_id: int
    saved_at: datetime
    all_fields: Optional[Dict[str, str]] = None
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

class RecommendationWithNotes(SavedRecommendation):
    notes: List[UserNote] = []
    skill_comparison: Optional[SkillsComparison] = None

    class Config:
        orm_mode = True
        from_attributes = True 