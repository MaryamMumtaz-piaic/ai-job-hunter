from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str = Field(..., min_length=6)
    confirm_password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    avatar_initials: str
    created_at: str


class UserInDB(BaseModel):
    id: str
    full_name: str
    email: str
    hashed_password: str
    avatar_initials: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    phone: Optional[str] = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
