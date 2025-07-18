from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserOut(UserBase):
    id: int
    onboarding_completed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)