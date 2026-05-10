import html

import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.skill_matcher import match_skills
from utils.ai_analyzer import generate_learning_roadmap
from utils.resource_recommender import recommend_resources
from utils.adjacent_skill_mapper import find_adjacent_skills
from utils.time_estimator import estimate_learning_time
from utils.skill_difficulty import classify_skill_difficulty
from utils.roadmap_optimizer import optimize_learning_order
from utils.report_generator import generate_report
from utils.report_insights import generate_report_insights
from utils.skill_formatter import format_skill, format_skills, format_skill_map
from utils.resume_strength_analyzer import analyze_resume_strengths
from utils.llm_client import get_usage_status
from utils.resume_intelligence import analyze_resume_intelligence
from utils.job_fit_intelligence import predict_job_fit

from utils.chart_generator import (
    generate_match_chart,
    generate_difficulty_chart,
    generate_time_chart,
    generate_coverage_chart
)


def render_list_panel(
    title,
    items,
    empty_text="No items detected."
):
    items = [
        format_skill(item) if isinstance(
            item,
            str
        ) else str(
            item
        )
        for item in items or []
    ]

    if not items:
        items = [
            empty_text
        ]

    html_items = "".join(
        f"<li>{html.escape(item)}</li>"
        for item in items
    )

    st.markdown(
        (
            "<div class=\"insight-panel\">"
            f"<div class=\"insight-title\">{html.escape(title)}</div>"
            f"<ul class=\"insight-list\">{html_items}</ul>"
            "</div>"
        ),
        unsafe_allow_html=True
    )


def get_homelander_reaction(
    match_percentage
):
    if match_percentage <= 30:
        return {
            "message": "You disappoint me.",
            "image": "https://comicbook.com/wp-content/uploads/sites/4/2026/04/Homelander-Antony-Starr-looking-sad-in-The-Boys-Season-5.jpg?w=1024"
        }

    if match_percentage <= 50:
        return {
            "message": "I expected better.",
            "image": "https://comicbook.com/wp-content/uploads/sites/4/2026/04/Homelander-Antony-Starr-looking-sad-in-The-Boys-Season-5.jpg?w=1024"
        }

    if match_percentage <= 70:
        return {
            "message": "Not bad. But not enough.",
            "image": "https://s.yimg.com/ny/api/res/1.2/Ny.HIxMFY1qWXl_bp.NdeQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTIwNDg7aD0xMTUyO2NmPXdlYnA-/https://media.zenfs.com/en/superherohype_979/5678ed4703822f234173f1ca03701238"
        }

    if match_percentage <= 85:
        return {
            "message": "Now that's more like it.",
            "image": "https://static0.cbrimages.com/wordpress/wp-content/uploads/2022/05/The-Boys-Season-3-Trailer-Homelander-Header.jpg?q=50&fit=crop&w=1232&h=693&dpr=1.5"
        }

    return {
        "message": "You belong with the strong.",
        "image": "https://static0.cbrimages.com/wordpress/wp-content/uploads/2022/05/The-Boys-Season-3-Trailer-Homelander-Header.jpg?q=50&fit=crop&w=1232&h=693&dpr=1.5"
    }


def render_homelander_card(
    match_percentage
):
    reaction = get_homelander_reaction(
        match_percentage
    )

    st.markdown(
        (
            "<div class=\"homelander-card\">"
            f"<img src=\"{html.escape(reaction['image'])}\" alt=\"Homelander reaction\" />"
            "<div class=\"homelander-copy\">"
            "<div class=\"panel-kicker\">Homelander Says</div>"
            f"<div class=\"homelander-quote\">{html.escape(reaction['message'])}</div>"
            f"<div class=\"homelander-score\">Career Match: {match_percentage}%</div>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True
    )


def render_gap_panels(
    job_fit_intelligence
):
    columns = st.columns(3)
    sections = [
        (
            "Critical Gaps",
            job_fit_intelligence.get(
                "critical_gaps",
                []
            )
        ),
        (
            "Short-Term Fixable",
            job_fit_intelligence.get(
                "short_term_fixable_gaps",
                []
            )
        ),
        (
            "Long-Term Gaps",
            job_fit_intelligence.get(
                "long_term_gaps",
                []
            )
        )
    ]

    for column, (
        title,
        items
    ) in zip(
        columns,
        sections
    ):
        with column:
            render_list_panel(
                title,
                items
            )


def render_resume_intelligence(
    resume_intelligence
):
    left, right = st.columns(2)

    with left:
        render_list_panel(
            "Strengths",
            resume_intelligence.get(
                "strengths",
                []
            )
        )
        render_list_panel(
            "High-Signal Skills",
            resume_intelligence.get(
                "high_signal_skills",
                []
            )
        )

    with right:
        render_list_panel(
            "Weaknesses",
            resume_intelligence.get(
                "weaknesses",
                []
            )
        )
        render_list_panel(
            "Low-Signal Sections",
            resume_intelligence.get(
                "low_signal_sections",
                []
            )
        )


def render_adjacent_skills(
    adjacent_skills
):
    formatted_map = format_skill_map(
        adjacent_skills
    )

    if not formatted_map:
        render_list_panel(
            "Adjacent Skill Leverage",
            [],
            "No adjacent leverage detected."
        )
        return

    cards = []

    for source_skill, mapped_skills in formatted_map.items():
        mapped_text = ", ".join(
            mapped_skills
        ) if isinstance(
            mapped_skills,
            list
        ) else str(
            mapped_skills
        )

        cards.append(
            (
                "<div class=\"transfer-card\">"
                f"<div class=\"transfer-source\">{html.escape(source_skill)}</div>"
                "<div class=\"transfer-arrow\">can support</div>"
                f"<div class=\"transfer-target\">{html.escape(mapped_text)}</div>"
                "</div>"
            )
        )

    st.markdown(
        f"<div class=\"transfer-grid\">{''.join(cards)}</div>",
        unsafe_allow_html=True
    )


def run_career_analysis(
    resume_text,
    job_description
):
    resume_skills = extract_skills(
        resume_text
    )

    jd_skills = extract_skills(
        job_description
    )

    skill_analysis = match_skills(
        resume_skills,
        jd_skills
    )

    priority_missing_skills = skill_analysis.get(
        "priority_missing_skills"
    ) or skill_analysis["missing_skills"]

    job_fit_intelligence = predict_job_fit(
        skill_analysis,
        resume_skills,
        jd_skills
    )

    role_fit = {
        "fit": job_fit_intelligence["fit_level"],
        "verdict": (
            f"{job_fit_intelligence['fit_level']} fit with "
            f"{job_fit_intelligence['confidence_score']}% confidence. "
            f"Critical gaps: {', '.join(format_skills(job_fit_intelligence['critical_gaps'])) or 'None detected'}."
        )
    }

    resume_intelligence = analyze_resume_intelligence(
        resume_text,
        resume_skills,
        jd_skills
    )

    resume_strengths = analyze_resume_strengths(
        resume_skills,
        jd_skills
    )

    adjacent_skills = find_adjacent_skills(
        resume_skills,
        skill_analysis["missing_skills"]
    )

    difficulty_map = classify_skill_difficulty(
        skill_analysis["missing_skills"]
    )

    time_estimates = estimate_learning_time(
        skill_analysis["missing_skills"]
    )

    optimized_skills = optimize_learning_order(
        priority_missing_skills,
        difficulty_map
    )

    learning_roadmap = generate_learning_roadmap(
        format_skills(
            optimized_skills
        )
    )

    ai_summary = generate_report_insights(
        skill_analysis["match_percentage"],
        format_skills(
            priority_missing_skills
        ),
        format_skill_map(
            adjacent_skills
        )
    )

    resources = recommend_resources(
        priority_missing_skills
    )

    charts = {
        "match": generate_match_chart(
            format_skills(
                skill_analysis["matched_skills"]
            ),
            format_skills(
                skill_analysis["missing_skills"]
            )
        ),
        "difficulty": generate_difficulty_chart(
            {
                format_skill(skill): level
                for skill, level in difficulty_map.items()
            }
        ),
        "time": generate_time_chart(
            {
                format_skill(skill): estimate
                for skill, estimate in time_estimates.items()
            }
        ),
        "coverage": generate_coverage_chart(
            resume_skills,
            jd_skills
        )
    }

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "skill_analysis": skill_analysis,
        "priority_missing_skills": priority_missing_skills,
        "job_fit_intelligence": job_fit_intelligence,
        "role_fit": role_fit,
        "resume_intelligence": resume_intelligence,
        "resume_strengths": resume_strengths,
        "adjacent_skills": adjacent_skills,
        "difficulty_map": difficulty_map,
        "time_estimates": time_estimates,
        "learning_roadmap": learning_roadmap,
        "ai_summary": ai_summary,
        "resources": resources,
        "charts": charts
    }

# PAGE CONFIG
st.set_page_config(
    page_title="Vought Career Audit AI",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# FULL UI STYLING
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
    --vought-navy: #07111f;
    --vought-blue: #0f3b78;
    --vought-red: #b31324;
    --vought-red-bright: #e11d2f;
    --vought-gold: #d6a94f;
    --vought-ink: #0b1220;
    --vought-paper: #f8fafc;
    --vought-muted: #aeb8c7;
    --vought-line: rgba(255, 255, 255, 0.14);
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        linear-gradient(100deg, rgba(7, 17, 31, 0.96) 0%, rgba(7, 17, 31, 0.84) 48%, rgba(108, 12, 24, 0.72) 100%),
        radial-gradient(circle at 78% 4%, rgba(214, 169, 79, 0.22), transparent 28%),
        url("https://images5.alphacoders.com/140/1403600.jpg");
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
#MainMenu,
footer {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding: 2rem 1.4rem 4rem;
}

.vought-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.1rem;
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-mark {
    display: grid;
    place-items: center;
    width: 46px;
    height: 46px;
    border: 1px solid rgba(214, 169, 79, 0.72);
    background: linear-gradient(145deg, rgba(177, 19, 36, 0.96), rgba(13, 50, 101, 0.96));
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: 30px;
    font-weight: 700;
    line-height: 1;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.32);
}

.brand-kicker,
.eyebrow,
.panel-kicker,
.kpi-label {
    color: var(--vought-gold);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08rem;
    text-transform: uppercase;
}

.brand-name {
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.04rem;
    line-height: 1.05;
}

.clearance-pill {
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: rgba(255, 255, 255, 0.08);
    color: #edf2f8;
    padding: 0.55rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
}

.hero-panel {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--vought-line);
    border-radius: 8px;
    background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.13), rgba(255, 255, 255, 0.04)),
        linear-gradient(90deg, rgba(11, 18, 32, 0.84), rgba(11, 18, 32, 0.46));
    box-shadow: 0 28px 70px rgba(0, 0, 0, 0.35);
    padding: clamp(1.25rem, 4vw, 2.15rem);
    margin-bottom: 1.5rem;
}

.hero-panel:before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, transparent 0 68%, rgba(214, 169, 79, 0.22) 68% 69%, transparent 69%),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0 1px, transparent 1px 72px);
    pointer-events: none;
}

.hero-content {
    position: relative;
    max-width: 820px;
}

.hero-title {
    margin: 0.35rem 0 0;
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: clamp(3rem, 8vw, 5.8rem);
    font-weight: 700;
    letter-spacing: 0;
    line-height: 0.92;
    text-transform: uppercase;
}

.hero-subtitle {
    max-width: 760px;
    margin-top: 1rem;
    color: #dbe5f3;
    font-size: 1.08rem;
    line-height: 1.65;
}

.hero-stripe {
    width: min(420px, 70vw);
    height: 5px;
    margin-top: 1.25rem;
    background: linear-gradient(90deg, var(--vought-red-bright), white 46%, var(--vought-blue));
}

.input-panel,
.result-panel {
    border: 1px solid var(--vought-line);
    border-radius: 8px;
    background: rgba(8, 15, 27, 0.76);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
    padding: 1.1rem;
}

.section-title {
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0;
    margin: 0.12rem 0 0.9rem;
    text-transform: uppercase;
}

label,
[data-testid="stFileUploader"] label {
    color: #e6edf7 !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.06rem !important;
    text-transform: uppercase !important;
}

[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: rgba(248, 250, 252, 0.96) !important;
    color: var(--vought-ink) !important;
    border: 1px solid rgba(214, 169, 79, 0.46) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.75) !important;
    font-size: 0.95rem !important;
    line-height: 1.65 !important;
}

[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: var(--vought-gold) !important;
    box-shadow: 0 0 0 3px rgba(214, 169, 79, 0.2) !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(11, 18, 32, 0.48) !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.055) !important;
    border: 1px solid rgba(214, 169, 79, 0.38) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}

[data-testid="stFileUploaderDropzone"] {
    min-height: 188px;
    align-items: center;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(232, 237, 246, 0.96)) !important;
    border: 1px dashed rgba(15, 59, 120, 0.5) !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small {
    color: #1f2937 !important;
    font-weight: 700 !important;
}

[data-testid="stFileUploader"] button,
.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] a {
    border-radius: 8px !important;
    font-weight: 800 !important;
    letter-spacing: 0.03rem !important;
    text-transform: uppercase !important;
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

[data-testid="stFileUploader"] button {
    background: var(--vought-blue) !important;
    color: white !important;
    border: 0 !important;
}

.stButton > button {
    width: 100%;
    min-height: 3.2rem;
    background: linear-gradient(90deg, var(--vought-red), var(--vought-red-bright)) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    box-shadow: 0 14px 30px rgba(177, 19, 36, 0.35) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    border-color: rgba(214, 169, 79, 0.72) !important;
    box-shadow: 0 16px 34px rgba(0, 0, 0, 0.28) !important;
    transform: translateY(-1px);
}

.stButton > button:disabled {
    background: rgba(148, 163, 184, 0.28) !important;
    color: rgba(255, 255, 255, 0.58) !important;
    box-shadow: none !important;
}

.stDownloadButton > button {
    width: 100%;
    background: linear-gradient(90deg, var(--vought-gold), #f1c96b) !important;
    color: #111827 !important;
    border: 0 !important;
}

[data-testid="stLinkButton"] a {
    width: 100% !important;
    display: inline-block !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    color: #f8fafc !important;
    padding: 0.68rem 0.8rem !important;
    text-align: center !important;
    text-decoration: none !important;
}

[data-testid="stLinkButton"] a:hover {
    background: rgba(15, 59, 120, 0.74) !important;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 0.35rem 0 1.25rem;
}

.kpi-card {
    min-height: 128px;
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-left: 4px solid var(--vought-red-bright);
    border-radius: 8px;
    background: linear-gradient(155deg, rgba(255, 255, 255, 0.13), rgba(255, 255, 255, 0.045));
    padding: 1rem;
}

.kpi-value {
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    line-height: 1;
    margin-top: 0.5rem;
}

.kpi-note {
    margin-top: 0.6rem;
    color: var(--vought-muted);
    font-size: 0.82rem;
}

.analysis-card {
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.07);
    padding: 1rem 1.05rem;
    margin: 0.75rem 0;
}

.homelander-card {
    display: grid;
    grid-template-columns: minmax(260px, 42%) minmax(0, 1fr);
    overflow: hidden;
    border: 1px solid rgba(214, 169, 79, 0.38);
    border-radius: 8px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.045));
    box-shadow: 0 18px 44px rgba(0, 0, 0, 0.26);
    margin: 0.75rem 0 1.15rem;
}

.homelander-card img {
    width: 100%;
    height: 235px;
    object-fit: cover;
    object-position: center;
    display: block;
}

.homelander-copy {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 235px;
    padding: 1.2rem 1.35rem;
}

.homelander-quote {
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: clamp(1.8rem, 4vw, 3.1rem);
    font-weight: 700;
    line-height: 1.05;
    margin-top: 0.45rem;
}

.homelander-score {
    color: var(--vought-muted);
    font-weight: 800;
    margin-top: 0.7rem;
    text-transform: uppercase;
}

.insight-panel {
    min-height: 100%;
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.075);
    padding: 0.95rem 1rem;
    margin: 0.55rem 0;
}

.insight-title {
    color: var(--vought-gold);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.07rem;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}

.insight-list {
    margin: 0;
    padding-left: 1.05rem;
}

.insight-list li {
    color: #eef4ff;
    margin: 0.36rem 0;
    line-height: 1.45;
}

.transfer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 0.75rem;
    margin: 0.5rem 0 1rem;
}

.transfer-card {
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-left: 3px solid var(--vought-gold);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.075);
    padding: 0.85rem 0.95rem;
}

.transfer-source,
.transfer-target {
    color: white;
    font-weight: 800;
}

.transfer-arrow {
    color: var(--vought-muted);
    font-size: 0.78rem;
    margin: 0.2rem 0;
    text-transform: uppercase;
}

.quota-card {
    border: 1px solid rgba(214, 169, 79, 0.34);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.06);
    padding: 0.9rem 1rem;
    margin: 0.2rem 0 1rem;
}

.quota-line {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.2rem;
    margin-top: 0.35rem;
    color: #dbe5f3;
    font-size: 0.9rem;
}

.quota-line strong {
    color: white;
}

[data-testid="stExpander"] details {
    background: rgba(8, 15, 27, 0.72) !important;
}

[data-testid="stExpander"] summary {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #eef4ff !important;
    font-weight: 800 !important;
}

[data-testid="stExpander"] textarea {
    background: rgba(248, 250, 252, 0.98) !important;
    color: var(--vought-ink) !important;
}

[data-testid="stExpander"] label {
    color: var(--vought-gold) !important;
}

.stJson,
[data-testid="stJson"] {
    display: none;
}

.resource-heading {
    color: white;
    font-family: 'Oswald', sans-serif;
    font-size: 1.2rem;
    margin: 1rem 0 0.4rem;
    text-transform: uppercase;
}

.creator-credit {
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    color: rgba(238, 244, 255, 0.72);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04rem;
    margin-top: 2.2rem;
    padding-top: 1rem;
    text-align: center;
    text-transform: uppercase;
}

button[data-baseweb="tab"] {
    color: #dbe5f3 !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: white !important;
    border-bottom-color: var(--vought-gold) !important;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 8px !important;
    background: rgba(255, 255, 255, 0.055) !important;
}

details summary,
h1, h2, h3, h4, h5, h6,
p, li, div {
    color: #eef4ff;
}

[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid rgba(214, 169, 79, 0.34) !important;
}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] {
    gap: 0.85rem;
}

@media (max-width: 900px) {
    .vought-topbar {
        align-items: flex-start;
        flex-direction: column;
    }

    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }

    .hero-panel {
        padding: 1rem;
    }

    .kpi-grid {
        grid-template-columns: 1fr;
    }

    .homelander-card {
        grid-template-columns: 1fr;
    }

    .homelander-card img,
    .homelander-copy {
        min-height: 0;
        height: 210px;
    }
}

</style>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="vought-topbar">
    <div class="brand-lockup">
        <div class="brand-mark">V</div>
        <div>
            <div class="brand-kicker">Vought Analytics Bureau</div>
            <div class="brand-name">Career Audit AI</div>
        </div>
    </div>
    <div class="clearance-pill">Talent Intelligence Console</div>
</div>

<section class="hero-panel">
    <div class="hero-content">
        <div class="eyebrow">Vought-Grade Skill Intelligence</div>
        <h1 class="hero-title">Career Audit AI</h1>
        <div class="hero-subtitle">
            Identify capability gaps, measure employability readiness,
            and build strategic learning pathways with executive clarity.
        </div>
        <div class="hero-stripe"></div>
    </div>
</section>
""", unsafe_allow_html=True)

# INPUTS
input_left, input_right = st.columns(
    [1.35, 0.85],
    gap="large"
)

with input_left:

    st.markdown(
        """
        <div class="input-panel">
            <div class="panel-kicker">Target Role Dossier</div>
            <div class="section-title">Job Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=260,
        placeholder="Paste the full job description here..."
    )

with input_right:

    st.markdown(
        """
        <div class="input-panel">
            <div class="panel-kicker">Candidate File</div>
            <div class="section-title">Resume Upload</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_resume = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"]
    )

analyze_ready = bool(
    uploaded_resume and job_description.strip()
)

analyze_requested = st.button(
    "Analyze Career Profile",
    disabled=not analyze_ready
)

# MAIN
if uploaded_resume:

    resume_text = extract_text_from_pdf(
        uploaded_resume
    )
    analysis_signature = (
        uploaded_resume.name,
        len(
            resume_text
        ),
        job_description.strip()
    )

    if analyze_requested:

        with st.spinner(
            "Building Career Intelligence..."
        ):
            st.session_state["analysis_result"] = run_career_analysis(
                resume_text,
                job_description
            )
            st.session_state["analysis_signature"] = analysis_signature

        st.rerun()

usage_status = get_usage_status()
capacity_used_percent = round(
    max(
        usage_status["requests_used_today"] / usage_status["daily_request_cap"],
        usage_status["tokens_used_today"] / usage_status["daily_token_cap"]
    ) * 100,
    1
)

st.markdown(
    f"""
    <div class="quota-card">
        <div class="panel-kicker">Vought Daily Intelligence Capacity</div>
        <div class="quota-line">
            <span><strong>{usage_status["estimated_analyses_left_today"]}</strong> estimated full analyses left today</span>
            <span><strong>{capacity_used_percent}%</strong> capacity used</span>
            <span><strong>{usage_status["requests_left_today"]}</strong> intelligence actions left</span>
            <span><strong>{usage_status["tokens_left_today"]}</strong> analysis credits left</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if usage_status["is_daily_cap_reached"]:
    st.error(
        "Today's intelligence capacity has been reached. The app will use structured fallback analysis until the daily counter resets."
    )

elif usage_status["is_minute_cap_reached"]:
    st.warning(
        "The intelligence console is cooling down for a moment. Wait briefly before running another full analysis."
    )

st.markdown("<br>", unsafe_allow_html=True)

if uploaded_resume:

    with st.expander(
        "VIEW EXTRACTED RESUME"
    ):
        st.text_area(
            "Resume Text",
            resume_text,
            height=220,
            key="resume_text_preview"
        )

    has_current_analysis = (
        st.session_state.get(
            "analysis_signature"
        ) == analysis_signature
        and "analysis_result" in st.session_state
    )

    if has_current_analysis:

        result = st.session_state["analysis_result"]
        resume_skills = result["resume_skills"]
        jd_skills = result["jd_skills"]
        skill_analysis = result["skill_analysis"]
        priority_missing_skills = result["priority_missing_skills"]
        job_fit_intelligence = result["job_fit_intelligence"]
        role_fit = result["role_fit"]
        resume_intelligence = result["resume_intelligence"]
        resume_strengths = result["resume_strengths"]
        adjacent_skills = result["adjacent_skills"]
        difficulty_map = result["difficulty_map"]
        time_estimates = result["time_estimates"]
        learning_roadmap = result["learning_roadmap"]
        ai_summary = result["ai_summary"]
        resources = result["resources"]
        chart1 = result["charts"]["match"]
        chart2 = result["charts"]["difficulty"]
        chart3 = result["charts"]["time"]
        chart4 = result["charts"]["coverage"]

        tabs = st.tabs([
            "Dashboard",
            "AI Summary",
            "Resources",
            "Report"
        ])

        # DASHBOARD
        with tabs[0]:

            st.markdown(
                f"""
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-label">Career Match</div>
                        <div class="kpi-value">{skill_analysis['match_percentage']}%</div>
                        <div class="kpi-note">Skill alignment score</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Matched Skills</div>
                        <div class="kpi-value">{len(skill_analysis["matched_skills"])}</div>
                        <div class="kpi-note">Confirmed strengths</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Missing Skills</div>
                        <div class="kpi-value">{len(skill_analysis["missing_skills"])}</div>
                        <div class="kpi-note">Priority gaps</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Role Fit</div>
                        <div class="kpi-value">{html.escape(role_fit["fit"])}</div>
                        <div class="kpi-note">{job_fit_intelligence["confidence_score"]}% confidence</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:
                st.plotly_chart(
                    chart1,
                    use_container_width=True
                )

                st.plotly_chart(
                    chart2,
                    use_container_width=True
                )

            with c2:
                st.plotly_chart(
                    chart3,
                    use_container_width=True
                )

                st.plotly_chart(
                    chart4,
                    use_container_width=True
                )

        # AI SUMMARY
        with tabs[1]:

            st.subheader(
                "Role Fit Assessment"
            )

            st.info(
                role_fit["verdict"]
            )

            render_homelander_card(
                skill_analysis["match_percentage"]
            )

            st.subheader(
                "Job Fit Intelligence"
            )

            f1, f2 = st.columns(2)

            f1.metric(
                "Fit Confidence",
                f"{job_fit_intelligence['confidence_score']}%"
            )

            f2.metric(
                "Resume Signal Score",
                f"{resume_intelligence['resume_score']}%"
            )

            render_gap_panels(
                job_fit_intelligence
            )

            st.subheader(
                "Strategic AI Analysis"
            )

            st.markdown(
                ai_summary
            )

            st.subheader(
                "Deep Resume Intelligence"
            )

            render_resume_intelligence(
                resume_intelligence
            )

            st.subheader(
                "Resume Strength Analysis"
            )

            for item in resume_strengths:

                st.success(
                    f"{format_skill(item['skill'])} - {item['advantage']}"
                )

            st.subheader(
                "Adjacent Skill Leverage"
            )

            render_adjacent_skills(
                adjacent_skills
            )

            st.subheader(
                "Strategic Learning Roadmap"
            )

            st.markdown(
                learning_roadmap
            )

        # RESOURCES
        with tabs[2]:

            for skill, links in resources.items():

                st.markdown(
                    f"""
                    <div class="resource-heading">
                        {html.escape(format_skill(skill))}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                r1, r2, r3, r4 = st.columns(4)

                with r1:
                    st.link_button(
                        "Course",
                        links["course"]
                    )

                with r2:
                    st.link_button(
                        "Docs",
                        links["docs"]
                    )

                with r3:
                    st.link_button(
                        "Projects",
                        links["projects"]
                    )

                with r4:
                    st.link_button(
                        "Interview",
                        links["interview"]
                    )

        # REPORT
        with tabs[3]:

            try:
                report_path = generate_report(
                    skill_analysis["match_percentage"],
                    format_skills(
                        skill_analysis["matched_skills"]
                    ),
                    format_skills(
                        skill_analysis["missing_skills"]
                    ),
                    format_skill_map(
                        adjacent_skills
                    ),
                    {
                        format_skill(skill): level
                        for skill, level in difficulty_map.items()
                    },
                    {
                        format_skill(skill): estimate
                        for skill, estimate in time_estimates.items()
                    },
                    ai_summary,
                    learning_roadmap,
                    [],
                    {
                        "role_fit": role_fit["fit"],
                        "fit_confidence": job_fit_intelligence["confidence_score"],
                        "resume_score": resume_intelligence["resume_score"],
                        "matched_count": len(
                            skill_analysis["matched_skills"]
                        ),
                        "missing_count": len(
                            skill_analysis["missing_skills"]
                        ),
                        "resume_skill_count": len(
                            resume_skills
                        ),
                        "job_skill_count": len(
                            jd_skills
                        ),
                        "priority_missing_skills": format_skills(
                            priority_missing_skills
                        ),
                        "critical_gaps": format_skills(
                            job_fit_intelligence["critical_gaps"]
                        ),
                        "short_term_fixable_gaps": format_skills(
                            job_fit_intelligence["short_term_fixable_gaps"]
                        ),
                        "long_term_gaps": format_skills(
                            job_fit_intelligence["long_term_gaps"]
                        ),
                        "resume_strengths": resume_intelligence["strengths"],
                        "resume_weaknesses": resume_intelligence["weaknesses"],
                        "high_signal_skills": format_skills(
                            resume_intelligence["high_signal_skills"]
                        ),
                        "low_signal_sections": resume_intelligence["low_signal_sections"],
                        "semantic_matches": [
                            {
                                **match,
                                "resume_skill": format_skill(
                                    match.get(
                                        "resume_skill",
                                        ""
                                    )
                                ),
                                "jd_skill": format_skill(
                                    match.get(
                                        "jd_skill",
                                        ""
                                    )
                                )
                            }
                            for match in skill_analysis.get(
                                "semantic_matches",
                                []
                            )
                            if isinstance(
                                match,
                                dict
                            )
                        ]
                    }
                )

                with open(
                    report_path,
                    "rb"
                ) as pdf_file:

                    st.download_button(
                        "Download Intelligence Report",
                        pdf_file,
                        file_name="career_audit_report.pdf"
                    )

            except Exception:
                st.error(
                    "The intelligence report could not be generated right now. Your dashboard analysis is still available, so please try the download again in a moment."
                )

st.markdown(
    "<div class=\"creator-credit\">Developed by Aashrith Atmuri</div>",
    unsafe_allow_html=True
)
