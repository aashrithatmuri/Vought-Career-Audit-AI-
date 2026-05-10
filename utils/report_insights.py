from utils.llm_client import complete_chat


def _fallback_insights(
    match_percentage,
    missing_skills,
    adjacent_skills
):
    missing_text = ", ".join(
        missing_skills
    ) or "No major gaps detected"

    return f"""
## Candidate Market Readiness
Current role alignment is **{match_percentage}%**. The profile has useful signal, but hiring readiness depends on closing the most visible gaps.

## Hiring Risk Assessment
The main risk is whether the candidate can prove hands-on capability in the required stack quickly enough for interview evaluation.

## Skill Gap Severity
Priority gaps: {missing_text}

## Strategic Learning Priorities
Focus first on gaps that appear directly in the job description and can be converted into portfolio proof within 2-4 weeks.

## Competitive Positioning
Adjacent strengths can help the candidate tell a transition story, especially where existing skills map to the target stack.

## Estimated Interview Readiness
The candidate should be interview-ready after building project evidence for the priority gaps and preparing concise trade-off explanations.

## Adjacent Skill Leverage
{adjacent_skills}
"""


def generate_report_insights(
    match_percentage,
    missing_skills,
    adjacent_skills
):
    fallback = _fallback_insights(
        match_percentage,
        missing_skills,
        adjacent_skills
    )

    system_prompt = """
You are a career intelligence analyst.

Think like a recruiter, hiring manager, and employability strategist. Produce
strategic insight that helps a candidate understand whether they can compete
for a role, what may block shortlisting, and what actions would improve their
market position fastest.

Rules:
- Return structured markdown.
- Be specific, not motivational filler.
- Tie recommendations to hiring outcomes.
- Prioritize gaps by severity and shortlisting impact.
- Use measured language. Do not invent credentials or experience.
"""

    user_prompt = f"""
Inputs:
- Career match percentage: {match_percentage}
- Missing skills: {missing_skills}
- Adjacent skill leverage: {adjacent_skills}

Generate these sections:

## Candidate Market Readiness
Assess current competitiveness for the target role.

## Hiring Risk Assessment
Identify what could prevent shortlisting or offer conversion.

## Skill Gap Severity
Classify gaps as critical, moderate, or low impact.

## Strategic Learning Priorities
Give the highest-return learning actions in order.

## Competitive Positioning
Explain how the candidate should position existing strengths.

## Estimated Interview Readiness
Estimate readiness now, after 2 weeks, and after 4-6 weeks of focused work.

## Recruiter-Facing Narrative
Write a concise positioning narrative the candidate could use in outreach.
"""

    result = complete_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=fallback,
        temperature=0.22,
        max_completion_tokens=1300
    )

    return result.content
