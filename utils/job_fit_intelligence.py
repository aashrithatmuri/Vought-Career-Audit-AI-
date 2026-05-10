from utils.llm_client import complete_json


def _fallback_job_fit(
    skill_analysis
):
    match_percentage = int(
        skill_analysis.get(
            "match_percentage",
            0
        )
    )

    if match_percentage >= 75:
        fit_level = "High"

    elif match_percentage >= 45:
        fit_level = "Medium"

    else:
        fit_level = "Low"

    missing_skills = skill_analysis.get(
        "priority_missing_skills"
    ) or skill_analysis.get(
        "missing_skills",
        []
    )

    return {
        "fit_level": fit_level,
        "confidence_score": match_percentage,
        "critical_gaps": missing_skills[:3],
        "short_term_fixable_gaps": missing_skills[3:6],
        "long_term_gaps": missing_skills[6:]
    }


def predict_job_fit(
    skill_analysis,
    resume_skills,
    jd_skills
):
    """
    Predict fit level and gap urgency using Groq intelligence.
    """

    fallback = _fallback_job_fit(
        skill_analysis
    )

    system_prompt = """
You are a technical hiring decision-support analyst.

Predict candidate fit for a role using skill evidence, missing skills, semantic
matches, and hiring-critical gap severity. Think like a recruiter deciding
whether to shortlist the candidate.

Rules:
- Return strict valid JSON only.
- Do not include markdown or prose outside JSON.
- Do not make employment decisions on protected or sensitive traits.
- Use only skill and role-relevance evidence.
- Critical gaps are gaps that can block shortlisting.
- Short-term fixable gaps are learnable or demonstrable within 2-4 weeks.
- Long-term gaps require deeper experience or project history.

JSON schema:
{
  "fit_level": "High/Medium/Low",
  "confidence_score": 0,
  "critical_gaps": [],
  "short_term_fixable_gaps": [],
  "long_term_gaps": []
}
"""

    user_prompt = f"""
Skill analysis:
{skill_analysis}

Resume skills:
{resume_skills}

Job-description skills:
{jd_skills}

Classify fit for a realistic hiring pipeline. Return only JSON.
"""

    result = complete_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=fallback,
        temperature=0.08,
        max_completion_tokens=850
    )

    fit_level = str(
        result.get(
            "fit_level",
            fallback["fit_level"]
        )
    ).title()

    if fit_level not in [
        "High",
        "Medium",
        "Low"
    ]:
        fit_level = fallback["fit_level"]

    result["fit_level"] = fit_level

    try:
        result["confidence_score"] = int(
            max(
                0,
                min(
                    100,
                    float(
                        result.get(
                            "confidence_score",
                            fallback["confidence_score"]
                        )
                    )
                )
            )
        )

    except (TypeError, ValueError):
        result["confidence_score"] = fallback["confidence_score"]

    for key in [
        "critical_gaps",
        "short_term_fixable_gaps",
        "long_term_gaps"
    ]:
        if not isinstance(
            result.get(
                key
            ),
            list
        ):
            result[key] = fallback[key]

    return result
