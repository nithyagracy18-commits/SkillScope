import html
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path
from resume_validator import validate_resume

import streamlit as st

from extract_resume import extract_resume
from skill_analyzer import analyze_resume, get_suggestions
from roadmap import build_roadmap, roadmap_to_text
from jd_parser import extract_jd_skills
from ai_features import (
    ai_available,
    evaluate_answer,
    generate_questions,
    improve_resume,
)
from ats_score import ats_to_text, score_resume


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SkillScope | Career Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# JOB ROLE CATALOG
# These are starter keyword lists, not live job-market data.
# =========================================================

JOB_ROLE_SKILLS = {
    "Data Analyst": [
        "SQL", "Excel", "Python", "Pandas", "NumPy",
        "Power BI", "Tableau", "Statistics", "Data Visualization",
        "Data Cleaning", "Data Analysis",
    ],
    "Business Analyst": [
        "SQL", "Excel", "Power BI", "Tableau", "Requirements Analysis",
        "Business Analysis", "Documentation", "Stakeholder Management",
        "Data Analysis", "Agile",
    ],
    "Business Intelligence Analyst": [
        "SQL", "Power BI", "Tableau", "Excel", "Data Modeling",
        "ETL", "Data Visualization", "DAX", "Data Warehousing",
    ],
    "Data Scientist": [
        "Python", "SQL", "Pandas", "NumPy", "Statistics",
        "Machine Learning", "Scikit-learn", "Data Visualization",
        "Deep Learning", "Feature Engineering",
    ],
    "Machine Learning Engineer": [
        "Python", "Machine Learning", "Deep Learning", "Scikit-learn",
        "TensorFlow", "PyTorch", "SQL", "Model Deployment",
        "Docker", "MLOps",
    ],
    "AI Engineer": [
        "Python", "Machine Learning", "Deep Learning", "LLMs",
        "NLP", "APIs", "PyTorch", "TensorFlow",
        "Prompt Engineering", "Model Deployment",
    ],
    "Generative AI Engineer": [
        "Python", "LLMs", "Prompt Engineering", "RAG",
        "Vector Databases", "Embeddings", "APIs",
        "LangChain", "Machine Learning",
    ],
    "Data Engineer": [
        "Python", "SQL", "ETL", "Data Warehousing", "Apache Spark",
        "Airflow", "Hadoop", "Cloud Computing", "Data Pipelines",
        "Data Modeling",
    ],
    "Big Data Engineer": [
        "Python", "SQL", "Apache Spark", "Hadoop", "PySpark",
        "Kafka", "ETL", "Data Pipelines", "Linux",
    ],
    "Database Administrator": [
        "SQL", "MySQL", "PostgreSQL", "Database Design",
        "Database Security", "Backup and Recovery",
        "Performance Tuning", "Linux",
    ],
    "SQL Developer": [
        "SQL", "MySQL", "PostgreSQL", "Stored Procedures",
        "Database Design", "Query Optimization", "DBMS",
    ],
    "Software Developer": [
        "Java", "Python", "C++", "Data Structures and Algorithms",
        "Object-Oriented Programming", "SQL", "Git",
        "Problem Solving", "REST API",
    ],
    "Java Developer": [
        "Java", "OOP", "Collections", "Exception Handling",
        "Spring Boot", "SQL", "REST API", "Git", "Maven",
    ],
    "Python Developer": [
        "Python", "OOP", "SQL", "REST API", "Git",
        "Flask", "Django", "Testing", "Data Structures and Algorithms",
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "React", "TypeScript",
        "Responsive Design", "Git", "REST API",
    ],
    "Backend Developer": [
        "Python", "Java", "Node.js", "SQL", "REST API",
        "Authentication", "Git", "Docker", "Testing",
    ],
    "Full Stack Developer": [
        "HTML", "CSS", "JavaScript", "React", "Node.js",
        "SQL", "REST API", "Git", "Authentication", "Deployment",
    ],
    "Mobile App Developer": [
        "Java", "Kotlin", "Android", "Flutter", "Dart",
        "REST API", "Firebase", "Git",
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "Responsive Design",
        "React", "REST API", "Git", "Web Development",
    ],
    "Software Test Engineer": [
        "Software Testing", "Test Cases", "Manual Testing",
        "Automation Testing", "Selenium", "SQL", "Jira",
        "Bug Tracking", "API Testing",
    ],
    "QA Automation Engineer": [
        "Python", "Java", "Selenium", "Automation Testing",
        "API Testing", "JUnit", "Git", "CI/CD",
    ],
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS", "Git",
        "CI/CD", "Jenkins", "Terraform", "Monitoring",
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "Google Cloud", "Linux", "Networking",
        "Docker", "IAM", "Cloud Security", "Terraform",
    ],
    "AWS Cloud Engineer": [
        "AWS", "EC2", "S3", "IAM", "Lambda",
        "VPC", "CloudWatch", "Docker", "Linux",
    ],
    "Cybersecurity Analyst": [
        "Networking", "Linux", "Cybersecurity", "SIEM",
        "Incident Response", "Vulnerability Assessment",
        "Security Monitoring", "Python",
    ],
    "Network Engineer": [
        "Networking", "TCP/IP", "DNS", "DHCP", "Routing",
        "Switching", "VLAN", "Firewalls", "Troubleshooting",
    ],
    "System Administrator": [
        "Linux", "Windows Server", "Networking", "Shell Scripting",
        "System Monitoring", "Backup and Recovery", "Security",
    ],
    "UI Designer": [
        "UI Design", "Figma", "Typography", "Color Theory",
        "Wireframing", "Prototyping", "Design Systems",
    ],
    "UX Designer": [
        "UX Research", "Figma", "Wireframing", "Prototyping",
        "Usability Testing", "User Research", "Information Architecture",
    ],
    "UI/UX Designer": [
        "Figma", "UI Design", "UX Research", "Wireframing",
        "Prototyping", "Usability Testing", "Design Systems",
    ],
    "Product Designer": [
        "Figma", "UI Design", "UX Research", "Prototyping",
        "Design Systems", "Product Thinking", "Usability Testing",
    ],
    "Product Manager": [
        "Product Management", "Roadmapping", "Agile",
        "Stakeholder Management", "Data Analysis",
        "Communication", "Product Strategy", "Jira",
    ],
    "Project Manager": [
        "Project Management", "Planning", "Agile", "Scrum",
        "Risk Management", "Communication", "Jira",
        "Stakeholder Management",
    ],
    "Digital Marketing Executive": [
        "SEO", "SEM", "Google Analytics", "Social Media Marketing",
        "Content Marketing", "Email Marketing", "Campaign Management",
    ],
    "SEO Specialist": [
        "SEO", "Keyword Research", "Google Analytics",
        "Google Search Console", "Content Optimization",
        "Technical SEO", "Link Building",
    ],
    "Social Media Manager": [
        "Social Media Marketing", "Content Strategy",
        "Content Creation", "Analytics", "Copywriting",
        "Campaign Management", "Community Management",
    ],
    "Content Writer": [
        "Content Writing", "Copywriting", "SEO",
        "Research", "Editing", "Communication",
    ],
    "Graphic Designer": [
        "Graphic Design", "Adobe Photoshop", "Adobe Illustrator",
        "Typography", "Color Theory", "Branding", "Canva",
    ],
    "Financial Analyst": [
        "Excel", "Financial Modeling", "Financial Analysis",
        "Accounting", "Forecasting", "Power BI",
        "Data Analysis", "Financial Reporting",
    ],
    "HR Analyst": [
        "Excel", "Data Analysis", "HR Analytics",
        "Reporting", "Communication", "Power BI",
        "Recruitment", "Statistics",
    ],
    "Operations Analyst": [
        "Excel", "SQL", "Data Analysis", "Process Improvement",
        "Reporting", "Power BI", "Problem Solving",
    ],
    "Research Analyst": [
        "Research", "Data Analysis", "Excel", "Statistics",
        "Report Writing", "Python", "Critical Thinking",
    ],
    "Prompt Engineer": [
        "Prompt Engineering", "LLMs", "Generative AI",
        "Python", "APIs", "Evaluation", "Critical Thinking",
    ],
    "Blockchain Developer": [
        "Blockchain", "Solidity", "Smart Contracts",
        "JavaScript", "Web3", "Cryptography", "Git",
    ],
    "Embedded Systems Engineer": [
        "C", "C++", "Microcontrollers", "Embedded Systems",
        "RTOS", "Electronics", "Debugging",
    ],
    "IoT Developer": [
        "Python", "C", "IoT", "Microcontrollers",
        "MQTT", "Networking", "Embedded Systems",
    ],
    "Game Developer": [
        "C++", "C#", "Unity", "Unreal Engine",
        "Game Development", "3D Mathematics", "Git",
    ],
    "Technical Support Engineer": [
        "Troubleshooting", "Networking", "Operating Systems",
        "SQL", "Communication", "Ticketing Systems",
        "Problem Solving",
    ],
    "Technical Writer": [
        "Technical Writing", "Documentation", "Research",
        "Communication", "Markdown", "API Documentation",
    ],
    "Research and Development Engineer": [
        "Research", "Python", "Problem Solving", "Prototyping",
        "Data Analysis", "Experimentation", "Documentation",
    ],
    "Computer Vision Engineer": [
        "Python", "OpenCV", "Computer Vision", "Deep Learning",
        "PyTorch", "Image Processing", "Machine Learning",
    ],
    "NLP Engineer": [
        "Python", "NLP", "Machine Learning", "Deep Learning",
        "Transformers", "LLMs", "Text Processing",
    ],
    "Statistician": [
        "Statistics", "Probability", "R", "Python",
        "Hypothesis Testing", "Regression Analysis", "Data Analysis",
    ],
    "Excel Specialist": [
        "Excel", "Pivot Tables", "VLOOKUP", "XLOOKUP",
        "Power Query", "Data Cleaning", "Reporting",
    ],
    "Power BI Developer": [
        "Power BI", "DAX", "Power Query", "Data Modeling",
        "SQL", "Data Visualization", "ETL",
    ],
    "Tableau Developer": [
        "Tableau", "SQL", "Data Visualization",
        "Dashboards", "Data Analysis", "Data Modeling",
    ],
    "Customer Success Analyst": [
        "Excel", "Data Analysis", "Communication",
        "Customer Relationship Management", "Reporting",
        "Problem Solving",
    ],
    "Business Development Executive": [
        "Communication", "Sales", "Market Research",
        "Lead Generation", "Negotiation",
        "Customer Relationship Management",
    ],
    "Sales Analyst": [
        "Excel", "SQL", "Sales Analytics", "Forecasting",
        "Power BI", "Reporting", "Data Visualization",
    ],
    "Accountant": [
        "Accounting", "Excel", "Financial Reporting",
        "Bookkeeping", "Taxation", "Attention to Detail",
    ],
    "Supply Chain Analyst": [
        "Excel", "SQL", "Supply Chain Management",
        "Forecasting", "Data Analysis", "Power BI",
    ],
    "Research Intern": [
        "Research", "Python", "Data Analysis",
        "Documentation", "Statistics", "Problem Solving",
    ],
    "Data Analyst Intern": [
        "SQL", "Excel", "Python", "Pandas",
        "Data Cleaning", "Data Visualization",
    ],
    "Software Engineer Intern": [
        "Java", "Python", "Data Structures and Algorithms",
        "OOP", "SQL", "Git", "Problem Solving",
    ],
    "AI/ML Intern": [
        "Python", "Machine Learning", "Pandas",
        "NumPy", "Scikit-learn", "Statistics",
    ],
    "Cloud Intern": [
        "AWS", "Linux", "Networking", "Cloud Computing",
        "Git", "Docker",
    ],
    "Cybersecurity Intern": [
        "Networking", "Linux", "Cybersecurity",
        "Python", "Security Fundamentals",
    ],
}

ALL_ROLES = sorted(JOB_ROLE_SKILLS.keys(), key=str.lower)

# Roadmap personalisation: scales the starter hour estimates.
LEVEL_FACTORS = {
    "Beginner: new to these skills": 1.0,
    "Some exposure: I know the basics": 0.7,
    "Comfortable: I mainly need practice": 0.5,
}
LEVEL_OPTIONS = list(LEVEL_FACTORS)

# Every skill in the catalog, used to find skills in a pasted job description.
SKILL_VOCABULARY = sorted(
    {skill for skills in JOB_ROLE_SKILLS.values() for skill in skills},
    key=str.casefold,
)


# =========================================================
# CUSTOM CSS
# Palette: Midnight Black #030407 + Electric Cobalt Blue #1558C9
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,700;1,500;1,700&display=swap');

    :root {
        --bg: #030407;
        --surface: #0B101A;
        --surface2: #0E131D;
        --blue: #1558C9;
        --blue-bright: #2878EE;
        --blue-light: #65A0FF;
        --white: #F3F6FF;
        --muted: #A3AEC5;
        --track: #2B3140;
        --line: rgba(101, 160, 255, 0.22);
        --serif: 'Playfair Display', Georgia, serif;
        --fs: 1.12;
    }

    /* Font scale follows the screen size: bigger text on bigger laptops */
    @media (min-width: 1280px) { :root { --fs: 1.22; } }
    @media (min-width: 1536px) { :root { --fs: 1.34; } }
    @media (min-width: 1920px) { :root { --fs: 1.48; } }
    @media (max-width: 700px)  { :root { --fs: 1.05; } }

    /* Streamlit's own widgets (inputs, buttons, labels) use rem, so scale them too */
    html { font-size: calc(16px * var(--fs)); }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%,
                rgba(21, 88, 201, .26), transparent 38%),
            radial-gradient(ellipse at 95% 55%,
                rgba(18, 61, 130, .22), transparent 34%),
            #030407;
        color: var(--white);
    }

    /* ---------- Animated background layers ---------- */

    /* Layer 1: moving grid + diagonal brush streaks */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(101, 160, 255, .07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(101, 160, 255, .07) 1px, transparent 1px),
            linear-gradient(45deg, transparent 49.6%,
                rgba(101, 160, 255, .09) 50%, transparent 50.4%),
            linear-gradient(45deg, transparent 24.7%,
                rgba(255, 255, 255, .05) 25%, transparent 25.3%);
        background-size: 56px 56px, 56px 56px, 260px 260px, 260px 260px;
        -webkit-mask-image: radial-gradient(ellipse at 50% 15%,
            #000 15%, transparent 78%);
        mask-image: radial-gradient(ellipse at 50% 15%,
            #000 15%, transparent 78%);
        animation: gridMove 16s linear infinite;
    }

    /* Layer 2: rising light particles */
    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        opacity: .7;
        background-image:
            radial-gradient(circle at 12% 22%, #65A0FF 0, #65A0FF 1.6px, transparent 3px),
            radial-gradient(circle at 31% 64%, #2878EE 0, #2878EE 1.6px, transparent 3px),
            radial-gradient(circle at 47% 12%, #65A0FF 0, #65A0FF 1.4px, transparent 3px),
            radial-gradient(circle at 63% 80%, #65A0FF 0, #65A0FF 1.8px, transparent 3.5px),
            radial-gradient(circle at 78% 38%, #2878EE 0, #2878EE 1.6px, transparent 3px),
            radial-gradient(circle at 92% 70%, #65A0FF 0, #65A0FF 1.4px, transparent 3px);
        background-size: 700px 700px;
        animation: particlesRise 26s linear infinite;
    }

    /* Layer 3: drifting cobalt glows and a slow scan line */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        height: 220px;
        z-index: 0;
        pointer-events: none;
        background: linear-gradient(180deg, transparent,
            rgba(21, 88, 201, .13), transparent);
        animation: scanDown 9s ease-in-out infinite;
    }

    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        width: 520px;
        height: 520px;
        left: -140px;
        top: -140px;
        z-index: 0;
        pointer-events: none;
        border-radius: 50%;
        background: rgba(21, 88, 201, .32);
        filter: blur(100px);
        animation: drift 12s ease-in-out infinite alternate;
    }

    /* Keep real content above the animated layers */
    [data-testid="stMain"],
    section.main,
    [data-testid="stSidebar"] {
        position: relative;
        z-index: 1;
    }

    [data-testid="stHeader"] {
        background: rgba(3, 4, 7, .55);
        backdrop-filter: blur(8px);
    }

    [data-testid="stMainBlockContainer"] {
        position: relative;
        z-index: 1;
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: #070A11;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        color: var(--white);
    }

    /* Brand bar */

    .brandbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 15px 0 24px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 24px;
    }

    .brand {
        color: #FFFFFF;
        font-size: calc(24px * var(--fs));
        font-weight: 800;
        letter-spacing: -1px;
    }

    .brand span {
        color: var(--blue-light);
    }

    .brand-note {
        font-size: calc(10px * var(--fs));
        color: #A3AEC5;
        letter-spacing: 2px;
        text-align: right;
    }

    /* Hero */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 62px 50px;
        border: 1px solid rgba(101, 160, 255, .32);
        border-radius: 26px;
        background:
            linear-gradient(115deg,
                rgba(3, 4, 7, .97) 8%,
                rgba(8, 26, 60, .95) 62%,
                rgba(21, 88, 201, .72));
        box-shadow: 0 24px 80px rgba(0, 0, 0, .45),
                    0 0 0 1px rgba(21, 88, 201, .08) inset;
        animation: rise .7s ease both;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 340px;
        height: 340px;
        right: -70px;
        top: -130px;
        background: rgba(40, 120, 238, .30);
        filter: blur(60px);
        border-radius: 50%;
        animation: drift 8s ease-in-out infinite alternate;
        pointer-events: none;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: 40px;
        top: 50%;
        margin-top: -180px;
        border-radius: 50%;
        border: 1px dashed rgba(101, 160, 255, .35);
        box-shadow: 0 0 0 60px rgba(101, 160, 255, .04),
                    0 0 0 120px rgba(101, 160, 255, .025);
        animation: spin 28s linear infinite;
        pointer-events: none;
    }

    .eyebrow {
        position: relative;
        z-index: 1;
        color: var(--blue-light);
        font-size: calc(11px * var(--fs));
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 22px;
    }

    .hero h1 {
        position: relative;
        z-index: 1;
        font-family: var(--serif) !important;
        color: #FFFFFF;
        font-size: clamp(36px, 5vw, 84px);
        font-weight: 500;
        line-height: 1.1;
        letter-spacing: -1px;
        margin: 0 0 22px;
        padding: 0;
    }

    /* First line in italic cobalt, like the reference title */
    .hero h1::first-line {
        font-style: italic;
        font-weight: 700;
        color: var(--blue-light);
    }

    .hero p {
        position: relative;
        z-index: 1;
        max-width: 620px;
        color: #C0CEE8;
        font-size: calc(15px * var(--fs));
        line-height: 1.9;
        margin: 0;
    }

    /* Sections */

    .section-title {
        font-family: var(--serif);
        color: #F5F7FF;
        font-size: calc(30px * var(--fs));
        font-weight: 500;
        letter-spacing: -.4px;
        margin: 34px 0 7px;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: calc(13px * var(--fs));
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .micro-label {
        color: #8FB8FF;
        font-size: calc(10px * var(--fs));
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Cards */

    .glass-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(145deg, #0E1522, #070A11);
        border: 1px solid var(--line);
        border-radius: 17px;
        padding: 24px;
        transition: transform .25s ease,
                    border-color .25s ease,
                    box-shadow .25s ease;
        animation: rise .6s ease both;
    }

    .glass-card::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        height: 2px;
        width: 0;
        background: linear-gradient(90deg, var(--blue), var(--blue-light));
        transition: width .4s ease;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(101, 160, 255, .7);
        box-shadow: 0 14px 40px rgba(21, 88, 201, .25);
    }

    .glass-card:hover::after {
        width: 100%;
    }

    .metric-label {
        color: #AAB8D2;
        font-size: calc(11px * var(--fs));
        font-weight: 700;
        letter-spacing: 1.3px;
        text-transform: uppercase;
    }

    .metric-number {
        color: #FFFFFF;
        font-size: calc(40px * var(--fs));
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-top: 12px;
    }

    .metric-caption {
        color: #A3AEC5;
        font-size: calc(11px * var(--fs));
        margin-top: 5px;
    }

    .skill-chip {
        display: inline-block;
        padding: 9px 13px;
        margin: 4px 4px 4px 0;
        border: 1px solid rgba(101, 160, 255, .40);
        border-radius: 8px;
        background: rgba(21, 88, 201, .16);
        color: #A7CBFF;
        font-size: calc(12px * var(--fs));
        transition: transform .2s ease, background .2s ease;
    }

    .skill-chip:hover {
        transform: translateY(-2px);
        background: rgba(21, 88, 201, .30);
    }

    .missing-chip {
        display: inline-block;
        padding: 9px 13px;
        margin: 4px 4px 4px 0;
        border: 1px solid rgba(217, 165, 90, .35);
        border-radius: 8px;
        background: rgba(217, 165, 90, .08);
        color: #F1CB91;
        font-size: calc(12px * var(--fs));
        transition: transform .2s ease;
    }

    .missing-chip:hover {
        transform: translateY(-2px);
    }

    .recommendation {
        padding: 18px 20px;
        margin: 10px 0;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: linear-gradient(110deg, #0C1422, #080B12);
        color: #E7EDFF;
        font-size: calc(13px * var(--fs));
        line-height: 1.8;
        transition: border-color .2s ease, transform .2s ease;
        animation: rise .5s ease both;
    }

    .recommendation:hover {
        border-color: var(--blue);
        transform: translateX(4px);
    }

    /* Inputs */

    div[data-testid="stFileUploader"] {
        padding: 15px;
        border: 1px dashed #376EC1;
        border-radius: 16px;
        background: rgba(11, 16, 26, .85);
        transition: border-color .25s ease,
                    background .25s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #75A9FF;
        background: rgba(21, 88, 201, .10);
    }

    div[data-testid="stFileUploader"] section {
        background: transparent;
    }

    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span {
        color: var(--muted);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: #0B111D;
        border-color: #2B3D5D;
        border-radius: 10px;
    }

    div[data-baseweb="select"] * {
        color: var(--white);
    }

    div[data-baseweb="input"] input {
        color: #F3F6FF;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--blue-light);
        box-shadow: 0 0 0 1px var(--blue-light);
    }

    ul[role="listbox"],
    div[data-baseweb="popover"] ul {
        background: #0B111D;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: var(--muted);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* Buttons */

    div.stButton > button,
    div.stDownloadButton > button {
        color: white;
        background: linear-gradient(110deg, #1558C9, #2878EE);
        border: 1px solid rgba(112, 165, 255, .45);
        border-radius: 10px;
        min-height: 46px;
        font-weight: 700;
        transition: transform .2s ease,
                    box-shadow .2s ease,
                    filter .2s ease;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        color: white;
        border-color: #83B4FF;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(21, 88, 201, .45);
        filter: brightness(1.12);
    }

    div.stButton > button:disabled {
        background: #141B2A;
        border-color: #26324A;
        color: #6F7C98;
    }

    div.stButton > button[kind="primary"] {
        animation: btnPulse 3s ease-in-out infinite;
    }

    div.stButton > button[kind="primary"]:disabled {
        animation: none;
    }

    /* Expanders */

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: rgba(11, 16, 26, .75);
    }

    div[data-testid="stExpander"] summary:hover {
        color: var(--blue-light);
    }

    /* Progress bar (thin, like a skill bar) */

    div[data-testid="stProgress"] > div {
        background: var(--track);
        border-radius: 20px;
        overflow: hidden;
        height: 8px;
    }

    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #1558C9, #65A0FF, #1558C9);
        background-size: 200% 100%;
        animation: progressFlow 3s ease infinite;
        border-radius: 20px;
    }

    /* ATS checklist */

    .ats-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid rgba(101, 160, 255, .12);
        font-size: calc(12px * var(--fs));
        color: #E7EDFF;
        line-height: 1.6;
    }

    .ats-tag {
        flex: none;
        min-width: 38px;
        text-align: center;
        padding: 2px 6px;
        border-radius: 6px;
        font-size: calc(10px * var(--fs));
        font-weight: 800;
        letter-spacing: 1px;
    }

    .ats-ok {
        color: #A7CBFF;
        background: rgba(21, 88, 201, .22);
        border: 1px solid rgba(101, 160, 255, .40);
    }

    .ats-fix {
        color: #F1CB91;
        background: rgba(217, 165, 90, .10);
        border: 1px solid rgba(217, 165, 90, .35);
    }

    .ats-tip {
        color: #A3AEC5;
        font-size: calc(11px * var(--fs));
    }

    /* Roadmap */

    .roadmap-phase {
        position: relative;
        margin: 0 0 22px 14px;
        padding: 0 0 0 26px;
        border-left: 2px solid rgba(101, 160, 255, .30);
        animation: rise .6s ease both;
    }

    .roadmap-phase::before {
        content: "";
        position: absolute;
        left: -9px;
        top: 4px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #1558C9;
        border: 3px solid #030407;
        box-shadow: 0 0 0 2px rgba(101, 160, 255, .6);
    }

    .roadmap-head {
        font-family: var(--serif);
        font-size: calc(22px * var(--fs));
        color: #FFFFFF;
    }

    .roadmap-meta {
        margin: 4px 0 12px;
        font-size: calc(12px * var(--fs));
        font-style: italic;
        color: var(--blue-light);
    }

    .roadmap-skill {
        padding: 16px 18px;
        margin: 8px 0;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: linear-gradient(110deg, #0C1422, #080B12);
        font-size: calc(13px * var(--fs));
        line-height: 1.8;
        color: #E7EDFF;
        transition: border-color .2s ease, transform .2s ease;
    }

    .roadmap-skill:hover {
        border-color: var(--blue);
        transform: translateX(4px);
    }

    .roadmap-skill b {
        color: #FFFFFF;
        font-size: calc(14px * var(--fs));
    }

    .roadmap-hours {
        float: right;
        color: var(--blue-light);
        font-size: calc(11px * var(--fs));
        font-weight: 700;
        letter-spacing: 1px;
    }

    .roadmap-label {
        color: #8FB8FF;
        font-size: calc(10px * var(--fs));
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* AI features */

    .ai-badge {
        display: inline-block;
        padding: 3px 10px;
        margin-bottom: 12px;
        border-radius: 999px;
        font-size: calc(10px * var(--fs));
        font-weight: 800;
        letter-spacing: 1.5px;
        border: 1px solid rgba(101, 160, 255, .45);
        color: #A7CBFF;
        background: rgba(21, 88, 201, .20);
    }

    .ai-badge.rules {
        color: #F1CB91;
        border-color: rgba(217, 165, 90, .40);
        background: rgba(217, 165, 90, .08);
    }

    .diff-card {
        padding: 16px 18px;
        margin: 10px 0;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: linear-gradient(110deg, #0C1422, #080B12);
        font-size: calc(13px * var(--fs));
        line-height: 1.8;
        color: #E7EDFF;
    }

    .diff-label {
        display: block;
        margin-top: 8px;
        color: #8FB8FF;
        font-size: calc(10px * var(--fs));
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .diff-before {
        color: #A3AEC5;
        text-decoration: line-through;
        text-decoration-color: rgba(217, 165, 90, .6);
    }

    .diff-after {
        color: #FFFFFF;
    }

    .fb-score {
        font-size: calc(34px * var(--fs));
        font-weight: 800;
        letter-spacing: -1px;
        color: #FFFFFF;
    }

    /* Top toolbar */

    .st-key-toolbar {
        padding: 10px;
        margin-bottom: 22px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: rgba(8, 11, 18, .85);
        backdrop-filter: blur(8px);
    }

    .st-key-toolbar div.stButton > button {
        min-height: 42px;
        font-size: calc(13px * var(--fs));
        animation: none !important;
    }

    .st-key-toolbar div.stButton > button[kind="secondary"],
    .st-key-toolbar button[data-testid="stBaseButton-secondary"] {
        background: transparent;
        border: 1px solid transparent;
        color: #C0CEE8;
        box-shadow: none;
    }

    .st-key-toolbar div.stButton > button[kind="secondary"]:hover,
    .st-key-toolbar button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(21, 88, 201, .18);
        border-color: var(--line);
        transform: none;
        box-shadow: none;
    }

    .st-key-toolbar div.stButton > button:disabled {
        background: transparent;
        border-color: transparent;
        color: #5C6985;
        opacity: .55;
    }

    /* ATS score bar and interview question */

    .ats-track {
        height: 8px;
        margin: 14px 0 6px;
        border-radius: 20px;
        background: var(--track);
        overflow: hidden;
    }

    .ats-fill {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #1558C9, #65A0FF);
        animation: barGrow 1.6s ease-out both;
    }

    .interview-question {
        font-family: var(--serif);
        font-size: calc(26px * var(--fs));
        line-height: 1.4;
        color: #FFFFFF;
        margin: 12px 0 18px;
    }

    @keyframes barGrow {
        from { width: 0; }
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #8A97B2;
        border-top: 1px solid var(--line);
        padding: 25px 0 5px;
        margin-top: 40px;
        font-size: calc(10px * var(--fs));
        letter-spacing: 2px;
        line-height: 2;
    }

    /* Keyframes */

    @keyframes rise {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes drift {
        from { transform: translate(0, 0) scale(1); }
        to { transform: translate(-45px, 35px) scale(1.18); }
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    @keyframes gridMove {
        from { background-position: 0 0, 0 0, 0 0, 0 0; }
        to { background-position: 56px 56px, 56px 56px, 260px 260px, 260px 260px; }
    }

    @keyframes particlesRise {
        from { background-position: 0 0; }
        to { background-position: 0 -700px; }
    }

    @keyframes scanDown {
        0% { transform: translateY(-240px); }
        100% { transform: translateY(100vh); }
    }

    @keyframes progressFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes btnPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(21, 88, 201, .5); }
        50% { box-shadow: 0 0 0 12px rgba(21, 88, 201, 0); }
    }

    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1rem;
        }

        .hero {
            padding: 34px 23px;
            border-radius: 17px;
        }

        .hero::after {
            display: none;
        }

        .hero h1 {
            font-size: calc(36px * var(--fs));
            letter-spacing: -.5px;
        }

        .section-title {
            font-size: calc(25px * var(--fs));
        }

        .metric-number {
            font-size: calc(30px * var(--fs));
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def render_brand():
    st.markdown(
        """
        <div class="brandbar">
            <div class="brand">Skill<span>Scope</span></div>
            <div class="brand-note">
                CAREER INTELLIGENCE<br>
                RESUME SKILL ANALYSIS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            SKILLSCOPE<br>
            CAREER CLARITY THROUGH SKILL ANALYSIS
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_chips(skills, missing=False):
    if not skills:
        st.caption("No skills to display.")
        return

    css_class = "missing-chip" if missing else "skill-chip"
    chips = "".join(
        f'<span class="{css_class}">{html.escape(str(skill))}</span>'
        for skill in skills
    )
    st.markdown(chips, unsafe_allow_html=True)


def normalize_percentage(value):
    try:
        return max(0.0, min(100.0, float(value)))
    except (ValueError, TypeError):
        return 0.0


def go_to(screen, view=None):
    """Button callback: switch screen (and results view)."""
    st.session_state.screen = screen
    if view:
        st.session_state.view = view


def render_toolbar():
    """Top navigation bar shown on every screen."""
    has_analysis = st.session_state.get("analysis_data") is not None
    screen = st.session_state.screen
    view = st.session_state.get("view", "gap")

    items = [
        ("Home", "home", None, False),
        ("Skill Gap", "results", "gap", not has_analysis),
        ("ATS Score", "results", "ats", not has_analysis),
        ("Learning Roadmap", "results", "roadmap", not has_analysis),
        ("Mock Interview", "interview", None, False),
    ]

    with st.container(key="toolbar"):
        columns = st.columns(len(items))

        for column, (label, target, target_view, disabled) in zip(
            columns, items
        ):
            active = screen == target and (
                target_view is None or view == target_view
            )

            with column:
                st.button(
                    label,
                    key=f"nav_{label}",
                    type="primary" if active else "secondary",
                    disabled=disabled,
                    use_container_width=True,
                    on_click=go_to,
                    args=(target, target_view),
                )


def render_ai_settings():
    """Optional API key box. Returns the key in use (may be empty)."""
    with st.expander("AI settings (optional)"):
        st.text_input(
            "Anthropic API key",
            type="password",
            key="anthropic_key",
            help="Leave empty to use the built-in rules. You can also set "
                 "ANTHROPIC_API_KEY as an environment variable or in "
                 ".streamlit/secrets.toml.",
        )
        st.caption(
            "With a key, AI mode sends your resume text and interview "
            "answers to the Anthropic API. Without a key, everything stays "
            "on your computer and simple built-in rules are used instead."
        )

    return get_api_key()


def ats_band(score):
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Good, with a few fixes"
    if score >= 45:
        return "Needs work"
    return "Needs a lot of work"


def render_ats_card(ats):
    score = ats["score"]

    # Problems first, so the user sees what to fix straight away.
    ordered = sorted(ats["checks"], key=lambda check: check["passed"])

    rows = []
    for check in ordered:
        tag_class = "ats-ok" if check["passed"] else "ats-fix"
        tag_text = "OK" if check["passed"] else "FIX"
        tip = (
            ""
            if check["passed"]
            else '<div class="ats-tip">' + html.escape(check["tip"]) + "</div>"
        )
        rows.append(
            '<div class="ats-row">'
            f'<span class="ats-tag {tag_class}">{tag_text}</span>'
            f'<span>{html.escape(check["label"])}{tip}</span>'
            "</div>"
        )

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="metric-label">Your ATS score</div>
            <div class="metric-number">{score}<span style="font-size:calc(18px * var(--fs));
                color:#A3AEC5"> / 100</span></div>
            <div class="metric-caption">{ats_band(score)}</div>
            <div class="ats-track"><div class="ats-fill"
                style="width:{score}%"></div></div>
            <div class="metric-caption" style="margin-bottom:14px">
                Scored on contact details, sections, writing quality, measurable results and keyword match for your target role. A guide, not a hiring prediction.
            </div>
            {"".join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_roadmap(roadmap):
    for phase in roadmap["phases"]:
        skill_cards = "".join(
            f"""
            <div class="roadmap-skill">
                <span class="roadmap-hours">~{item['hours']} HRS</span>
                <b>{html.escape(item['skill'])}</b><br>
                <span class="roadmap-label">Learn</span>
                {html.escape(item['learn'])}<br>
                <span class="roadmap-label">Practise</span>
                {html.escape(item['project'])}
            </div>
            """
            for item in phase["items"]
        )

        st.markdown(
            f"""
            <div class="roadmap-phase">
                <div class="roadmap-head">{html.escape(phase['title'])}</div>
                <div class="roadmap-meta">
                    {html.escape(phase['weeks'])} &nbsp;/&nbsp;
                    about {phase['hours']} hours
                </div>
                {skill_cards}
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_api_key():
    """API key from the settings box, Streamlit secrets or environment."""
    typed = str(st.session_state.get("anthropic_key", "")).strip()
    if typed:
        return typed

    try:
        secret = str(st.secrets.get("ANTHROPIC_API_KEY", "")).strip()
    except Exception:
        secret = ""

    return secret or os.environ.get("ANTHROPIC_API_KEY", "").strip()


def render_mode_badge(mode):
    if mode == "ai":
        st.markdown(
            '<span class="ai-badge">AI MODE</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="ai-badge rules">BUILT-IN RULES</span>',
            unsafe_allow_html=True,
        )


def render_improvement(result):
    render_mode_badge(result.get("mode"))

    if result.get("warning"):
        st.warning(result["warning"])

    if result.get("summary"):
        st.markdown(
            f"""
            <div class="diff-card">
                <span class="diff-label">Suggested summary</span>
                <span class="diff-after">{html.escape(result['summary'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result.get("bullets"):
        st.markdown(
            '<div class="section-subtitle" style="margin:16px 0 0">'
            'Suggested line rewrites</div>',
            unsafe_allow_html=True,
        )
        for item in result["bullets"]:
            before = (
                f'<span class="diff-label">Before</span>'
                f'<span class="diff-before">{html.escape(item["original"])}</span>'
                if item.get("original") else ""
            )
            why = (
                f'<span class="diff-label">Why</span>{html.escape(item["why"])}'
                if item.get("why") else ""
            )
            st.markdown(
                f"""
                <div class="diff-card">
                    {before}
                    <span class="diff-label">After</span>
                    <span class="diff-after">{html.escape(item['improved'])}</span>
                    {why}
                </div>
                """,
                unsafe_allow_html=True,
            )

    if result.get("skills_to_surface"):
        st.markdown(
            '<div class="section-subtitle" style="margin:16px 0 6px">'
            'If you genuinely have experience with these, add them to your '
            'Skills section and show them in a project:</div>',
            unsafe_allow_html=True,
        )
        render_skill_chips(result["skills_to_surface"], missing=True)

    if result.get("tips"):
        for tip in result["tips"]:
            st.markdown(
                f'<div class="recommendation">{html.escape(tip)}</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "Check that every suggested line is true before you use it, and "
        "replace anything in [brackets] with your real details."
    )


def render_interview_feedback(feedback):
    render_mode_badge(feedback.get("mode"))

    if feedback.get("warning"):
        st.warning(feedback["warning"])

    strengths = "".join(
        f"<li>{html.escape(item)}</li>" for item in feedback.get("strengths", [])
    )
    improvements = "".join(
        f"<li>{html.escape(item)}</li>"
        for item in feedback.get("improvements", [])
    )
    outline = (
        f'<span class="diff-label">Stronger answer outline</span>'
        f'{html.escape(feedback["outline"])}'
        if feedback.get("outline") else ""
    )

    st.markdown(
        f"""
        <div class="diff-card">
            <span class="diff-label">Score</span>
            <span class="fb-score">{feedback['score']}<span
                style="font-size:calc(16px * var(--fs));color:#A3AEC5"> / 10</span></span>
            <span class="diff-label">What worked</span>
            <ul style="margin:4px 0 0 18px">{strengths or '<li>Nothing stood out yet.</li>'}</ul>
            <span class="diff-label">How to improve</span>
            <ul style="margin:4px 0 0 18px">{improvements or '<li>No major issues found.</li>'}</ul>
            {outline}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if feedback.get("note"):
        st.caption(feedback["note"])


# =========================================================
# SESSION STATE
# =========================================================

if "screen" not in st.session_state:
    st.session_state.screen = "home"

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "selected_role" not in st.session_state:
    st.session_state.selected_role = "Data Analyst"

if "view" not in st.session_state:
    st.session_state.view = "gap"

if "improvement" not in st.session_state:
    st.session_state.improvement = None

if "interview" not in st.session_state:
    st.session_state.interview = None


# =========================================================
# HEADER
# =========================================================

render_brand()
render_toolbar()


# =========================================================
# SCREEN 1 - HOME AND RESUME UPLOAD
# =========================================================

if st.session_state.screen == "home":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">A SMARTER WAY TO PLAN YOUR CAREER</div>
            <h1>Know your skills.<br>Discover your next move.</h1>
            <p>
                Compare your resume against the skills expected for your
                target role. Discover your strengths, identify gaps, and
                get practical recommendations to improve your profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Find your target role</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Search from the available roles, '
        'then upload your resume to begin.</div>',
        unsafe_allow_html=True,
    )

    compare_mode = st.radio(
        "Compare my resume against",
        ["A predefined job role", "A job description I paste"],
        horizontal=True,
        key="compare_mode",
    )
    use_jd = compare_mode == "A job description I paste"

    if not use_jd:
        # Streamlit's selectbox has built-in type-to-search: click the dropdown
        # and start typing a role to filter the list. This keeps search inside
        # the dropdown instead of showing a separate search field.
        current_role = st.session_state.selected_role
        if current_role not in ALL_ROLES:
            current_role = ALL_ROLES[0]

        selected_role = st.selectbox(
            "Target role",
            options=ALL_ROLES,
            index=ALL_ROLES.index(current_role),
            key="role_selector",
            help="Open the dropdown and start typing to search and filter job roles.",
        )

        st.session_state.selected_role = selected_role

        role_skills = JOB_ROLE_SKILLS[selected_role]

        st.markdown(
            f"""
            <div class="glass-card">
                <div class="micro-label">SELECTED CAREER PATH</div>
                <div style="font-size:calc(23px * var(--fs));font-weight:750;
                            color:#FFFFFF;margin-top:10px">
                    {html.escape(selected_role)}
                </div>
                <p style="font-size:calc(12px * var(--fs));color:#A3AEC5;
                          line-height:1.8;margin-top:10px">
                    This analysis checks your resume against
                    {len(role_skills)} predefined skills for this role.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        jd_text = st.text_area(
            "Paste the job description",
            height=220,
            key="jd_text",
            placeholder=(
                "Paste the full job description here. SkillScope will pick "
                "out the skills it recognises and compare them with your "
                "resume."
            ),
        )

        jd_skills = extract_jd_skills(jd_text, SKILL_VOCABULARY)

        if jd_skills:
            selected_role = "Custom job description"
            role_skills = jd_skills

            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="micro-label">SKILLS FOUND IN THE JOB DESCRIPTION</div>
                    <p style="font-size:calc(12px * var(--fs));color:#A3AEC5;
                              line-height:1.8;margin:10px 0 6px">
                        {len(jd_skills)} skills detected. Your resume will be
                        checked against these.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_skill_chips(jd_skills)
        else:
            selected_role = None
            role_skills = []

            if jd_text.strip():
                st.warning(
                    "No known skills were found in this text. Try pasting "
                    "the requirements section, or choose a predefined role."
                )
            else:
                st.info(
                    "Paste a job description above to see which skills "
                    "it asks for."
                )

    st.markdown(
        '<div class="section-title">Upload your resume</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Accepted formats: PDF, DOCX, '
        'PNG, JPG, TIFF, BMP and WEBP.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a resume file (Maximum 5 MB)",
        type=[
            "pdf", "docx", "png", "jpg", "jpeg",
            "tif", "tiff", "bmp", "webp",
        ],
        max_upload_size=5,
        key="resume_uploader",
    )

    st.markdown("")

    start_analysis = st.button(
        "Analyze my resume",
        type="primary",
        use_container_width=True,
        disabled=(uploaded_file is None or selected_role is None),
    )

    if start_analysis and uploaded_file is not None and selected_role:

        temporary_path = None

        try:
            suffix = Path(uploaded_file.name).suffix.lower()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temporary_file:
                temporary_file.write(uploaded_file.getvalue())
                temporary_path = Path(temporary_file.name)

            with st.spinner(
                "Extracting resume text and comparing your skills..."
            ):
                
                resume_text, extraction_methods = extract_resume(
                temporary_path
                )
                # STEP 1: Check whether text was extracted
                if not resume_text.strip():
                    st.error(
                        "No text could be extracted. Please upload "
                        "a readable resume."
                        )
                else:
                    # STEP 2: Validate whether the document is a resume
                    is_valid, message = validate_resume(resume_text)
                if not is_valid:
                    st.error("Invalid Document")
                    st.warning(
                        "This file does not appear to be a resume. "
                        "Please upload a valid resume instead of "
                        "a question paper, notes, or another document."
                        )
                    st.info(message)
                else:
                # STEP 3: Continue normal resume analysis
                    analysis_result = analyze_resume(
                        resume_text,
                        role_skills,
                        )
                    st.session_state.analysis_data = {
                        "role": selected_role,
                        "role_skills": list(role_skills),
                        "filename": uploaded_file.name,
                        "resume_text": resume_text,
                        "extraction_methods": extraction_methods,
                        "results": analysis_result,
                        }
                    st.session_state.improvement = None
                    st.session_state.view = "gap"
                    st.session_state.interview = None
                    
                    st.session_state.screen = "results"
                    st.rerun()


                    st.session_state.analysis_data = {
                        "role": selected_role,
                        "role_skills": list(role_skills),
                        "filename": uploaded_file.name,
                        "resume_text": resume_text,
                        "extraction_methods": extraction_methods,
                        "results": analysis_result,
                    }

                    st.session_state.improvement = None
                    st.session_state.view = "gap"
                    st.session_state.interview = None

                    # Move to the separate results screen.
                    st.session_state.screen = "results"
                    st.rerun()

        except Exception as error:
            st.error(f"Analysis failed: {error}")

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    st.markdown("")
    st.markdown(
        """
        <div class="section-subtitle" style="text-align:center">
            Your resume is processed by this app for analysis.
            Review the extracted text before sharing the report.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_footer()


# =========================================================
# SCREEN 2 - SKILL GAP, ATS SCORE AND LEARNING ROADMAP
# =========================================================

elif st.session_state.screen == "results":

    data = st.session_state.analysis_data

    if not data:
        st.session_state.screen = "home"
        st.rerun()

    results = data["results"]
    role = data["role"]
    view = st.session_state.get("view", "gap")

    matched_skills = results.get("matched_skills", [])
    missing_skills = results.get("missing_skills", [])
    resume_skills = results.get("resume_skills", [])

    percentage = normalize_percentage(
        results.get("match_percentage", 0)
    )

    ats = score_resume(
        data["resume_text"],
        matched_keywords=len(matched_skills),
        total_keywords=len(matched_skills) + len(missing_skills),
    )
    study_hours = st.session_state.get("study_hours", 10)
    study_level = st.session_state.get("study_level", LEVEL_OPTIONS[0])
    roadmap = build_roadmap(
        missing_skills,
        study_hours,
        LEVEL_FACTORS.get(study_level, 1.0),
    )
    suggestions = get_suggestions(missing_skills)
    analysis_key = f"{data['filename']}|{role}"

    # -----------------------------------------------------
    # VIEW 1 - SKILL GAP
    # -----------------------------------------------------

    if view == "gap":

        st.markdown(
            """
            <div class="hero">
                <div class="eyebrow">YOUR SKILL GAP</div>
                <h1>Here is where you<br>stand today.</h1>
                <p>
                    See which skills your resume already shows and which
                    ones are missing for this role. Then check your ATS
                    score, get a learning roadmap, or practise an interview.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="section-title">Skill gap analysis</div>
            <div class="section-subtitle">
                Target role: <b>{html.escape(role)}</b><br>
                Resume: {html.escape(data["filename"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="metric-label">Skill alignment</div>
                    <div class="metric-number">{percentage:.1f}%</div>
                    <div class="metric-caption">Based on the role's skills</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="metric-label">Skills you have</div>
                    <div class="metric-number">{len(matched_skills)}</div>
                    <div class="metric-caption">Found in your resume</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="metric-label">Skills to develop</div>
                    <div class="metric-number">{len(missing_skills)}</div>
                    <div class="metric-caption">Not found in your resume</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">Overall skill alignment</div>',
            unsafe_allow_html=True,
        )

        st.progress(percentage / 100.0)

        st.caption(
            "This score measures keyword matches against the role's skills. "
            "It is not a hiring probability or a complete assessment of "
            "your abilities."
        )

        left, right = st.columns(2)

        with left:
            st.markdown(
                '<div class="section-title">Skills you have</div>',
                unsafe_allow_html=True,
            )

            if matched_skills:
                render_skill_chips(matched_skills)
            else:
                st.info("No required skills were detected in your resume.")

        with right:
            st.markdown(
                '<div class="section-title">Skills to develop</div>',
                unsafe_allow_html=True,
            )

            if missing_skills:
                render_skill_chips(missing_skills, missing=True)
            else:
                st.success("All the role's skills were detected.")

        if suggestions:
            st.markdown(
                '<div class="section-title">Quick tips</div>',
                unsafe_allow_html=True,
            )

            for index, suggestion in enumerate(suggestions, start=1):
                st.markdown(
                    f"""
                    <div class="recommendation">
                        <div class="micro-label">TIP {index}</div>
                        <div style="margin-top:7px">
                            {html.escape(str(suggestion))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # NEXT STEPS

        st.markdown(
            '<div class="section-title">What would you like to do next?</div>',
            unsafe_allow_html=True,
        )

        step1, step2, step3 = st.columns(3)

        with step1:
            st.button(
                "Check my ATS score",
                key="next_ats",
                on_click=go_to,
                args=("results", "ats"),
                use_container_width=True,
            )
            st.caption(
                "See how your resume scores and how to improve it."
            )

        with step2:
            st.button(
                "Personalized learning roadmap",
                key="next_roadmap",
                on_click=go_to,
                args=("results", "roadmap"),
                use_container_width=True,
                disabled=not missing_skills,
            )
            st.caption(
                "A step-by-step plan for the skills you are missing."
            )

        with step3:
            st.button(
                "AI mock interview",
                key="next_interview",
                on_click=go_to,
                args=("interview",),
                use_container_width=True,
            )
            st.caption("Practise questions for this role and get feedback.")

        # EXTRA DETAILS

        with st.expander("View all skills detected in the resume"):
            st.write(
                ", ".join(resume_skills)
                if resume_skills
                else "No skills were detected."
            )

        with st.expander("View extracted resume text"):
            st.text_area(
                "Extracted text",
                value=data["resume_text"],
                height=260,
                disabled=True,
            )

        with st.expander("View extraction details"):
            for method in data["extraction_methods"]:
                st.write(f"- {method}")

        # DOWNLOAD REPORT

        report_lines = [
            "SKILLSCOPE - RESUME SKILL GAP REPORT",
            "=" * 42,
            f"Target role: {role}",
            f"Resume file: {data['filename']}",
            f"Skill alignment: {percentage:.1f}%",
            "",
            "MATCHED SKILLS",
            *[f"- {skill}" for skill in matched_skills],
            "",
            "SKILLS TO DEVELOP",
            *[f"- {skill}" for skill in missing_skills],
            "",
            "ATS SCORE",
            *ats_to_text(ats),
            "",
            "LEARNING ROADMAP",
            *roadmap_to_text(roadmap),
            "",
            "Note: This report uses predefined skill keywords. "
            "It does not guarantee employment or measure every skill.",
        ]

        st.download_button(
            "Download skill gap report",
            data="\n".join(report_lines),
            file_name="skillscope_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

        if st.button("Analyze another resume", use_container_width=True):
            st.session_state.analysis_data = None
            st.session_state.screen = "home"
            st.rerun()

    # -----------------------------------------------------
    # VIEW 2 - ATS SCORE AND IMPROVEMENT
    # -----------------------------------------------------

    elif view == "ats":

        st.markdown(
            f"""
            <div class="section-title">Your ATS score</div>
            <div class="section-subtitle">
                Checks that recruiters and applicant tracking systems look
                for in <b>{html.escape(data["filename"])}</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_ats_card(ats)

        st.markdown(
            '<div class="section-title">How to improve your resume</div>',
            unsafe_allow_html=True,
        )

        api_key = get_api_key()
        improvement = st.session_state.get("improvement")

        if not improvement or improvement.get("key") != analysis_key:
            with st.spinner("Reviewing your resume..."):
                improvement = improve_resume(
                    data["resume_text"], role, matched_skills,
                    missing_skills, api_key, ats,
                )
            improvement["key"] = analysis_key
            st.session_state.improvement = improvement

        render_improvement(improvement)

        if st.button("Regenerate suggestions", key="regenerate_improvement"):
            st.session_state.improvement = None
            st.rerun()

        render_ai_settings()

        st.button(
            "Next: personalized learning roadmap",
            key="ats_next",
            on_click=go_to,
            args=("results", "roadmap"),
            use_container_width=True,
            disabled=not missing_skills,
        )

    # -----------------------------------------------------
    # VIEW 3 - PERSONALIZED LEARNING ROADMAP
    # -----------------------------------------------------

    elif view == "roadmap":

        st.markdown(
            '<div class="section-title">Your personalized learning roadmap</div>',
            unsafe_allow_html=True,
        )

        if missing_skills:
            st.markdown(
                f"""
                <div class="section-subtitle">
                    A suggested order for learning the
                    {len(missing_skills)} skills missing for
                    <b>{html.escape(role)}</b>, with a small project for
                    each one.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.slider(
                "Study hours per week",
                min_value=3,
                max_value=30,
                value=10,
                key="study_hours",
            )

            st.selectbox(
                "Your current level with these skills",
                LEVEL_OPTIONS,
                key="study_level",
            )

            finish_date = (
                date.today() + timedelta(weeks=roadmap["total_weeks"])
            ).strftime("%d %b %Y")

            st.markdown(
                f"""
                <div class="section-subtitle">
                    Estimated effort: about <b>{roadmap['total_hours']} hours</b>,
                    roughly <b>{roadmap['total_weeks']} weeks</b> at
                    {roadmap['hours_per_week']} hours per week. Starting today,
                    you could finish around <b>{finish_date}</b>.
                </div>
                """,
                unsafe_allow_html=True,
            )

            render_roadmap(roadmap)

            st.caption(
                "Hours are rough starter estimates and resources are "
                "suggestions, not guarantees. Adjust them to your own pace."
            )
        else:
            st.success(
                "No roadmap needed: all the role's skills were detected."
            )

        st.button(
            "Next: AI mock interview",
            key="roadmap_next",
            on_click=go_to,
            args=("interview",),
            use_container_width=True,
        )

    render_footer()


# =========================================================
# SCREEN 3 - AI MOCK INTERVIEW
# =========================================================

elif st.session_state.screen == "interview":

    def next_question():
        st.session_state.interview["index"] += 1

    def end_interview():
        st.session_state.interview = None

    data = st.session_state.analysis_data
    interview = st.session_state.get("interview")

    st.markdown(
        '<div class="section-title">AI mock interview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Choose a role, answer five interview '
        'questions one at a time, and get feedback on every answer.</div>',
        unsafe_allow_html=True,
    )

    active = bool(interview) and interview["index"] < len(
        interview["questions"]
    )

    if "interview_role" not in st.session_state:
        start_role = st.session_state.selected_role
        if data and data["role"] in ALL_ROLES:
            start_role = data["role"]
        st.session_state.interview_role = (
            start_role if start_role in ALL_ROLES else ALL_ROLES[0]
        )

    chosen_role = st.selectbox(
        "Choose the role you are interviewing for",
        ALL_ROLES,
        key="interview_role",
        disabled=active,
    )

    use_resume = False
    if data:
        use_resume = st.checkbox(
            "Use my resume to personalise the questions",
            value=True,
            key="interview_use_resume",
            disabled=active,
        )

    api_key = render_ai_settings()
    st.caption(
        "Mode: AI interviewer" if ai_available(api_key)
        else "Mode: built-in questions and feedback (no API key set)"
    )

    if active:
        restart_col, end_col = st.columns(2)
        with restart_col:
            start_clicked = st.button(
                "Restart interview", key="interview_start",
                use_container_width=True,
            )
        with end_col:
            st.button(
                "End interview", key="interview_end",
                on_click=end_interview, use_container_width=True,
            )
    else:
        start_clicked = st.button(
            "Start mock interview", key="interview_start",
            type="primary", use_container_width=True,
        )

    if start_clicked:
        for stale_key in [
            k for k in st.session_state if str(k).startswith("answer_")
        ]:
            del st.session_state[stale_key]

        role_skill_list = JOB_ROLE_SKILLS[chosen_role]
        interview_matched = []
        interview_missing = []
        interview_resume = ""

        if data and use_resume:
            known = {
                str(skill).casefold()
                for skill in data["results"].get("resume_skills", [])
            } | {
                str(skill).casefold()
                for skill in data["results"].get("matched_skills", [])
            }
            interview_matched = [
                s for s in role_skill_list if s.casefold() in known
            ]
            interview_missing = [
                s for s in role_skill_list if s.casefold() not in known
            ]
            interview_resume = data["resume_text"]

        with st.spinner("Preparing your interview..."):
            generated = generate_questions(
                chosen_role, interview_matched, interview_missing,
                role_skill_list, interview_resume, api_key,
            )

        st.session_state.interview = {
            "role": chosen_role,
            "mode": generated["mode"],
            "warning": generated.get("warning", ""),
            "questions": generated["questions"],
            "index": 0,
            "answers": {},
            "feedback": {},
        }
        st.rerun()

    interview = st.session_state.get("interview")

    if interview:
        questions = interview["questions"]
        index = interview["index"]
        total = len(questions)

        render_mode_badge(interview["mode"])

        if interview.get("warning"):
            st.warning(interview["warning"])

        if index < total:
            item = questions[index]

            st.progress(index / total)

            st.markdown(
                f"""
                <div class="micro-label">
                    QUESTION {index + 1} OF {total} /
                    {html.escape(item['type'])} /
                    {html.escape(interview['role'])}
                </div>
                <div class="interview-question">
                    {html.escape(item['question'])}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if index not in interview["feedback"]:
                answer = st.text_area(
                    "Your answer",
                    key=f"answer_{index}",
                    height=170,
                    placeholder="Type your answer as you would say it in "
                                "the interview.",
                )

                if st.button(
                    "Submit answer", key=f"submit_{index}",
                    type="primary", use_container_width=True,
                ):
                    if answer.strip():
                        with st.spinner("Reviewing your answer..."):
                            interview["feedback"][index] = evaluate_answer(
                                item, answer, interview["role"], api_key
                            )
                        interview["answers"][index] = answer
                        st.rerun()
                    else:
                        st.warning("Write an answer first.")
            else:
                st.markdown(
                    f"""
                    <div class="diff-card">
                        <span class="diff-label">Your answer</span>
                        {html.escape(interview["answers"].get(index, ""))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                render_interview_feedback(interview["feedback"][index])

                st.button(
                    "Next question" if index < total - 1
                    else "Finish interview",
                    key=f"next_{index}",
                    on_click=next_question,
                    type="primary",
                    use_container_width=True,
                )

        else:
            scores = [
                interview["feedback"][i]["score"]
                for i in range(total) if i in interview["feedback"]
            ]
            average = sum(scores) / len(scores) if scores else 0

            if average >= 8:
                verdict = "Strong performance. Keep your answers specific."
            elif average >= 5:
                verdict = (
                    "Decent start. Add concrete examples, numbers and a "
                    "clear structure to your answers."
                )
            else:
                verdict = (
                    "Keep practising. Explain what you did, how, and what "
                    "the result was."
                )

            rows = "".join(
                f"<li>Question {i + 1} ({html.escape(questions[i]['type'])}): "
                f"{interview['feedback'][i]['score']} / 10</li>"
                for i in range(total) if i in interview["feedback"]
            )

            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="metric-label">Interview complete</div>
                    <div class="metric-number">{average:.1f}
                        <span style="font-size:calc(18px * var(--fs));color:#A3AEC5"> / 10</span>
                    </div>
                    <div class="metric-caption">{html.escape(verdict)}</div>
                    <ul style="margin:14px 0 0 18px;font-size:calc(13px * var(--fs));
                               line-height:1.9;color:#E7EDFF">{rows}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.button(
                "Start a new interview",
                key="interview_again",
                on_click=end_interview,
                type="primary",
                use_container_width=True,
            )

    render_footer()
