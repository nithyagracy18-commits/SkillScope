"""Rule-based resume readiness (ATS-style) score for SkillScope.

This checks common resume structure and writing signals. It is a guide,
not the scoring system of any real applicant tracking software.
"""

import re

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){10,12}")
LINK_PATTERN = re.compile(r"linkedin\.com|github\.com|portfolio", re.I)

SECTION_PATTERNS = {
    "Education": r"\beducation\b|\bacademic\b|\bqualification",
    "Skills": r"\bskills?\b|\btechnologies\b|\btech stack\b",
    "Projects": r"\bprojects?\b",
    "Experience or internship": (
        r"\bexperience\b|\binternship\b|\bwork history\b|\btraining\b"
    ),
    "Summary or objective": r"\bsummary\b|\bobjective\b|\bprofile\b|\babout me\b",
}

SECTION_POINTS = {
    "Education": 8,
    "Skills": 8,
    "Projects": 8,
    "Experience or internship": 8,
    "Summary or objective": 4,
}

ACTION_VERBS = {
    "built", "developed", "designed", "created", "implemented",
    "analyzed", "analysed", "improved", "optimized", "optimised",
    "led", "managed", "automated", "deployed", "launched", "reduced",
    "increased", "trained", "tested", "integrated", "collaborated",
    "achieved", "delivered", "engineered", "organized", "organised",
    "researched", "presented", "streamlined", "migrated",
}

BULLET_PATTERN = re.compile(r"^\s*[-•●▪*◦►➢]\s+", re.M)
NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s?(?:%|\+|k\b|x\b)|\b\d{2,}\b")


def _check(label, points, maximum, tip):
    return {
        "label": label,
        "points": points,
        "max": maximum,
        "passed": points >= maximum,
        "tip": tip,
    }


def score_resume(resume_text):
    """Return {"score": int, "checks": [...]} for the given resume text."""
    text = resume_text or ""
    lowered = text.casefold()
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", text)
    word_count = len(words)

    checks = []

    # Contact details (20)
    checks.append(_check(
        "Email address", 10 if EMAIL_PATTERN.search(text) else 0, 10,
        "Add a professional email address at the top.",
    ))
    checks.append(_check(
        "Phone number", 5 if PHONE_PATTERN.search(text) else 0, 5,
        "Add a phone number recruiters can call.",
    ))
    checks.append(_check(
        "LinkedIn, GitHub or portfolio link",
        5 if LINK_PATTERN.search(text) else 0, 5,
        "Add a LinkedIn or GitHub link so recruiters can see your work.",
    ))

    # Sections (36)
    for label, pattern in SECTION_PATTERNS.items():
        maximum = SECTION_POINTS[label]
        found = re.search(pattern, lowered) is not None
        checks.append(_check(
            f"{label} section", maximum if found else 0, maximum,
            f"Add a clearly labelled {label.lower()} section.",
        ))

    # Length (12)
    if 250 <= word_count <= 900:
        length_points = 12
    elif 150 <= word_count < 250 or 900 < word_count <= 1200:
        length_points = 6
    else:
        length_points = 0
    checks.append(_check(
        f"Length ({word_count} words)", length_points, 12,
        "Aim for roughly 250-900 words, about one to two pages.",
    ))

    # Action verbs (12)
    used_verbs = {
        word.casefold() for word in words
        if word.casefold() in ACTION_VERBS
    }
    if len(used_verbs) >= 5:
        verb_points = 12
    elif len(used_verbs) >= 3:
        verb_points = 8
    elif used_verbs:
        verb_points = 4
    else:
        verb_points = 0
    checks.append(_check(
        f"Action verbs ({len(used_verbs)} found)", verb_points, 12,
        "Start bullets with verbs such as built, automated or improved.",
    ))

    # Quantified achievements (12)
    number_hits = len(NUMBER_PATTERN.findall(text))
    if number_hits >= 3:
        number_points = 12
    elif number_hits >= 1:
        number_points = 6
    else:
        number_points = 0
    checks.append(_check(
        "Quantified results", number_points, 12,
        "Add numbers, such as users, accuracy, time saved or dataset size.",
    ))

    # Bullet points (8)
    bullet_hits = len(BULLET_PATTERN.findall(text))
    if bullet_hits >= 5:
        bullet_points = 8
    elif bullet_hits >= 2:
        bullet_points = 4
    else:
        bullet_points = 0
    checks.append(_check(
        "Bullet-point formatting", bullet_points, 8,
        "Use short bullet points. Some PDFs lose bullets when text is "
        "extracted, so this check can be too strict.",
    ))

    score = sum(check["points"] for check in checks)

    return {"score": int(score), "checks": checks}


def ats_to_text(ats):
    """Plain-text version for the downloadable report."""
    lines = [f"Readiness score: {ats['score']}/100"]
    for check in ats["checks"]:
        status = "OK " if check["passed"] else "FIX"
        lines.append(f"- [{status}] {check['label']}")
        if not check["passed"]:
            lines.append(f"    Tip: {check['tip']}")
    return lines
