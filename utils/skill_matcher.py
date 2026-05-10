from utils.llm_client import complete_json


def _normalize_skills(
    skills
):
    normalized = []

    for skill in skills or []:
        if skill is None:
            continue

        cleaned = str(
            skill
        ).strip()

        if cleaned and cleaned not in normalized:
            normalized.append(
                cleaned
            )

    return normalized


def _fallback_match(
    resume_skills,
    jd_skills
):
    resume_normalized = _normalize_skills(
        resume_skills
    )
    jd_normalized = _normalize_skills(
        jd_skills
    )
    resume_lookup = {
        skill.lower(): skill
        for skill in resume_normalized
    }
    matched_skills = []
    missing_skills = []

    for skill in jd_normalized:
        if skill.lower() in resume_lookup:
            matched_skills.append(
                skill
            )

        else:
            missing_skills.append(
                skill
            )

    match_percentage = 0

    if jd_normalized:
        match_percentage = round(
            len(matched_skills) / len(jd_normalized) * 100
        )

    return {
        "match_percentage": int(match_percentage),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "semantic_matches": [],
        "priority_missing_skills": missing_skills[:5]
    }


def _coerce_result(
    result,
    fallback
):
    match_percentage = result.get(
        "match_percentage",
        fallback["match_percentage"]
    )

    try:
        match_percentage = int(
            round(
                float(match_percentage)
            )
        )

    except (TypeError, ValueError):
        match_percentage = fallback["match_percentage"]

    match_percentage = max(
        0,
        min(
            100,
            match_percentage
        )
    )

    coerced = {
        "match_percentage": match_percentage,
        "matched_skills": result.get(
            "matched_skills",
            fallback["matched_skills"]
        ),
        "missing_skills": result.get(
            "missing_skills",
            fallback["missing_skills"]
        ),
        "semantic_matches": result.get(
            "semantic_matches",
            fallback["semantic_matches"]
        ),
        "priority_missing_skills": result.get(
            "priority_missing_skills",
            fallback["priority_missing_skills"]
        )
    }

    for key in [
        "matched_skills",
        "missing_skills",
        "priority_missing_skills"
    ]:
        if not isinstance(
            coerced[key],
            list
        ):
            coerced[key] = fallback[key]

    if not isinstance(
        coerced["semantic_matches"],
        list
    ):
        coerced["semantic_matches"] = fallback["semantic_matches"]

    return coerced


def match_skills(
    resume_skills,
    jd_skills
):
    """
    Compare resume skills with job-description skills using Groq semantic analysis.
    """

    resume_skills = _normalize_skills(
        resume_skills
    )
    jd_skills = _normalize_skills(
        jd_skills
    )
    fallback = _fallback_match(
        resume_skills,
        jd_skills
    )

    if not jd_skills:
        return fallback

    system_prompt = """
You are a hiring-focused technical skill matching engine.

Think like a senior recruiter, hiring manager, and career strategist.
Your job is to compare candidate resume skills against job-description skills
using semantic equivalence, category relevance, and transferable skill value.

Rules:
- Return strict valid JSON only.
- Do not include markdown, comments, or prose outside JSON.
- Treat exact matches, close synonyms, framework equivalents, and category matches intelligently.
- Do not over-credit weak relevance. A transferable skill can be a semantic match only when it would reduce hiring risk.
- Missing skills should be job-description skills that the candidate does not sufficiently cover.
- Priority missing skills must be the missing skills most likely to affect shortlisting or interviews.
- Match percentage must be an integer from 0 to 100 based on hiring readiness, not raw overlap.

JSON schema:
{
  "match_percentage": 0,
  "matched_skills": ["job skill covered by resume"],
  "missing_skills": ["job skill not sufficiently covered"],
  "semantic_matches": [
    {
      "resume_skill": "candidate skill",
      "jd_skill": "job skill",
      "relationship": "exact/synonym/framework/category/transferable",
      "confidence": 0-100,
      "hiring_relevance": "why this reduces hiring risk"
    }
  ],
  "priority_missing_skills": ["highest-impact missing job skills"]
}
"""

    user_prompt = f"""
Resume skills:
{resume_skills}

Job-description skills:
{jd_skills}

Evaluate the candidate for a real hiring pipeline. Detect examples like:
- PyTorch can partially cover deep learning frameworks.
- FastAPI can transfer to backend API development.
- SQL can partially cover relational database work.
- AWS does not fully cover Kubernetes unless orchestration is explicit.

Return only the JSON object.
"""

    result = complete_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=fallback,
        temperature=0.05,
        max_completion_tokens=1100
    )

    return _coerce_result(
        result,
        fallback
    )
