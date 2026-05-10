FORMAT_MAP = {
    "ai": "AI",
    "api": "API",
    "apis": "APIs",
    "aws": "AWS",
    "azure": "Azure",
    "ci/cd": "CI/CD",
    "css": "CSS",
    "docker": "Docker",
    "django": "Django",
    "excel": "Excel",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "git": "Git",
    "github": "GitHub",
    "html": "HTML",
    "javascript": "JavaScript",
    "kubernetes": "Kubernetes",
    "llm": "LLM",
    "llms": "LLMs",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "mongodb": "MongoDB",
    "node.js": "Node.js",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "postgresql": "PostgreSQL",
    "power bi": "Power BI",
    "pytorch": "PyTorch",
    "python": "Python",
    "react": "React",
    "scikit-learn": "scikit-learn",
    "sql": "SQL",
    "tableau": "Tableau",
    "tensorflow": "TensorFlow"
}


def format_skill(
    skill
):
    if skill is None:
        return ""

    raw = str(
        skill
    ).strip()

    if not raw:
        return ""

    lookup = raw.lower()

    if lookup in FORMAT_MAP:
        return FORMAT_MAP[lookup]

    return raw.title()


def format_skills(
    skills
):
    formatted = []

    for skill in skills or []:
        display_skill = format_skill(
            skill
        )

        if display_skill and display_skill not in formatted:
            formatted.append(
                display_skill
            )

    return formatted


def format_skill_map(
    skill_map
):
    formatted = {}

    for key, value in (
        skill_map or {}
    ).items():
        formatted_key = format_skill(
            key
        )

        if isinstance(
            value,
            list
        ):
            formatted[formatted_key] = format_skills(
                value
            )

        else:
            formatted[formatted_key] = value

    return formatted
