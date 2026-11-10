"""Skill categories and learning roadmap for SkillScope.

The learning data below is a curated starter set (resource names are
well-known free or official sources, no links). Skills that are not listed
fall back to a generic plan, so the roadmap works for every role.
"""

import math

# ---------------------------------------------------------
# CATEGORIES (used by the radar chart)
# ---------------------------------------------------------

CATEGORY_KEYWORDS = [
    ("AI / ML", [
        "machine learning", "deep learning", "nlp", "llm", "prompt",
        "rag", "vector", "embedding", "tensorflow", "pytorch", "scikit",
        "mlops", "opencv", "computer vision", "transformers",
        "generative", "langchain", "feature engineering",
        "model deployment", "evaluation", "image processing",
        "text processing",
    ]),
    ("Security & Networking", [
        "network", "cyber", "siem", "incident", "vulnerab", "security",
        "firewall", "tcp", "dns", "dhcp", "routing", "switching",
        "vlan", "cryptography",
    ]),
    ("Cloud & DevOps", [
        "aws", "azure", "google cloud", "cloud", "docker", "kubernetes",
        "terraform", "jenkins", "ci/cd", "linux", "iam", "ec2", "s3",
        "lambda", "vpc", "cloudwatch", "monitoring", "shell", "system",
        "backup", "recovery", "windows server",
    ]),
    ("Design", [
        "figma", "ui", "ux", "typography", "color", "wireframing",
        "prototyping", "design systems", "adobe", "canva", "branding",
        "graphic", "usability", "information architecture",
    ]),
    ("Web & Mobile", [
        "html", "css", "javascript", "react", "typescript", "node",
        "responsive", "web", "android", "flutter", "dart", "kotlin",
        "firebase", "rest", "api", "authentication", "deployment",
        "flask", "django", "spring",
    ]),
    ("Programming & CS", [
        "python", "java", "c++", "c#", "data structures",
        "object-oriented", "oop", "git", "collections", "exception",
        "maven", "testing", "debugging", "selenium", "junit", "bug",
        "test", "unity", "unreal", "game", "embedded", "rtos",
        "microcontroller", "iot", "mqtt", "blockchain", "solidity",
        "smart contracts", "web3", "electronics", "3d mathematics",
    ]),
    ("Data & Analytics", [
        "sql", "mysql", "postgresql", "pandas", "numpy", "statistic",
        "power bi", "tableau", "excel", "dax", "power query", "data",
        "etl", "spark", "hadoop", "kafka", "airflow", "pivot",
        "vlookup", "xlookup", "probability", "regression", "hypothesis",
        "dashboard", "analytics", "reporting", "forecasting", "query",
        "stored procedures", "dbms", "tuning", "database",
    ]),
]

EXACT_CATEGORY = {"c": "Programming & CS", "r": "Programming & CS"}
DEFAULT_CATEGORY = "Business & Soft Skills"


def get_category(skill):
    """Return the category name for a skill."""
    name = str(skill).casefold().strip()

    if name in EXACT_CATEGORY:
        return EXACT_CATEGORY[name]

    words = set(name.replace("/", " ").split())

    for category, keywords in CATEGORY_KEYWORDS:
        for keyword in keywords:
            if len(keyword) <= 3:
                if keyword in words:
                    return category
            elif keyword in name:
                return category

    return DEFAULT_CATEGORY


# ---------------------------------------------------------
# LEARNING DATA
# skill (lowercase): (level, hours, how to learn, mini project)
# level 1 = foundation, 2 = core tools, 3 = advanced
# ---------------------------------------------------------

LEARNING_DATA = {
    "python": (1, 40, "Python for Everybody (free) or the official Python tutorial; practise on HackerRank", "Automate a daily task, such as renaming files or scraping a web page"),
    "sql": (1, 25, "SQLBolt, Mode SQL tutorial and Kaggle Learn: Intro to SQL", "Design a small library database and answer 15 business questions with queries"),
    "excel": (1, 20, "Microsoft's Excel training videos, focusing on pivot tables and lookup functions", "Clean a messy sales sheet and build a pivot-table summary"),
    "statistics": (1, 30, "Khan Academy: Statistics and Probability", "Run a hypothesis test on a real dataset and explain the result in plain words"),
    "data cleaning": (1, 15, "Kaggle Learn: Data Cleaning", "Clean a dirty dataset and document each step you took"),
    "git": (1, 8, "Pro Git book (free) and GitHub Skills exercises", "Push three of your projects to GitHub with proper README files"),
    "linux": (1, 20, "Linux Journey and the OverTheWire Bandit game", "Set up a Linux VM and write three shell scripts"),
    "html": (1, 12, "MDN Learn Web Development", "Build a responsive personal portfolio page"),
    "css": (1, 15, "MDN CSS guides and Flexbox Froggy", "Make your portfolio responsive using flexbox and grid"),
    "javascript": (1, 40, "javascript.info and freeCodeCamp", "Build a to-do app that saves tasks in local storage"),
    "java": (1, 45, "MOOC.fi Java Programming or Oracle's Java tutorials", "Build a console banking app using classes and exceptions"),
    "oop": (1, 15, "Any Java or Python OOP tutorial", "Model a library system using inheritance and polymorphism"),
    "data structures and algorithms": (1, 60, "NeetCode roadmap and Harvard CS50", "Solve 50 problems across arrays, strings, trees and graphs"),
    "networking": (1, 25, "Cisco Networking Academy intro or Professor Messer's free videos", "Map a small network and capture traffic in Wireshark"),
    "software testing": (1, 15, "ISTQB Foundation syllabus (free)", "Write a test plan and 20 test cases for a sample app"),
    "jira": (1, 5, "Atlassian's free Jira tutorials", "Track one of your own projects on a Jira board"),
    "agile": (1, 8, "The Scrum Guide (free)", "Run a one-week sprint on a personal project"),
    "communication": (1, 10, "Practise short presentations and write project summaries", "Record a 2-minute walkthrough of your best project"),
    "project management": (1, 15, "Google Project Management Certificate (audit for free)", "Plan a small project with milestones and risks"),
    "figma": (1, 15, "Figma's official beginner tutorials", "Design a four-screen mobile app prototype"),
    "wireframing": (1, 8, "Figma or Balsamiq tutorials", "Wireframe the screens of an app you use every day"),
    "seo": (1, 15, "Google Search Central's SEO starter guide", "Audit a small website and list ten fixes"),
    "mysql": (1, 15, "MySQL official tutorial", "Create a schema with joins and indexes"),
    "pandas": (2, 20, "Kaggle Learn: Pandas and the official 10 minutes to pandas guide", "Analyse a Kaggle CSV and write up five findings"),
    "numpy": (2, 10, "NumPy official quickstart", "Re-implement mean, standard deviation and correlation with NumPy arrays"),
    "power bi": (2, 25, "Microsoft Learn: Power BI Data Analyst path (free)", "Build a two-page sales dashboard with slicers"),
    "tableau": (2, 25, "Tableau's free training videos and Tableau Public", "Publish a dashboard to Tableau Public from an open dataset"),
    "data visualization": (2, 15, "Matplotlib and Seaborn tutorials plus Storytelling with Data principles", "Turn one dataset into four clear charts with titles and takeaways"),
    "data analysis": (2, 25, "Kaggle Learn courses or the Google Data Analytics Certificate (audit for free)", "Do an end-to-end analysis: question, cleaning, charts and conclusions"),
    "dax": (2, 15, "SQLBI's DAX guide", "Write ten measures for your Power BI dashboard"),
    "power query": (2, 10, "Microsoft Learn Power Query documentation", "Clean and merge three data sources with Power Query"),
    "etl": (2, 20, "Introductory data engineering tutorials and dbt Learn", "Write a Python script that extracts, cleans and loads a CSV into SQLite"),
    "data modeling": (2, 15, "Kimball dimensional modelling basics", "Draw an ER diagram and star schema for a small retail business"),
    "data warehousing": (2, 20, "Kimball dimensional modelling basics", "Design a star schema for a sales database"),
    "postgresql": (2, 15, "PostgreSQL official tutorial", "Create a schema with constraints and use window functions"),
    "scikit-learn": (2, 20, "scikit-learn user guide and Kaggle Learn: Intro to ML", "Build a classification pipeline with a train/test split and cross-validation"),
    "prompt engineering": (2, 10, "Anthropic's prompt engineering guide", "Write and test ten prompts for one task and compare the outputs"),
    "docker": (2, 15, "Docker's official Get Started guide", "Containerise one of your apps and run it with docker compose"),
    "aws": (2, 35, "AWS Cloud Practitioner free training", "Host a static site on S3 and launch a small EC2 instance"),
    "azure": (2, 30, "Microsoft Learn AZ-900 path", "Deploy a web app to Azure App Service"),
    "ci/cd": (2, 12, "GitHub Actions documentation", "Add a workflow that runs your tests on every push"),
    "react": (2, 35, "The official React tutorial", "Build a notes or weather app with components and hooks"),
    "typescript": (2, 15, "The TypeScript Handbook", "Convert one JavaScript project to TypeScript"),
    "node.js": (2, 25, "Node.js official guides and The Odin Project", "Build a REST API with Express"),
    "rest api": (2, 15, "MDN HTTP guides and the Flask or FastAPI tutorial", "Build a small CRUD API and test it with Postman"),
    "spring boot": (2, 30, "Spring's official guides", "Build a REST service backed by a database"),
    "selenium": (2, 20, "Selenium documentation", "Automate login and search tests for a demo site"),
    "cybersecurity": (2, 30, "TryHackMe pre-security path", "Complete ten TryHackMe rooms and write a short report"),
    "ui design": (2, 20, "Refactoring UI principles and Figma community files", "Redesign one screen of an existing app"),
    "ux research": (2, 15, "Nielsen Norman Group articles and the Google UX Design Certificate (audit)", "Interview five users and write a findings summary"),
    "prototyping": (2, 10, "Figma prototyping tutorials", "Create a clickable prototype with transitions"),
    "google analytics": (2, 10, "Google Analytics Academy", "Set up GA4 on a demo site and read the reports"),
    "stakeholder management": (2, 10, "Business analysis articles and case studies", "Interview a friend about a problem and write a requirements summary"),
    "machine learning": (3, 50, "Andrew Ng's Machine Learning Specialization or Kaggle Learn: Intro to ML", "Train and compare three models on a Kaggle dataset and report the metrics"),
    "deep learning": (3, 50, "fast.ai Practical Deep Learning", "Train an image classifier and show its confusion matrix"),
    "tensorflow": (3, 25, "TensorFlow official tutorials", "Build a small neural network, then save and reload the model"),
    "pytorch": (3, 25, "PyTorch official tutorials", "Train a simple CNN on MNIST"),
    "feature engineering": (3, 15, "Kaggle Learn: Feature Engineering", "Improve a model's score by adding five engineered features"),
    "nlp": (3, 30, "The Hugging Face NLP course", "Build a sentiment or resume-text classifier"),
    "llms": (3, 20, "Provider API documentation and DeepLearning.AI short courses", "Build a small chatbot using an LLM API"),
    "rag": (3, 20, "LangChain or LlamaIndex tutorials", "Build a question-answering app over your own PDF notes"),
    "kubernetes": (3, 30, "Kubernetes official tutorials with Minikube", "Deploy a containerised app on a local cluster"),
    "apache spark": (3, 30, "Spark's quick start and Databricks Academy free courses", "Process a large CSV with PySpark"),
    "pyspark": (3, 25, "Databricks Academy free PySpark training", "Rewrite a pandas analysis in PySpark"),
    "airflow": (3, 20, "Apache Airflow tutorials", "Schedule a daily ETL job as a DAG"),
}

GENERIC_LEVEL = 2
GENERIC_HOURS = 15

PHASE_NAMES = {
    1: "Foundations",
    2: "Core tools",
    3: "Advanced and specialisation",
}


def learning_info(skill):
    """Return learning details for one skill (generic fallback if unknown)."""
    key = str(skill).casefold().strip()

    if key in LEARNING_DATA:
        level, hours, learn, project = LEARNING_DATA[key]
    else:
        level = GENERIC_LEVEL
        hours = GENERIC_HOURS
        learn = (
            f"Follow a beginner course on {skill} and read its "
            "official documentation"
        )
        project = (
            f"Build one small project that uses {skill} and add it "
            "to your resume"
        )

    return {
        "skill": str(skill),
        "level": level,
        "hours": hours,
        "learn": learn,
        "project": project,
    }


def build_roadmap(missing_skills, hours_per_week=10, hours_factor=1.0):
    """Turn missing skills into ordered phases with week estimates.

    hours_factor scales the starter hour estimates: 1.0 for a beginner,
    lower for someone who already has some exposure to the skills.
    """
    try:
        hours_per_week = max(1, int(hours_per_week))
    except (TypeError, ValueError):
        hours_per_week = 10

    try:
        hours_factor = min(1.5, max(0.2, float(hours_factor)))
    except (TypeError, ValueError):
        hours_factor = 1.0

    items = [
        (index, learning_info(skill))
        for index, skill in enumerate(missing_skills)
    ]

    for _, item in items:
        item["hours"] = max(2, round(item["hours"] * hours_factor))

    # Foundations first, then core tools, then advanced.
    # Within a level, keep the role's own skill order.
    items.sort(key=lambda pair: (pair[1]["level"], pair[0]))

    phases = []
    weeks_used = 0.0

    for level in (1, 2, 3):
        level_items = [item for _, item in items if item["level"] == level]

        if not level_items:
            continue

        phase_hours = sum(item["hours"] for item in level_items)
        phase_weeks = max(1, math.ceil(phase_hours / hours_per_week))

        start_week = int(weeks_used) + 1
        end_week = int(weeks_used) + phase_weeks
        weeks_used += phase_weeks

        phases.append({
            "title": f"Phase {len(phases) + 1}: {PHASE_NAMES[level]}",
            "weeks": (
                f"Week {start_week}"
                if start_week == end_week
                else f"Weeks {start_week}-{end_week}"
            ),
            "hours": phase_hours,
            "items": level_items,
        })

    total_hours = sum(phase["hours"] for phase in phases)

    return {
        "phases": phases,
        "total_hours": total_hours,
        "total_weeks": int(weeks_used),
        "hours_per_week": hours_per_week,
    }


def roadmap_to_text(roadmap):
    """Plain-text version of the roadmap for the downloadable report."""
    if not roadmap["phases"]:
        return ["No roadmap needed: all predefined skills were detected."]

    lines = [
        f"Estimated effort: about {roadmap['total_hours']} hours "
        f"({roadmap['total_weeks']} weeks at "
        f"{roadmap['hours_per_week']} hours per week)",
        "",
    ]

    for phase in roadmap["phases"]:
        lines.append(f"{phase['title']} ({phase['weeks']})")
        for item in phase["items"]:
            lines.append(f"- {item['skill']} (~{item['hours']} hrs)")
            lines.append(f"    Learn: {item['learn']}")
            lines.append(f"    Practise: {item['project']}")
        lines.append("")

    return lines
