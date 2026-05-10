def analyze_resume_strengths(
    resume_skills,
    jd_skills
):

    strengths = []

    overlap = set(
        resume_skills
    ).intersection(
        set(jd_skills)
    )

    for skill in overlap:

        strengths.append(
            {
                "skill": skill,
                "advantage": "Relevant for target role"
            }
        )

    return strengths