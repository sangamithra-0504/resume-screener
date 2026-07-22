"""
ORM models: Job, Candidate.

A Job represents a job posting/description the recruiter wants to screen
resumes against. A Candidate represents one uploaded resume, parsed and
scored against a specific Job.
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)  # list[str]
    created_at = Column(DateTime, default=datetime.utcnow)

    candidates = relationship(
        "Candidate", back_populates="job", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)

    extracted_skills = Column(JSON, default=list)  # list[str]
    years_experience = Column(Float, nullable=True)

    semantic_score = Column(Float, default=0.0)   # 0-100
    skill_score = Column(Float, default=0.0)       # 0-100
    final_score = Column(Float, default=0.0)       # 0-100

    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="candidates")
