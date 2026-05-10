ADJACENT_SKILLS = {
    "python": [
        "fastapi",
        "django",
        "flask",
        "machine learning"
    ],
    "sql": [
        "postgresql",
        "mysql"
    ],
    "flask": [
        "fastapi",
        "django"
    ],
    "machine learning": [
        "deep learning",
        "tensorflow",
        "pytorch"
    ],
    "docker": [
        "kubernetes"
    ]
}


def find_adjacent_skills(
    resume_skills,
    missing_skills
):
    """
    Find missing skills that are adjacent to current skills
    """

    adjacent_matches = {}

    for current_skill in resume_skills:

        if current_skill in ADJACENT_SKILLS:

            related_skills = ADJACENT_SKILLS[current_skill]

            for skill in missing_skills:

                if skill in related_skills:

                    adjacent_matches[skill] = current_skill

    return adjacent_matches