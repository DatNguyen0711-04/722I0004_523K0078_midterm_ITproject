from modules.matching.semantic_matcher import compute_similarity
from modules.matching.scoring import calculate_match_percentage
from modules.jd_processing.skill_extractor import extract_skills, get_role_name


def recommend_best_role(
    cv_text: str,
    applied_role_key: str,
    applied_score: float,
    all_jds: dict[str, dict],
) -> list[dict]:
    other_matches = []
    for role_key, jd_data in all_jds.items():
        if role_key == applied_role_key:
            continue
        skills = extract_skills(jd_data)
        role_name = get_role_name(jd_data)
        similarities = compute_similarity(cv_text, skills)
        score = calculate_match_percentage(list(similarities))
        if score > applied_score + 5:
            other_matches.append({
                "key": role_key,
                "role": role_name,
                "score": score,
            })
    other_matches.sort(key=lambda x: x["score"], reverse=True)
    return other_matches
