"""
Extracts skills, contact info, and rough years-of-experience from raw text.

Uses simple, explainable techniques (regex + keyword matching against a
curated skills taxonomy) rather than a black-box model — deliberate choice
for a project you'll need to explain in a viva.
"""
import re
from app.services.skills_db import SKILLS_DB_LOWER

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3,4}\)?[\s-]?)\d{3,4}[\s-]?\d{3,4}")
YEARS_EXP_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)\s*(?:of)?\s*(?:experience)?",
    re.IGNORECASE,
)


def extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_RE.search(text)
    if not match:
        return None
    phone = match.group(0).strip()
    # Filter out obviously-too-short false positives (e.g. random numbers)
    digits = re.sub(r"\D", "", phone)
    return phone if len(digits) >= 7 else None


def extract_years_experience(text: str) -> float | None:
    matches = YEARS_EXP_RE.findall(text)
    if not matches:
        return None
    try:
        years = [float(m) for m in matches]
        return max(years)  # take the largest mentioned figure
    except ValueError:
        return None


def extract_name(text: str, filename: str) -> str | None:
    """
    Heuristic: assume the candidate's name is on one of the first few
    non-empty lines, and looks like a short Title-Case line (not an
    email, not a bullet point, not too long).
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:6]:
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            if line.isupper() or line.istitle():
                return line.title()
    # Fallback: use filename without extension
    stem = filename.rsplit(".", 1)[0]
    return stem.replace("_", " ").replace("-", " ").title()


def extract_skills(text: str) -> list[str]:
    """
    Matches curated skills against the text using word-boundary-aware
    substring search. Returns skills in their canonical (lowercase) form,
    matched longest-first so e.g. "machine learning" is matched before
    just "learning" would ever be considered (it isn't in the DB, but
    the principle holds for overlapping multi-word skills).
    """
    text_lower = f" {text.lower()} "
    found = []
    for skill in SKILLS_DB_LOWER:
        # Build a lenient boundary pattern; skills may contain '.', '+', '#'
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))
