
from pathlib import Path

from extract_resume import extract_resume
from skill_analyzer import analyze_resume, ROLE_SKILLS, get_suggestions


# Uses the extracted text file created by your working extractor.
resume_file = Path("extracted.txt")

if not resume_file.exists():
    raise FileNotFoundError(
        "extracted.txt not found. Run your resume extraction command first."
    )

resume_text = resume_file.read_text(encoding="utf-8")

role = "Data Analyst"
required_skills = ROLE_SKILLS[role]

result = analyze_resume(resume_text, required_skills)

print(f"\nTARGET ROLE: {role}")
print(f"SKILL MATCH: {result['match_percentage']}%")

print("\nSKILLS FOUND IN YOUR RESUME:")
print(", ".join(result["resume_skills"]) or "None detected")

print("\nMATCHED SKILLS:")
print(", ".join(result["matched_skills"]) or "None")

print("\nMISSING SKILLS:")
print(", ".join(result["missing_skills"]) or "None")

print("\nSUGGESTIONS:")
for suggestion in get_suggestions(result["missing_skills"]):
    print(f"- {suggestion}")
