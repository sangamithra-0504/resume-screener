"""
Central configuration, loaded from environment variables / .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the backend/ directory regardless of the current working
# directory the process was launched from.
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/resume_screener",
)

UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Sentence-transformers model. "all-MiniLM-L6-v2" is small (~80MB), fast on CPU,
# and gives solid semantic similarity results — good for a laptop demo.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Final score = SEMANTIC_WEIGHT * semantic_similarity + SKILL_WEIGHT * skill_overlap
SEMANTIC_WEIGHT = 0.6
SKILL_WEIGHT = 0.4
