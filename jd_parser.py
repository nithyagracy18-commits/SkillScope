"""Extract skills from a pasted job description for SkillScope.

The parser looks for known skills (your role catalog plus a few extras)
and common alternative spellings. It does not understand context, so it
can miss skills that are not in the list. It is a keyword extractor, not
a language model.
"""

import re

# Skills that are not in the role catalog but appear often in job posts.
EXTRA_SKILLS = [
    "MongoDB", "NoSQL", "FastAPI", "Matplotlib", "Seaborn", "Jupyter",
    "GitHub", "Postman", "Microservices", "GraphQL", "Redux", "Next.js",
    "Vue", "Angular", "Bash", "Hugging Face", "Keras", "XGBoost",
    "Looker", "Snowflake", "BigQuery", "Databricks", "dbt", "Redis",
    "Teamwork", "Leadership", "Time Management", "Presentation Skills",
]

# Alternative spellings: alias -> canonical skill name.
ALIASES = {
    "powerbi": "Power BI",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "llm": "LLMs",
    "large language models": "LLMs",
    "natural language processing": "NLP",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "reactjs": "React",
    "react.js": "React",
    "js": "JavaScript",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "restful": "REST API",
    "rest apis": "REST API",
    "restful apis": "REST API",
    "object oriented": "OOP",
    "object-oriented programming": "Object-Oriented Programming",
    "dsa": "Data Structures and Algorithms",
    "data structures": "Data Structures and Algorithms",
    "k8s": "Kubernetes",
    "postgres": "PostgreSQL",
    "data visualisation": "Data Visualization",
    "communication skills": "Communication",
    "problem solving skills": "Problem Solving",
    "c programming": "C",
    "r programming": "R",
}

# Single letters are too ambiguous to match on their own.
SKIP_ALONE = {"c", "r"}

MAX_SKILLS = 20


def _term_pattern(term):
    """Regex for one term: whole-word, case-insensitive, flexible spaces."""
    parts = [re.escape(part) for part in re.split(r"[\s-]+", term.strip())]
    body = r"[\s\-]+".join(parts)
    return re.compile(
        r"(?<![A-Za-z0-9+#])" + body + r"(?![A-Za-z0-9+#])",
        re.IGNORECASE,
    )


def extract_jd_skills(jd_text, vocabulary):
    """Return skills found in the job description, most mentioned first."""
    text = jd_text or ""

    if not text.strip():
        return []

    canonical = {}
    for skill in list(vocabulary) + EXTRA_SKILLS:
        canonical.setdefault(skill.casefold(), skill)

    terms = {}
    for skill in canonical.values():
        if skill.casefold() not in SKIP_ALONE:
            terms[skill] = skill

    for alias, target in ALIASES.items():
        target_skill = canonical.get(target.casefold())
        if target_skill:
            terms[alias] = target_skill

    counts = {}
    first_position = {}

    for term, skill in terms.items():
        for match in _term_pattern(term).finditer(text):
            counts[skill] = counts.get(skill, 0) + 1
            first_position[skill] = min(
                first_position.get(skill, match.start()), match.start()
            )

    ranked = sorted(
        counts,
        key=lambda skill: (-counts[skill], first_position[skill]),
    )

    return ranked[:MAX_SKILLS]
