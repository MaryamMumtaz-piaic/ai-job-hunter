from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

APPLICATION_STATUSES = [
    "Draft",
    "Pending Approval",
    "Approved",
    "Submitted",
    "Interview",
    "Rejected",
    "Offer",
]


class Application(BaseModel):
    id: str
    user_id: str
    job_id: str
    job_title: str
    company: str
    status: str = "Draft"
    cover_letter: str = ""
    candidate_info: dict = {}
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    submitted_at: Optional[str] = None


class ApplicationCreate(BaseModel):
    job_id: str
    cover_letter: str = ""
    candidate_info: dict = {}


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    cover_letter: Optional[str] = None
    candidate_info: Optional[dict] = None
