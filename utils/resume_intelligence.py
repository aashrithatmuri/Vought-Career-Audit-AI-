from utils.llm_client import complete_json


def _fallback_resume_intelligence(
    resume_skills
):
    score = 50

    if len(
        resume_skills or []
    ) >= 8:
        score = 70

    elif len(
        resume_skills or []
    ) >= 4:
        score = 60

    return {
        "strengths": [
            "Resume contains identifiable technical skills."
        ],
        "weaknesses": [
            "Depth, business impact, and project evidence need manual review."
        ],
        "high_signal_skills": list(
            resume_skills or []
        )[:8],
        "low_signal_sections": [
            "Sections without quantified outcomes or concrete tools may be low signal."
        ],
        "resume_score": score
    }


def analyze_resume_intelligence(
    resume_text,
    resume_skills,
    jd_skills=None
):
    """
    Analyze resume signal quality and market relevance.
    """

    fallback = _fallback_resume_intelligence(
        resume_skills
    )

    system_prompt = """
You are a senior resume reviewer for technical hiring.

Evaluate resume signal strength from the perspective of recruiters and hiring
managers. Focus on technical depth, market relevance, proof of execution, and
whether the resume is likely to survive screening.

Rules:
- Return strict valid JSON only.
- Do not include markdown or prose outside JSON.
- Do not infer personal traits, protected attributes, or unverifiable claims.
- Penalize vague skills without project, metric, or responsibility evidence.
- Reward concrete tools, shipped projects, quantified outcomes, and role-relevant depth.

JSON schema:
{
  "strengths": [],
  "weaknesses": [],
  "high_signal_skills": [],
  "low_signal_sections": [],
  "resume_score": 0
}
"""

    user_prompt = f"""
Resume text:
{resume_text[:7000]}

Extracted resume skills:
{resume_skills}

Target job skills:
{jd_skills or []}

Analyze:
- technical depth
- market relevance
- signal strength
- whether skills are backed by evidence
- what sections look generic or weak

Return only the JSON object.
"""

    result = complete_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=fallback,
        temperature=0.08,
        max_completion_tokens=900
    )

    try:
        result["resume_score"] = int(
            max(
                0,
                min(
                    100,
                    float(
                        result.get(
                            "resume_score",
                            fallback["resume_score"]
                        )
                    )
                )
            )
        )

    except (TypeError, ValueError):
        result["resume_score"] = fallback["resume_score"]

    for key in [
        "strengths",
        "weaknesses",
        "high_signal_skills",
        "low_signal_sections"
    ]:
        if not isinstance(
            result.get(
                key
            ),
            list
        ):
            result[key] = fallback[key]

    return result
