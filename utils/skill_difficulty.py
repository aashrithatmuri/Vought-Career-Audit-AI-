EASY_SKILLS = [
    "fastapi",
    "flask",
    "postgresql",
    "git"
]

MEDIUM_SKILLS = [
    "docker",
    "django",
    "react",
    "machine learning"
]

HARD_SKILLS = [
    "aws",
    "kubernetes",
    "deep learning",
    "tensorflow",
    "pytorch"
]


def classify_skill_difficulty(missing_skills):
    """
    Classify missing skills by difficulty
    """

    difficulty_map = {}

    for skill in missing_skills:

        if skill in EASY_SKILLS:
            difficulty_map[skill] = "Easy"

        elif skill in MEDIUM_SKILLS:
            difficulty_map[skill] = "Medium"

        elif skill in HARD_SKILLS:
            difficulty_map[skill] = "Hard"

        else:
            difficulty_map[skill] = "Medium"

    return difficulty_map