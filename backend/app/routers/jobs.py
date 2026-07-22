"""
Endpoints for creating and listing job postings.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Job, Candidate
from app.schemas import JobCreate, JobOut
from app.services.skill_extractor import extract_skills

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    skills = payload.required_skills
    if not skills:
        skills = extract_skills(payload.description)

    job = Job(
        title=payload.title,
        description=payload.description,
        required_skills=skills,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    result = JobOut.model_validate(job)
    result.candidate_count = 0
    return result


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    counts = dict(
        db.query(Candidate.job_id, func.count(Candidate.id))
        .group_by(Candidate.job_id)
        .all()
    )
    results = []
    for job in jobs:
        out = JobOut.model_validate(job)
        out.candidate_count = counts.get(job.id, 0)
        results.append(out)
    return results


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    count = db.query(Candidate).filter(Candidate.job_id == job_id).count()
    out = JobOut.model_validate(job)
    out.candidate_count = count
    return out


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"detail": "Job deleted"}
