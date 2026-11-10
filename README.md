# SkillScope: AI Resume Skill Gap Analyzer

## Run
    python -m pip install -r requirements.txt
    python -m streamlit run app.py

## Files
- app.py          Streamlit app (screens, styling, layout)
- extract_resume.py, skill_analyzer.py   Your existing text extraction and skill matching
- ats_score.py    Resume readiness (ATS-style) score out of 100
- jd_parser.py    Extracts skills from a pasted job description
- roadmap.py      Personalised learning roadmap
- ai_features.py  AI resume improvement and mock interview (AI mode or built-in rules)
- .streamlit/config.toml   Dark theme in the Midnight Black + Electric Cobalt palette

## How the app flows
1. Home: upload your resume and pick a role (or paste a job description).
2. Skill Gap (shown first): your alignment score, skills you have and skills to develop.
3. ATS Score: click it to see your score, what to fix and suggested improvements.
4. Learning Roadmap: click it for a step-by-step plan for the missing skills,
   adjusted by study hours per week and your current level.
5. Mock Interview (top bar): choose any role, answer five questions one at a
   time and get feedback and a score on each answer. Works with or without a resume.

The top toolbar is on every screen. ATS Score, Skill Gap and Learning Roadmap
unlock after a resume has been analysed.

## Optional AI mode
Without a key, features 4 and 5 use built-in rules and nothing leaves your computer.
With an Anthropic API key (type it in "AI settings", set the ANTHROPIC_API_KEY
environment variable, or copy .streamlit/secrets.toml.example to secrets.toml),
the resume text and your answers are sent to the Anthropic API.
Set SKILLSCOPE_MODEL to change the model.

## Limits
- Skill matching is keyword based, so it can miss skills outside its lists.
- The ATS score is a rule-based guide, not what real ATS software uses.
- AI suggestions can be wrong. Check every suggested line is true before using it.
