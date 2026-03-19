import sys
import subprocess
import os

REQUIRED_PACKAGES = {
    "pdfplumber": "pdfplumber",
    "sentence_transformers": "sentence-transformers",
    "sklearn": "scikit-learn",
    "numpy": "numpy",
    "tqdm": "tqdm",
}


def check_and_install_dependencies() -> None:
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print("All packages installed successfully.\n")


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        print("Python 3.10 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)


def ensure_project_directories() -> None:
    from utils.file_manager import ensure_directories_exist

    directories = [
        "data/incoming_cv",
        "data/stored_cv",
        "data/output_reports",
        "jd",
        "config",
    ]
    ensure_directories_exist(directories)


def load_recruitment_waves() -> dict:
    import json

    config_path = os.path.join("config", "recruitment_wave.json")
    with open(config_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def display_banner() -> None:
    print("\n" + "=" * 50)
    print("   CV SCREENING SYSTEM")
    print("   Semantic Skill Matching Engine")
    print("=" * 50 + "\n")


def select_recruitment_wave(waves: dict) -> tuple[str, dict]:
    wave_keys = list(waves.keys())
    print("Available Recruitment Waves:\n")
    for idx, key in enumerate(wave_keys, start=1):
        display_name = key.replace("_", " ").title()
        print(f"  [{idx}] {display_name}")
    print()

    while True:
        choice = input("Select recruitment wave (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(wave_keys):
            selected_key = wave_keys[int(choice) - 1]
            return selected_key, waves[selected_key]
        print("Invalid selection. Please try again.\n")


def select_role(wave_data: dict) -> str:
    role_keys = list(wave_data.keys())
    print("\nAvailable Roles:\n")
    for idx, key in enumerate(role_keys, start=1):
        display_name = key.replace("_", " ").title()
        positions = wave_data[key]
        print(f"  [{idx}] {display_name} ({positions} positions)")
    print()

    while True:
        choice = input("Select role (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(role_keys):
            return role_keys[int(choice) - 1]
        print("Invalid selection. Please try again.\n")


def get_cv_path() -> str:
    while True:
        cv_path = input("\nEnter path to CV (PDF file): ").strip().strip('"').strip("'")
        if os.path.isfile(cv_path) and cv_path.lower().endswith(".pdf"):
            return cv_path
        print("File not found or not a PDF. Please try again.")


def run_analysis(cv_path: str, applied_role_key: str, wave_data: dict) -> None:
    from tqdm import tqdm
    from modules.pdf_reader.pdf_parser import extract_text_from_pdf
    from modules.jd_processing.jd_loader import load_all_job_descriptions
    from modules.jd_processing.skill_extractor import extract_skills, get_role_name
    from modules.matching.semantic_matcher import find_matching_skills, compute_similarity
    from modules.matching.scoring import calculate_match_percentage, get_match_status
    from modules.recommendation.recommender import recommend_best_role
    from utils.file_manager import copy_file, get_candidate_name_from_path
    from utils.report_writer import write_report
    from config.settings import CV_STORAGE, REPORT_FOLDER

    steps = [
        "Copying CV to storage",
        "Reading PDF content",
        "Loading job descriptions",
        "Computing semantic similarity",
        "Evaluating other roles",
        "Generating report",
    ]

    progress = tqdm(total=len(steps), desc="Processing", unit="step")

    progress.set_description("Copying CV to storage")
    copy_file(cv_path, CV_STORAGE)
    progress.update(1)

    progress.set_description("Reading PDF content")
    cv_text = extract_text_from_pdf(cv_path)
    if not cv_text.strip():
        print("\nWarning: No text could be extracted from the PDF.")
        print("The file may be image-based or empty.\n")
        progress.close()
        return
    progress.update(1)

    progress.set_description("Loading job descriptions")
    all_jds = load_all_job_descriptions("jd")
    applied_jd = all_jds.get(applied_role_key)
    if applied_jd is None:
        print(f"\nError: Job description for '{applied_role_key}' not found.\n")
        progress.close()
        return
    progress.update(1)

    progress.set_description("Computing semantic similarity")
    skills = extract_skills(applied_jd)
    role_name = get_role_name(applied_jd)
    matched, missing, scores = find_matching_skills(cv_text, skills)
    match_score = calculate_match_percentage(scores)
    progress.update(1)

    progress.set_description("Evaluating other roles")
    other_matches = recommend_best_role(cv_text, applied_role_key, match_score, all_jds)
    progress.update(1)

    progress.set_description("Generating report")
    candidate_name = get_candidate_name_from_path(cv_path)

    recommendation = ""
    if other_matches:
        best = other_matches[0]
        recommendation = f"Candidate is stronger for {best['role']} role ({best['score']:.0f}%)"

    open_positions = {}
    for role_key, count in wave_data.items():
        display = role_key.replace("_", " ").title()
        open_positions[display] = count

    report_path = write_report(
        candidate_name=candidate_name,
        applied_role=role_name,
        match_score=match_score,
        matched_skills=matched,
        missing_skills=missing,
        other_role_matches=other_matches,
        recommendation=recommendation,
        open_positions=open_positions,
        report_folder=REPORT_FOLDER,
    )
    progress.update(1)
    progress.close()

    status = get_match_status(match_score)

    print("\n")
    print("=" * 50)
    print("   APPLICANT CV ANALYSIS")
    print("=" * 50)
    print(f"\n  Applied Role: {role_name}")
    print(f"\n  Match Score: {match_score:.0f}%")
    print(f"  Status: {status}")

    print("\n  Skill Scores:")
    for skill, score in zip(skills, scores):
        print(f"    {skill}: {score:.2f}")

    if matched:
        print("\n  Matched Skills:")
        for skill in matched:
            print(f"    - {skill}")

    if missing:
        print("\n  Missing Skills:")
        for skill in missing:
            print(f"    - {skill}")

    if other_matches:
        print("\n  Better Role Match:")
        for entry in other_matches:
            entry_status = get_match_status(entry["score"])
            print(f"    {entry['role']}: {entry['score']:.0f}% ({entry_status.lower()})")

    if recommendation:
        print(f"\n  Recommendation: {recommendation}")

    print("\n  Open Positions:")
    for role_display, count in open_positions.items():
        print(f"    {role_display}: {count} remaining")

    print(f"\n  Report saved: {report_path}")
    print("\n" + "=" * 50 + "\n")


def main() -> None:
    check_python_version()
    check_and_install_dependencies()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ensure_project_directories()
    display_banner()

    waves = load_recruitment_waves()
    wave_name, wave_data = select_recruitment_wave(waves)

    print(f"\nSelected: {wave_name.replace('_', ' ').title()}\n")

    while True:
        applied_role_key = select_role(wave_data)
        cv_path = get_cv_path()
        run_analysis(cv_path, applied_role_key, wave_data)

        again = input("Screen another CV? (y/n): ").strip().lower()
        if again != "y":
            print("\nThank you for using CV Screening System. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
