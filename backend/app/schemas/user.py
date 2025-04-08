from pydantic import BaseModel, EmailStr
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
    created_at: datetime

    class Config:
        orm_mode = True