import json
import os


def load_job_description(jd_path: str) -> dict:
    with open(jd_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_all_job_descriptions(jd_folder: str) -> dict[str, dict]:
    jd_map = {}
    for filename in os.listdir(jd_folder):
        if filename.endswith(".json"):
            key = os.path.splitext(filename)[0]
            filepath = os.path.join(jd_folder, filename)
            jd_map[key] = load_job_description(filepath)
    return jd_map