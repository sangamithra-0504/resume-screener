"""
Core ranking engine: combines semantic similarity (sentence embeddings)
with explicit skill overlap to produce a final match score.

The embedding model is loaded ONCE at module import time and reused for
every request — loading it per-request would be extremely slow.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import EMBEDDING_MODEL_NAME, SEMANTIC_WEIGHT, SKILL_WEIGHT


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """
    Lazily load and cache the sentence-transformers model.
    First call downloads the model (~80MB) if not already cached locally
    by huggingface_hub — subsequent calls are instant.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Returns a 0-100 semantic similarity score between two texts using
    cosine similarity of their sentence embeddings.

    Note: all-MiniLM-L6-v2 truncates input to 256 word-piece tokens, so
    only roughly the first page of a long resume is used for the semantic
    portion of the score. This is a known trade-off of the model choice —
    fine to mention in your report as a limitation. The skill-overlap
    score (which scans the full text) is unaffected by this limit.
    """
    model = get_model()
    embeddings = model.encode([text_a, text_b], convert_to_numpy=True)
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    # Cosine similarity is typically in [-1, 1]; clip and rescale to 0-100
    sim = max(0.0, min(1.0, float(sim)))
    return round(sim * 100, 2)


def skill_overlap_score(
    required_skills: list[str], candidate_skills: list[str]
) -> tuple[float, list[str], list[str]]:
    """
    Returns (score_0_to_100, matched_skills, missing_skills) comparing
    the job's required skills against the candidate's extracted skills.
    """
    if not required_skills:
        return 0.0, [], []

    required_set = set(s.lower() for s in required_skills)
    candidate_set = set(s.lower() for s in candidate_skills)

    matched = sorted(required_set & candidate_set)
    missing = sorted(required_set - candidate_set)

    score = round(len(matched) / len(required_set) * 100, 2)
    return score, matched, missing


def compute_final_score(
    job_description: str,
    required_skills: list[str],
    resume_text: str,
    candidate_skills: list[str],
) -> dict:
    """
    Combines semantic similarity and skill overlap into one weighted score.
    Weights are configured in app.config (SEMANTIC_WEIGHT / SKILL_WEIGHT).
    """
    sem_score = semantic_similarity(job_description, resume_text)
    skl_score, matched, missing = skill_overlap_score(required_skills, candidate_skills)

    final = round(SEMANTIC_WEIGHT * sem_score + SKILL_WEIGHT * skl_score, 2)

    return {
        "semantic_score": sem_score,
        "skill_score": skl_score,
        "final_score": final,
        "matched_skills": matched,
        "missing_skills": missing,
    }
