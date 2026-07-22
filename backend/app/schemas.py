"""
Pydantic schemas used for request validation and API responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: Optional[list[str]] = None  # if None, auto-extracted


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    required_skills: list[str]
    created_at: datetime
    candidate_count: int = 0


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    filename: str
    extracted_skills: list[str]
    years_experience: Optional[float] = None
    semantic_score: float
    skill_score: float
    final_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime


class CandidateDetail(CandidateOut):
    raw_text: str
