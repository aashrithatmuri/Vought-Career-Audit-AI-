def optimize_learning_order(
    missing_skills,
    skill_difficulty
):
    """
    Sort skills by difficulty:
    Easy → Medium → Hard
    """

    difficulty_priority = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    optimized_skills = sorted(
        missing_skills,
        key=lambda skill: difficulty_priority.get(
            skill_difficulty.get(skill, "Medium"),
            2
        )
    )

    return optimized_skills