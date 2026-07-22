"""
Endpoints for uploading resumes and retrieving ranked candidates.
"""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db
from app.models.models import Job, Candidate
from app.schemas import CandidateOut, CandidateDetail
from app.services.extractor import extract_text_from_file, UnsupportedFileType
from app.services.skill_extractor import (
    extract_skills, extract_email, extract_phone,
    extract_years_experience, extract_name,
)
from app.services.matcher import compute_final_score

router = APIRouter(prefix="/api", tags=["candidates"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 10


@router.post("/jobs/{job_id}/resumes", response_model=list[CandidateOut])
async def upload_resumes(
    job_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    created_candidates = []

    for upload in files:
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"'{upload.filename}': unsupported file type. "
                       f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Save to disk with a unique name to avoid collisions
        safe_name = f"{uuid.uuid4().hex}_{upload.filename}"
        dest_path = UPLOAD_DIR / safe_name

        with dest_path.open("wb") as f:
            shutil.copyfileobj(upload.file, f)

        size_mb = dest_path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            dest_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"'{upload.filename}' exceeds {MAX_FILE_SIZE_MB}MB limit",
            )

        try:
            raw_text = extract_text_from_file(dest_path)
        except UnsupportedFileType as e:
            dest_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=str(e))

        if not raw_text.strip():
            dest_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"'{upload.filename}': could not extract any text "
                       f"(file may be a scanned image without OCR text layer)",
            )

        candidate_skills = extract_skills(raw_text)
        scores = compute_final_score(
            job_description=job.description,
            required_skills=job.required_skills or [],
            resume_text=raw_text,
            candidate_skills=candidate_skills,
        )

        candidate = Candidate(
            job_id=job.id,
            name=extract_name(raw_text, upload.filename),
            email=extract_email(raw_text),
            phone=extract_phone(raw_text),
            filename=upload.filename,
            raw_text=raw_text,
            extracted_skills=candidate_skills,
            years_experience=extract_years_experience(raw_text),
            semantic_score=scores["semantic_score"],
            skill_score=scores["skill_score"],
            final_score=scores["final_score"],
            matched_skills=scores["matched_skills"],
            missing_skills=scores["missing_skills"],
        )
        db.add(candidate)
        created_candidates.append(candidate)

    db.commit()
    for c in created_candidates:
        db.refresh(c)

    return created_candidates


@router.get("/jobs/{job_id}/candidates", response_model=list[CandidateOut])
def list_candidates(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = (
        db.query(Candidate)
        .filter(Candidate.job_id == job_id)
        .order_by(Candidate.final_score.desc())
        .all()
    )
    return candidates


@router.get("/candidates/{candidate_id}", response_model=CandidateDetail)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"detail": "Candidate deleted"}
