import html
import tempfile
from pathlib import Path

import streamlit as st

from extract_resume import extract_resume
from skill_analyzer import analyze_resume, get_suggestions


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
    }

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
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .brand span {
        color: var(--blue-light);
    }

    .brand-note {
        font-size: 10px;
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
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 22px;
    }

    .hero h1 {
        position: relative;
        z-index: 1;
        font-family: var(--serif) !important;
        color: #FFFFFF;
        font-size: clamp(36px, 5vw, 64px);
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
        font-size: 15px;
        line-height: 1.9;
        margin: 0;
    }

    /* Sections */

    .section-title {
        font-family: var(--serif);
        color: #F5F7FF;
        font-size: 30px;
        font-weight: 500;
        letter-spacing: -.4px;
        margin: 34px 0 7px;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .micro-label {
        color: #8FB8FF;
        font-size: 10px;
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
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.3px;
        text-transform: uppercase;
    }

    .metric-number {
        color: #FFFFFF;
        font-size: 40px;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-top: 12px;
    }

    .metric-caption {
        color: #A3AEC5;
        font-size: 11px;
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
        font-size: 12px;
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
        font-size: 12px;
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
        font-size: 13px;
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

    /* Footer */

    .footer {
        text-align: center;
        color: #8A97B2;
        border-top: 1px solid var(--line);
        padding: 25px 0 5px;
        margin-top: 40px;
        font-size: 10px;
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
            font-size: 36px;
            letter-spacing: -.5px;
        }

        .section-title {
            font-size: 25px;
        }

        .metric-number {
            font-size: 30px;
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


# =========================================================
# SESSION STATE
# =========================================================

if "screen" not in st.session_state:
    st.session_state.screen = "home"

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "selected_role" not in st.session_state:
    st.session_state.selected_role = "Data Analyst"


# =========================================================
# HEADER
# =========================================================

render_brand()


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
            <div style="font-size:23px;font-weight:750;
                        color:#FFFFFF;margin-top:10px">
                {html.escape(selected_role)}
            </div>
            <p style="font-size:12px;color:#A3AEC5;
                      line-height:1.8;margin-top:10px">
                This analysis checks your resume against
                {len(role_skills)} predefined skills for this role.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
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
        "Choose a resume file",
        type=[
            "pdf", "docx", "png", "jpg", "jpeg",
            "tif", "tiff", "bmp", "webp",
        ],
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

                if not resume_text.strip():
                    st.error(
                        "No text could be extracted. Try another resume "
                        "or upload a clearer document."
                    )
                else:
                    analysis_result = analyze_resume(
                        resume_text,
                        JOB_ROLE_SKILLS[selected_role],
                    )

                    st.session_state.analysis_data = {
                        "role": selected_role,
                        "filename": uploaded_file.name,
                        "resume_text": resume_text,
                        "extraction_methods": extraction_methods,
                        "results": analysis_result,
                    }

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
# SCREEN 2 - SEPARATE ANALYSIS RESULTS PAGE
# =========================================================

elif st.session_state.screen == "results":

    data = st.session_state.analysis_data

    if not data:
        st.session_state.screen = "home"
        st.rerun()

    results = data["results"]
    role = data["role"]

    st.button(
        "Back to resume upload",
        on_click=lambda: setattr(st.session_state, "screen", "home"),
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR PERSONAL SKILL REPORT</div>
            <h1>Your next career move<br>starts here.</h1>
            <p>
                Review your skill alignment, explore the areas to improve,
                and use the recommendations to plan your next steps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="section-title">Analysis results</div>
        <div class="section-subtitle">
            Target role: <b>{html.escape(role)}</b><br>
            Resume: {html.escape(data["filename"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    matched_skills = results.get("matched_skills", [])
    missing_skills = results.get("missing_skills", [])
    resume_skills = results.get("resume_skills", [])

    percentage = normalize_percentage(
        results.get("match_percentage", 0)
    )

    # METRIC CARDS

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">Skill alignment</div>
                <div class="metric-number">{percentage:.1f}%</div>
                <div class="metric-caption">Based on predefined role skills</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">Matched skills</div>
                <div class="metric-number">{len(matched_skills)}</div>
                <div class="metric-caption">Required keywords detected</div>
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
                <div class="metric-caption">Required keywords not detected</div>
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
        "This score measures keyword matches against the selected role's "
        "predefined skills. It is not a hiring probability or a complete "
        "assessment of your abilities."
    )

    # MATCHED AND MISSING SKILLS

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-title">Skills found</div>',
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
            st.success("All predefined role skills were detected.")

    # RECOMMENDATIONS

    st.markdown(
        '<div class="section-title">Recommended next steps</div>',
        unsafe_allow_html=True,
    )

    suggestions = get_suggestions(missing_skills)

    if suggestions:
        for index, suggestion in enumerate(suggestions, start=1):
            st.markdown(
                f"""
                <div class="recommendation">
                    <div class="micro-label">STEP {index}</div>
                    <div style="margin-top:7px">
                        {html.escape(str(suggestion))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="recommendation">
                No skill-gap recommendations are available for this result.
                Consider validating your resume against a real job
                description to find additional improvements.
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        "RECOMMENDATIONS",
        *[f"- {suggestion}" for suggestion in suggestions],
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

    render_footer()