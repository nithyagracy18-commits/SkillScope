
"""Compare resume skills with the skills required for a target job."""

import re


# Skills the analyzer can recognize in a resume or job description.
SKILL_KEYWORDS = {
    "Python": ["python"],
    "Java": ["java"],
    "C": ["programming in c", "c language"],
    "SQL": ["sql"],
    "Excel": ["excel", "microsoft excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn"],
    "Data Analysis": ["data analysis", "data analytics", "data analyst"],
    "Statistics": ["statistics", "statistical analysis"],
    "Data Visualization": ["data visualization", "data visualisation"],
    "HTML": ["html"],
    "CSS": ["css"],
    "JavaScript": ["javascript"],
    "React": ["react", "react.js"],
    "TypeScript": ["typescript"],
    "MySQL": ["mysql"],
    "SQLite": ["sqlite"],
    "Firebase": ["firebase"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Data Structures and Algorithms": [
        "data structures and algorithms",
        "dsa",
    ],
    "Object-Oriented Programming": [
        "object-oriented programming",
        "oop",
    ],
    "DBMS": ["dbms", "database management system"],
    "Deep Learning": ["deep learning"],
    "NLP": ["natural language processing", "nlp"],
    "AWS": ["amazon web services", "aws"],
    "Docker": ["docker"],
    "PowerPoint": ["powerpoint", "power point"],
}


ROLE_SKILLS = {
    "Data Analyst": [
        "SQL", "Excel", "Python", "Pandas", "NumPy",
        "Power BI", "Statistics", "Data Visualization",
    ],
    "Software Developer": [
        "Java", "Python", "SQL", "Git",
        "Data Structures and Algorithms",
        "Object-Oriented Programming", "DBMS",
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "React",
        "TypeScript", "Git",
    ],
    "Machine Learning Intern": [
        "Python", "Pandas", "NumPy", "Machine Learning",
        "Statistics", "SQL",
    ],
}


def contains_keyword(text: str, keyword: str) -> bool:
    """Match whole words where possible to reduce accidental matches."""
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def find_skills(text: str) -> list[str]:
    """Return recognized skills found in a block of text."""
    found = []

    for skill, keywords in SKILL_KEYWORDS.items():
        if any(contains_keyword(text, keyword) for keyword in keywords):
            found.append(skill)

    return found


def analyze_resume(
    resume_text: str,
    required_skills: list[str],
) -> dict:
    """Compare recognized resume skills with a target skill list."""
    resume_skills = find_skills(resume_text)

    matched = [
        skill for skill in required_skills
        if skill in resume_skills
    ]
    missing = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    total = len(required_skills)
    match_percentage = round(len(matched) / total * 100, 1) if total else 0

    return {
        "resume_skills": resume_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage,
    }


def get_suggestions(missing_skills: list[str]) -> list[str]:
    """Generate basic next-step suggestions for missing skills."""
    suggestions = []

    for skill in missing_skills:
        suggestions.append(
            f"Learn {skill} and build a small project demonstrating it."
        )

    if not suggestions:
        suggestions.append(
            "Your resume covers all listed skills. Practise interviews "
            "and strengthen your project evidence."
        )

    return suggestions
