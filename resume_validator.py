
import re

RESUME_KEYWORDS = [
    "education",
    "work experience",
    "professional experience",
    "skills",
    "technical skills",
    "projects",
    "certifications",
    "internship",
    "career objective",
    "professional summary",
    "employment history",
    "academic qualifications"
]

NON_RESUME_KEYWORDS = [
    "question paper",
    "examination",
    "semester examination",
    "total marks",
    "maximum marks",
    "multiple choice questions",
    "section a",
    "section b",
    "answer all questions",
    "question bank"
]


def validate_resume(text):
    if not text or len(text.strip()) < 100:
        return False, "Unable to extract sufficient text. Please upload a readable resume."

    content = re.sub(r"\s+", " ", text.lower())

    resume_score = sum(
        1 for keyword in RESUME_KEYWORDS
        if keyword in content
    )

    non_resume_score = sum(
        1 for keyword in NON_RESUME_KEYWORDS
        if keyword in content
    )

    if non_resume_score >= 2 and resume_score < 3:
        return False, "This document appears to be a question paper or academic document, not a resume."

    if resume_score < 3:
        return False, "This document does not appear to be a valid resume. Please upload your resume."

    return True, "Resume validated successfully."
