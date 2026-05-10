from utils.llm_client import complete_chat


def _fallback_roadmap(
    missing_skills
):
    if not missing_skills:
        return """
## Phase 1: Foundation
No critical missing skills were detected. Consolidate fundamentals by reviewing the role's core tools and terminology.

## Phase 2: Intermediate
Build one small proof-of-work project that mirrors the target role's day-to-day responsibilities.

## Phase 3: Advanced
Add measurable outcomes, testing, deployment, documentation, or business context to show professional maturity.

## Phase 4: Job-readiness
Convert the project into resume bullets, interview stories, and a concise portfolio walkthrough.
"""

    skill_lines = "\n".join(
        f"- {skill}: learn fundamentals, build one practical artifact, then prepare interview proof."
        for skill in missing_skills
    )

    return f"""
## Phase 1: Foundation
Build the concepts needed to understand the missing skill set.

{skill_lines}

## Phase 2: Intermediate
Connect each skill to a small project that resembles the target role.

## Phase 3: Advanced
Add production details: documentation, testing, deployment, performance, and trade-off explanations.

## Phase 4: Job-readiness
Create resume bullets and interview stories for each skill so the learning is visible to recruiters.
"""


def generate_learning_roadmap(
    missing_skills
):
    """
    Generate a staged learning roadmap for missing skills.
    """

    fallback = _fallback_roadmap(
        missing_skills
    )

    system_prompt = """
You are a senior career strategist and technical hiring manager.

Generate a practical learning roadmap that helps a candidate become more
employable for a specific target role. Your advice must be concrete,
hiring-focused, and action-oriented.

Rules:
- Return structured markdown.
- Do not ask questions.
- Assume beginner-to-intermediate ability unless the skill implies advanced work.
- Prioritize employability, portfolio proof, and interview readiness.
- Avoid generic advice like "learn the basics" unless you specify what basics matter.
- Explain dependencies and sequencing clearly.
"""

    user_prompt = f"""
Missing or weak skills:
{missing_skills}

Create this exact structure:

## Phase 1: Foundation
For each foundational skill:
- Skill:
- Why it matters:
- Dependencies:
- Estimated time:
- Practical milestone:

## Phase 2: Intermediate
For each intermediate skill:
- Skill:
- Why it matters:
- Dependencies:
- Estimated time:
- Practical milestone:

## Phase 3: Advanced
For advanced or specialization skills:
- Skill:
- Why it matters:
- Dependencies:
- Estimated time:
- Practical milestone:

## Phase 4: Job-readiness
Include:
- Portfolio project sequence
- Resume bullet strategy
- Interview preparation priorities
- What proof would convince a hiring manager

Keep it concise but high-signal.
"""

    result = complete_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fallback=fallback,
        temperature=0.25,
        max_completion_tokens=1400
    )

    return result.content
