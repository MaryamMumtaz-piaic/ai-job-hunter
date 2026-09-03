from pydantic import BaseModel, Field
from typing import Optional


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    country: str
    work_mode: str
    employment_type: str
    experience_level: str
    salary_min: Optional[int] = 0
    salary_max: Optional[int] = 0
    currency: str = "USD"
    description: str = ""
    requirements: list[str] = []
    skills: list[str] = []
    benefits: list[str] = []
    posted_date: str = ""
    company_description: str = ""
    industry: str = ""
    match_score: float = 0.0
    match_reason: str = ""
    matched_skills: list[str] = []
    missing_skills: list[str] = []


class JobMatchRequest(BaseModel):
    resume_data: dict
    preferences: dict


class SavedJob(BaseModel):
    user_id: str
    job_id: str
    saved_at: str
