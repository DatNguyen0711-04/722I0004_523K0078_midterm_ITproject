import os
from datetime import datetime
from pathlib import Path


def write_report(
    candidate_name: str,
    applied_role: str,
    match_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    other_role_matches: list[dict],
    recommendation: str,
    open_positions: dict,
    report_folder: str,
) -> str:
    Path(report_folder).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = candidate_name.replace(" ", "_").lower()
    filename = f"result_{safe_name}_{date_str}.txt"
    filepath = os.path.join(report_folder, filename)

    lines = []
    lines.append("=" * 50)
    lines.append("APPLICANT CV ANALYSIS REPORT")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Candidate: {candidate_name}")
    lines.append(f"Applied Role: {applied_role}")
    lines.append(f"Match Score: {match_score:.0f}%")

    if match_score >= 80:
        lines.append("Status: STRONG MATCH")
    elif match_score >= 65:
        lines.append("Status: GOOD MATCH")
    elif match_score >= 50:
        lines.append("Status: POSSIBLE MATCH")
    else:
        lines.append("Status: WEAK MATCH")
    lines.append("")

    if matched_skills:
        lines.append("Matched Skills:")
        for skill in matched_skills:
            lines.append(f"  - {skill}")
        lines.append("")

    if missing_skills:
        lines.append("Missing Skills:")
        for skill in missing_skills:
            lines.append(f"  - {skill}")
        lines.append("")

    if other_role_matches:
        lines.append("Better Role Matches:")
        for entry in other_role_matches:
            if entry["score"] >= 80:
                label = "strong match"
            elif entry["score"] >= 65:
                label = "good match"
            elif entry["score"] >= 50:
                label = "possible match"
            else:
                label = "weak match"
            lines.append(f"  {entry['role']}: {entry['score']:.0f}% ({label})")
        lines.append("")

    if recommendation:
        lines.append(f"Recommendation: {recommendation}")
        lines.append("")

    if open_positions:
        lines.append("Open Positions:")
        for role, count in open_positions.items():
            lines.append(f"  {role}: {count} remaining")

    lines.append("")
    lines.append("=" * 50)
    lines.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
