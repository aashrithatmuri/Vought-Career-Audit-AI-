SKILL_TIME_ESTIMATES = {
    "python": "2 weeks",
    "sql": "2 weeks",
    "docker": "1 week",
    "aws": "3 weeks",
    "fastapi": "1 week",
    "django": "2 weeks",
    "flask": "1 week",
    "machine learning": "4 weeks",
    "deep learning": "6 weeks",
    "tensorflow": "3 weeks",
    "pytorch": "3 weeks",
    "postgresql": "2 weeks",
    "react": "3 weeks",
    "javascript": "3 weeks"
}


def estimate_learning_time(missing_skills):
    """
    Estimate learning time for missing skills
    """

    estimates = {}

    for skill in missing_skills:
        if skill in SKILL_TIME_ESTIMATES:
            estimates[skill] = SKILL_TIME_ESTIMATES[skill]
        else:
            estimates[skill] = "2 weeks"

    return estimates