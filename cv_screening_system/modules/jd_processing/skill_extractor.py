def extract_skills(jd_data: dict) -> list[str]:
    return jd_data.get("skills", [])


def get_role_name(jd_data: dict) -> str:
    return jd_data.get("role", "Unknown")
