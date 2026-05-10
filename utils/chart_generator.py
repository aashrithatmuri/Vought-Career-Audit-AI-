import plotly.graph_objects as go

VOUGHT_NAVY = "#07111f"
VOUGHT_PANEL = "#0b1728"
VOUGHT_BLUE = "#1f5ea8"
VOUGHT_RED = "#e11d2f"
VOUGHT_GOLD = "#d6a94f"
VOUGHT_GREEN = "#2dd47f"
VOUGHT_TEXT = "#eef4ff"
VOUGHT_MUTED = "#aeb8c7"
VOUGHT_GRID = "rgba(238, 244, 255, 0.12)"


def apply_theme(
    fig,
    title
):

    fig.update_layout(
        title=title,
        paper_bgcolor=VOUGHT_PANEL,
        plot_bgcolor=VOUGHT_PANEL,

        font=dict(
            color=VOUGHT_TEXT,
            family="Inter, Arial, sans-serif",
            size=13
        ),

        title_font=dict(
            size=20,
            color=VOUGHT_TEXT,
            family="Oswald, Arial, sans-serif"
        ),

        margin=dict(
            l=48,
            r=28,
            t=68,
            b=48
        ),

        height=360,

        hoverlabel=dict(
            bgcolor="#f8fafc",
            bordercolor=VOUGHT_GOLD,
            font=dict(
                color="#0b1220",
                family="Inter, Arial, sans-serif"
            )
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(
                color=VOUGHT_MUTED
            )
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            color=VOUGHT_MUTED
        ),
        title_font=dict(
            color=VOUGHT_MUTED
        )
    )

    fig.update_yaxes(
        gridcolor=VOUGHT_GRID,
        zeroline=False,
        tickfont=dict(
            color=VOUGHT_MUTED
        ),
        title_font=dict(
            color=VOUGHT_MUTED
        )
    )

    return fig


def generate_match_chart(
    matched_skills,
    missing_skills
):

    fig = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Matched",
                    "Missing"
                ],
                values=[
                    len(matched_skills),
                    len(missing_skills)
                ],
                hole=0.45,

                marker=dict(
                    colors=[
                        VOUGHT_GREEN,
                        VOUGHT_RED
                    ]
                ),

                textfont=dict(
                    color=VOUGHT_TEXT
                ),

                textinfo="label+percent",
                hovertemplate="%{label}: %{value}<extra></extra>",
                pull=[0.02, 0.02]
            )
        ]
    )

    return apply_theme(
        fig,
        "Skill Match Distribution"
    )


def generate_difficulty_chart(
    difficulty_map
):

    counts = {}

    for skill, level in difficulty_map.items():
        counts[level] = counts.get(level, 0) + 1

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(counts.keys()),
                y=list(counts.values()),

                marker=dict(
                    color=VOUGHT_RED,
                    line=dict(
                        color="rgba(255,255,255,0.42)",
                        width=1
                    )
                ),

                hovertemplate="%{x}: %{y}<extra></extra>"
            )
        ]
    )

    return apply_theme(
        fig,
        "Difficulty Distribution"
    )


def generate_time_chart(
    time_estimates
):

    skills = list(
        time_estimates.keys()
    )

    durations = []

    for value in time_estimates.values():

        try:
            num = int(
                str(value).split()[0]
            )

        except:
            num = 0

        durations.append(
            num
        )

    fig = go.Figure(
        data=[
            go.Bar(
                x=skills,
                y=durations,

                marker=dict(
                    color=VOUGHT_GOLD,
                    line=dict(
                        color="rgba(255,255,255,0.42)",
                        width=1
                    )
                ),

                hovertemplate="%{x}: %{y} weeks<extra></extra>"
            )
        ]
    )

    return apply_theme(
        fig,
        "Learning Timeline"
    )


def generate_coverage_chart(
    resume_skills,
    jd_skills
):

    fig = go.Figure(
        data=[
            go.Bar(
                x=[
                    "Resume",
                    "Job Description"
                ],

                y=[
                    len(resume_skills),
                    len(jd_skills)
                ],

                marker=dict(
                    color=[
                        VOUGHT_BLUE,
                        VOUGHT_RED
                    ],
                    line=dict(
                        color="rgba(255,255,255,0.42)",
                        width=1
                    )
                ),

                hovertemplate="%{x}: %{y} skills<extra></extra>"
            )
        ]
    )

    return apply_theme(
        fig,
        "Coverage Comparison"
    )
