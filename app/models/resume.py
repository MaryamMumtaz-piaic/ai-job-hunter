from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResumeData(BaseModel):
    user_id: str
    name: str = ""
    email: str = ""
    summary: str = ""
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []
    years_of_experience: int = 0
    job_titles: list[str] = []
    industries: list[str] = []
    technologies: list[str] = []
    raw_text: str = ""
    file_path: str = ""
    portfolio_path: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
