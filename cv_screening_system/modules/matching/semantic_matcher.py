import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


_model = None

# Synonym mapping: JD skill (lowercase) → CV terms that indicate proficiency
SKILL_SYNONYMS: dict[str, list[str]] = {
    "python": [
        "python", "python3", "pandas", "numpy", "scipy",
        "django", "flask", "fastapi", "pytorch", "tensorflow",
    ],
    "sql": [
        "sql", "mysql", "postgresql", "postgres", "sqlite",
        "oracle", "sql server", "tsql", "plsql",
    ],
    "data visualization": [
        "data visualization", "visualization", "data viz",
        "tableau", "power bi", "powerbi", "matplotlib",
        "seaborn", "plotly", "charts", "dashboards", "grafana",
    ],
    "tableau": ["tableau", "tableau desktop", "tableau server"],
    "statistics": [
        "statistics", "statistical", "probability",
        "hypothesis testing", "regression", "bayesian",
        "anova", "statistical modeling",
    ],
    "database": [
        "database", "databases", "sql", "nosql", "mongodb",
        "mysql", "postgresql", "redis", "dynamodb",
        "cassandra", "oracle", "data modeling",
    ],
    "system design": [
        "system design", "software architecture", "architecture",
        "distributed systems", "scalability", "high availability",
    ],
    "microservices": [
        "microservices", "micro services", "docker",
        "kubernetes", "containerization", "api gateway",
    ],
    "java": ["java", "jdk", "jvm", "spring", "spring boot", "maven", "gradle"],
    "kotlin": ["kotlin"],
    "android": ["android", "android sdk", "android studio"],
    "mobile ui": [
        "mobile ui", "mobile interface", "ui design",
        "material design", "mobile layout", "responsive design",
    ],
    "rest api": [
        "rest api", "restful", "api development", "web api",
        "http api", "endpoint",
    ],
    "data analysis": [
        "data analysis", "data analytics", "data analyst",
        "analytical", "data mining", "eda",
    ],
}


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def normalize_text(text: str) -> str:
    """Lowercase, strip special characters, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.\,\/\+\#\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get_synonyms(skill: str) -> list[str]:
    return SKILL_SYNONYMS.get(skill.lower(), [skill.lower()])


def _keyword_match_score(cv_text: str, skill: str) -> float:
    """Return 0.85 if any synonym of the skill appears in the CV text."""
    for synonym in _get_synonyms(skill):
        if synonym in cv_text:
            return 0.85
    return 0.0


def _expand_skill_for_embedding(skill: str) -> str:
    """Build a richer phrase for the skill embedding."""
    synonyms = _get_synonyms(skill)
    unique = list(dict.fromkeys([skill.lower()] + synonyms))
    return ", ".join(unique)


def compute_similarity(cv_text: str, skills: list[str]) -> np.ndarray:
    """Hybrid similarity: max(semantic embedding, keyword match) per skill.

    1. Encode the *entire* CV as a single embedding.
    2. Encode each skill (with synonym expansion) as a single embedding.
    3. Cosine similarity between CV embedding and each skill embedding.
    4. Keyword/synonym lookup in the normalised CV text.
    5. Per-skill score = max(semantic, keyword).
    """
    model = _get_model()
    normalized_cv = normalize_text(cv_text)

    cv_embedding = model.encode([normalized_cv])

    skill_texts = [_expand_skill_for_embedding(s) for s in skills]
    skill_embeddings = model.encode(skill_texts)

    semantic_sims = cosine_similarity(cv_embedding, skill_embeddings)[0]

    keyword_scores = np.array(
        [_keyword_match_score(normalized_cv, s) for s in skills]
    )

    return np.maximum(semantic_sims, keyword_scores)


def find_matching_skills(
    cv_text: str,
    skills: list[str],
    match_threshold: float = 0.60,
) -> tuple[list[str], list[str], list[float]]:
    """Classify each skill as matched (>= 0.60) or missing (< 0.60)."""
    similarities = compute_similarity(cv_text, skills)
    matched: list[str] = []
    missing: list[str] = []
    scores: list[float] = []
    for skill, score in zip(skills, similarities):
        scores.append(float(score))
        if score >= match_threshold:
            matched.append(skill)
        else:
            missing.append(skill)
    return matched, missing, scores
