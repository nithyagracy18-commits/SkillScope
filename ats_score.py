"""Honest, rule-based ATS score.

Every check earns partial credit from real measurements of the resume text,
so scores vary from resume to resume. Typical results: weak resume 25-50,
average 55-70, well written 75-88. 90+ is rare.

Public API (same as before):
    score_resume(text, matched_keywords=None, total_keywords=None) -> dict
    ats_to_text(ats) -> list[str]
"""

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

ACTION_VERBS = {
    "achieved", "analyzed", "analysed", "architected", "automated", "built",
    "collaborated", "configured", "conducted", "created", "customized",
    "debugged", "delivered", "deployed", "designed", "developed", "devised",
    "drove", "engineered", "enhanced", "established", "evaluated", "executed",
    "expanded", "extracted", "facilitated", "generated", "implemented",
    "improved", "increased", "initiated", "integrated", "introduced",
    "launched", "led", "maintained", "managed", "migrated", "mentored",
    "modeled", "modelled", "monitored", "optimized", "optimised",
    "orchestrated", "organized", "organised", "performed", "planned",
    "presented", "processed", "programmed", "reduced", "refactored",
    "researched", "resolved", "restructured", "reviewed", "scaled",
    "secured", "simplified", "solved", "spearheaded", "streamlined",
    "supported", "tested", "trained", "transformed", "troubleshot",
    "upgraded", "utilized", "utilised", "validated", "visualized", "wrote",
    "authored", "coordinated", "cleaned", "compiled", "contributed",
    "crafted", "diagnosed", "documented", "forecasted", "identified",
    "investigated", "leveraged", "owned", "prototyped", "published",
    "revamped", "shipped", "standardized", "summarized", "tuned",
    "boosted", "cut", "saved", "won", "organised", "applied", "assisted",
    "administered", "negotiated", "directed", "supervised", "trained",
}

WEAK_PHRASES = [
    "responsible for", "worked on", "duties included", "helped with",
    "hardworking", "hard working", "team player", "references available",
    "self-motivated", "self motivated", "fast learner", "go-getter",
    "result-oriented", "results-oriented", "passionate about",
    "detail oriented", "detail-oriented", "jack of all trades",
]

SECTION_PATTERNS = {
    "skills": r"(technical\s+|key\s+|core\s+)?skills?|core competencies|"
              r"technologies|tech stack|tools",
    "education": r"education|academics?|academic (background|qualifications?)|"
                 r"qualifications?",
    "experience": r"(work |professional |relevant )?experience|employment|"
                  r"work history|internships?",
    "projects": r"(personal |academic |key )?projects?",
    "summary": r"(professional |career )?(summary|objective|profile)|"
               r"about me",
    "extras": r"certifications?|certificates?|achievements?|awards?|courses",
}

BULLET_RE = re.compile(r"^\s*([\-\u2022\u25cf\u25aa\u25e6\u2023\u2043*\u27a2\u2013>])\s*")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s\-().]{8,}\d)(?!\d)")
LINK_RE = re.compile(r"linkedin\.com|github\.com|gitlab\.com|behance\.net|"
                     r"portfolio|https?://|www\.", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
NUMBER_RE = re.compile(r"\d")
NOT_METRIC_LINE = re.compile(
    r"cgpa|gpa|percentage|grade|semester|class\s*(x|xii|10|12)|"
    r"\b(10th|12th)\b|pin\s*code|phone|mobile|contact|dob|batch",
    re.I,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lines(text):
    return [ln.strip() for ln in text.replace("\r", "\n").split("\n")
            if ln.strip()]


def _strip_bullet(line):
    return BULLET_RE.sub("", line).strip()


def _heading_of(line):
    """Return the section key if the line looks like a section heading."""
    cleaned = re.sub(r"[^A-Za-z& ]", " ", line).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned or len(cleaned.split()) > 5:
        return None
    for key, pattern in SECTION_PATTERNS.items():
        if re.fullmatch(pattern, cleaned):
            return key
    # "Skills: Python, SQL" style: heading word followed by a colon
    head = line.split(":")[0].strip().lower() if ":" in line else ""
    if head and len(head.split()) <= 3:
        head = re.sub(r"[^a-z& ]", "", head).strip()
        for key, pattern in SECTION_PATTERNS.items():
            if re.fullmatch(pattern, head):
                return key
    return None


def _content_lines(lines):
    """Lines that look like achievement statements (bullets or sentences)."""
    out = []
    for ln in lines:
        if _heading_of(ln):
            continue
        body = _strip_bullet(ln)
        words = body.split()
        if len(words) >= 5 and not EMAIL_RE.search(body):
            out.append(body)
    return out


def _check(label, earned, maximum, tip):
    earned = max(0.0, min(float(maximum), float(earned)))
    return {
        "label": label,
        "passed": earned >= 0.7 * maximum,
        "tip": tip,
        "points": round(earned, 1),
        "max": maximum,
    }


# ---------------------------------------------------------------------------
# Main scorer
# ---------------------------------------------------------------------------

def score_resume(text, matched_keywords=None, total_keywords=None):
    text = text or ""
    lines = _lines(text)
    words = re.findall(r"[A-Za-z0-9+#.'/-]+", text)
    word_count = len(words)
    low = text.lower()
    checks = []

    # 1. Contact details (10) ------------------------------------------------
    has_email = bool(EMAIL_RE.search(text))
    phone_hit = any(
        len(re.sub(r"\D", "", m.group(1))) >= 10 for m in PHONE_RE.finditer(text)
    )
    has_link = bool(LINK_RE.search(text))
    earned = 4 * has_email + 3 * phone_hit + 3 * has_link
    missing = [n for n, ok in (("email", has_email), ("phone number", phone_hit),
                               ("LinkedIn/GitHub/portfolio link", has_link))
               if not ok]
    checks.append(_check(
        "Contact details (email, phone, profile link)", earned, 10,
        "Add your " + ", ".join(missing) + " near the top of the resume."
        if missing else "",
    ))

    # 2. Standard sections (15) -----------------------------------------------
    found = {}
    for ln in lines:
        key = _heading_of(ln)
        if key and key not in found:
            found[key] = ln
    exp_pts = 5 if "experience" in found else (3.5 if "projects" in found else 0)
    if "experience" in found and "projects" in found:
        exp_pts = 5
    earned = (4 * ("skills" in found) + 4 * ("education" in found)
              + exp_pts + 2 * ("summary" in found))
    need = []
    if "skills" not in found:
        need.append("Skills")
    if "education" not in found:
        need.append("Education")
    if "experience" not in found:
        need.append("Experience/Internships")
    if "projects" not in found and "experience" not in found:
        need.append("Projects")
    if "summary" not in found:
        need.append("Summary")
    checks.append(_check(
        f"Standard section headings ({len(found)} found)", earned, 15,
        "Use clear headings ATS can recognise. Missing: "
        + ", ".join(need) + "." if need else "",
    ))

    # 3. Length (8) ------------------------------------------------------------
    if word_count < 150:
        ratio = 0.0
    elif word_count < 350:
        ratio = 0.4 + 0.6 * (word_count - 150) / 200
    elif word_count <= 850:
        ratio = 1.0
    elif word_count <= 1200:
        ratio = 0.7
    else:
        ratio = 0.4
    checks.append(_check(
        f"Resume length ({word_count} words)", 8 * ratio, 8,
        "Aim for roughly 350-850 words (1-2 pages). "
        + ("Yours is too short; add projects, tools and results."
           if word_count < 350 else "Yours is long; trim older or minor items."),
    ))

    # 4. Action verbs (10) ------------------------------------------------------
    content = _content_lines(lines)
    verb_starts = [c.split()[0].lower().strip(",.;:") for c in content
                   if c.split()[0].lower().strip(",.;:") in ACTION_VERBS]
    earned = 10 * min(1.0, len(verb_starts) / 10)
    checks.append(_check(
        f"Strong action verbs ({len(verb_starts)} bullets start with one)",
        earned, 10,
        "Start bullets with verbs like Built, Designed, Automated, Reduced. "
        "Aim for at least 10.",
    ))

    # 5. Measurable results (14) -----------------------------------------------
    metric_lines = 0
    for c in content:
        if NOT_METRIC_LINE.search(c):
            continue
        scrubbed = EMAIL_RE.sub("", YEAR_RE.sub("", c))
        scrubbed = PHONE_RE.sub("", scrubbed)
        if re.search(r"\d+(?:[.,]\d+)?\s*(%|\+|x\b|k\b|m\b|lakh|crore|users|"
                     r"customers|records|rows|hours|days|ms|seconds)", scrubbed,
                     re.I) or re.search(r"[$\u20b9\u00a3\u20ac]\s?\d", scrubbed):
            metric_lines += 1
        elif len(NUMBER_RE.findall(scrubbed)) >= 1 and verb_starts:
            metric_lines += 0.25
    earned = 14 * min(1.0, metric_lines / 4)
    checks.append(_check(
        f"Measurable results (about {int(metric_lines)} bullets with numbers)",
        earned, 14,
        "Add numbers: \"Reduced report time by 40%\", \"Handled 10k+ records\". "
        "Aim for at least 4 such bullets.",
    ))

    # 6. Bullet structure (6) ---------------------------------------------------
    bullet_count = sum(1 for ln in lines if BULLET_RE.match(ln))
    structured = max(bullet_count, len(content) // 2)
    checks.append(_check(
        f"Bullet-point structure ({bullet_count} bullets)",
        6 * min(1.0, structured / 8), 6,
        "Describe each role or project in short bullet points, not paragraphs.",
    ))

    # 7. Keyword match for the target role (15) ---------------------------------
    if total_keywords:
        ratio_kw = (matched_keywords or 0) / total_keywords
        earned = 15 * min(1.0, ratio_kw / 0.85)
        checks.append(_check(
            f"Target-role keyword match ({matched_keywords} of "
            f"{total_keywords} skills)", earned, 15,
            "Add the missing role skills you genuinely have, in your Skills "
            "section and inside project/experience bullets.",
        ))

    # 8. Dates (5) --------------------------------------------------------------
    years = YEAR_RE.findall(text)
    n_years = len(re.findall(r"\b(?:19|20)\d{2}\b", text))
    earned = 5 * (1.0 if n_years >= 3 else 0.5 if n_years >= 1 else 0.0)
    checks.append(_check(
        f"Dates on education and experience ({n_years} years found)", earned, 5,
        "Add start and end dates (e.g. 2022 - 2025) to education, internships "
        "and projects.",
    ))

    # 9. Formatting risks (5) ---------------------------------------------------
    penalty = 0.0
    if text.count("|") >= 8:
        penalty += 2          # table or column layout
    garbled = len(re.findall(r"[\ufffd\ue000-\uf8ff\u25a0-\u25ff]", text))
    if word_count and garbled / max(len(text), 1) > 0.01:
        penalty += 2          # icons / broken glyphs
    caps = sum(1 for ln in lines if len(ln) > 8 and ln.isupper())
    if lines and caps / len(lines) > 0.25:
        penalty += 1
    wide = sum(1 for ln in lines if re.search(r"\S {5,}\S|\t", ln))
    if lines and wide / len(lines) > 0.2:
        penalty += 1.5        # multi-column text that reads out of order
    checks.append(_check(
        "ATS-friendly formatting", 5 - penalty, 5,
        "Avoid tables, columns, icons and all-caps lines. Use a simple "
        "single-column layout.",
    ))

    # 10. Cliches and first person (6) -----------------------------------------
    used = [p for p in WEAK_PHRASES if p in low]
    first_person = len(re.findall(r"\b(i|my|me)\b", low))
    penalty = 1.5 * len(used) + 0.5 * max(0, first_person - 2)
    tip = "Remove weak or cliche wording"
    if used:
        tip += " (" + ", ".join(f'"{p}"' for p in used[:4]) + ")"
    tip += ". Avoid \"I\" and \"my\"; write in short, direct statements."
    checks.append(_check("Clear, confident wording", 6 - penalty, 6, tip))

    # 11. Bullet length (3) -----------------------------------------------------
    if len(content) >= 3:
        avg = sum(len(c.split()) for c in content) / len(content)
        if 8 <= avg <= 28:
            ratio = 1.0
        elif avg < 8:
            ratio = max(0.0, avg / 8)
        else:
            ratio = max(0.0, 1 - (avg - 28) / 20)
        label = f"Bullet length (average {avg:.0f} words)"
    else:
        ratio, label = 0.0, "Bullet length (not enough bullets to judge)"
    checks.append(_check(
        label, 3 * ratio, 3,
        "Keep bullets to one or two lines, about 10-25 words each.",
    ))

    # 12. Variety of verbs (3) --------------------------------------------------
    if len(verb_starts) >= 3:
        top = Counter(verb_starts).most_common(1)[0]
        ratio = 1.0 if top[1] <= 2 or top[1] / len(verb_starts) <= 0.3 else 0.4
        label = "Variety of action verbs"
        tip = f"You start many bullets with \"{top[0]}\". Vary your verbs."
    else:
        ratio, label = 0.0, "Variety of action verbs"
        tip = "Use at least 3 different action verbs to open your bullets."
    checks.append(_check(label, 3 * ratio, 3, tip))

    # Total ---------------------------------------------------------------------
    earned_total = sum(c["points"] for c in checks)
    max_total = sum(c["max"] for c in checks)
    score = round(100 * earned_total / max_total) if max_total else 0

    # Almost no readable text usually means a scanned/image resume.
    if word_count < 120:
        score = min(score, 30)
        checks.insert(0, {
            "label": "Readable text found",
            "passed": False,
            "tip": "Very little text could be read. Scanned or image-based "
                   "resumes are unreadable to most ATS. Export a text PDF or "
                   "DOCX instead.",
            "points": 0, "max": 0,
        })

    return {"score": int(max(0, min(100, score))), "checks": checks}


def ats_to_text(ats):
    lines = [f"ATS score: {ats['score']} / 100"]
    for check in sorted(ats["checks"], key=lambda c: c["passed"]):
        tag = "OK " if check["passed"] else "FIX"
        row = f"- [{tag}] {check['label']}"
        if not check["passed"] and check.get("tip"):
            row += f" -> {check['tip']}"
        lines.append(row)
    return lines
