import re
from collections import Counter
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)


VOUGHT_NAVY = colors.HexColor("#07111f")
VOUGHT_BLUE = colors.HexColor("#0f3b78")
VOUGHT_RED = colors.HexColor("#b31324")
VOUGHT_GOLD = colors.HexColor("#d6a94f")
VOUGHT_TEXT = colors.HexColor("#1f2937")
VOUGHT_MUTED = colors.HexColor("#64748b")
VOUGHT_ROW = colors.HexColor("#f3f6fb")
VOUGHT_GREEN = colors.HexColor("#2dd47f")
VOUGHT_PANEL = colors.HexColor("#eef3f9")


def _clean_inline(
    text
):
    text = escape(
        str(
            text
        )
    )

    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text
    )

    return text


def _cell(
    text,
    style
):
    return Paragraph(
        _clean_inline(
            text
        ),
        style
    )


def _build_styles():
    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "VoughtTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=VOUGHT_NAVY,
            spaceAfter=14
        ),
        "heading": ParagraphStyle(
            "VoughtHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=VOUGHT_RED,
            spaceBefore=8,
            spaceAfter=8
        ),
        "subheading": ParagraphStyle(
            "VoughtSubheading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=VOUGHT_BLUE,
            spaceBefore=6,
            spaceAfter=5
        ),
        "body": ParagraphStyle(
            "VoughtBody",
            parent=styles["BodyText"],
            alignment=TA_JUSTIFY,
            leading=16,
            textColor=VOUGHT_TEXT,
            spaceAfter=7
        ),
        "bullet": ParagraphStyle(
            "VoughtBullet",
            parent=styles["BodyText"],
            leftIndent=14,
            firstLineIndent=-8,
            leading=15,
            textColor=VOUGHT_TEXT,
            spaceAfter=4
        ),
        "small": ParagraphStyle(
            "VoughtSmall",
            parent=styles["BodyText"],
            alignment=TA_LEFT,
            fontSize=8.5,
            leading=11,
            textColor=VOUGHT_MUTED
        ),
        "header": ParagraphStyle(
            "VoughtHeader",
            parent=styles["BodyText"],
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white
        ),
        "score": ParagraphStyle(
            "ScoreCard",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=24,
            textColor=colors.white
        )
    }


def _add_markdown(
    elements,
    markdown_text,
    styles
):
    for raw_line in str(
        markdown_text or ""
    ).splitlines():
        line = raw_line.strip()

        if not line:
            elements.append(
                Spacer(
                    1,
                    4
                )
            )
            continue

        if line.startswith(
            "## "
        ):
            elements.append(
                Paragraph(
                    _clean_inline(
                        line[3:]
                    ),
                    styles["heading"]
                )
            )

        elif line.startswith(
            "### "
        ):
            elements.append(
                Paragraph(
                    _clean_inline(
                        line[4:]
                    ),
                    styles["subheading"]
                )
            )

        elif line.startswith(
            "- "
        ):
            elements.append(
                Paragraph(
                    f"- {_clean_inline(line[2:])}",
                    styles["bullet"]
                )
            )

        else:
            elements.append(
                Paragraph(
                    _clean_inline(
                        line
                    ),
                    styles["body"]
                )
            )


def _styled_table(
    table_data,
    col_widths=None,
    header_color=VOUGHT_NAVY
):
    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), header_color),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, VOUGHT_ROW]),
            ("TEXTCOLOR", (0,1), (-1,-1), VOUGHT_TEXT),
            ("GRID", (0,0), (-1,-1), 0.45, colors.HexColor("#d8dee9")),
            ("BOX", (0,0), (-1,-1), 1, VOUGHT_GOLD),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 7),
            ("RIGHTPADDING", (0,0), (-1,-1), 7),
            ("VALIGN", (0,0), (-1,-1), "TOP")
        ])
    )

    return table


def _score_card(
    label,
    value,
    styles
):
    return Table(
        [[
            Paragraph(
                f"<b>{_clean_inline(label)}</b><br/>{_clean_inline(value)}",
                styles["score"]
            )
        ]],
        colWidths=[2.25 * inch],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), VOUGHT_NAVY),
            ("BOX", (0,0), (-1,-1), 1.2, VOUGHT_GOLD),
            ("TOPPADDING", (0,0), (-1,-1), 13),
            ("BOTTOMPADDING", (0,0), (-1,-1), 13)
        ])
    )


def _match_pie(
    matched_count,
    missing_count
):
    drawing = Drawing(
        240,
        170
    )
    drawing.add(
        Rect(
            0,
            0,
            240,
            170,
            fillColor=VOUGHT_PANEL,
            strokeColor=colors.HexColor("#d8dee9")
        )
    )
    drawing.add(
        String(
            14,
            148,
            "Skill Match Distribution",
            fontName="Helvetica-Bold",
            fontSize=11,
            fillColor=VOUGHT_NAVY
        )
    )

    pie = Pie()
    pie.x = 25
    pie.y = 25
    pie.width = 105
    pie.height = 105
    pie.data = [
        max(
            0,
            matched_count
        ),
        max(
            0,
            missing_count
        )
    ] or [
        1,
        0
    ]
    pie.labels = [
        "Matched",
        "Missing"
    ]
    pie.slices[0].fillColor = VOUGHT_GREEN
    pie.slices[1].fillColor = VOUGHT_RED

    drawing.add(
        pie
    )
    drawing.add(
        String(
            145,
            90,
            f"Matched: {matched_count}",
            fontSize=9,
            fillColor=VOUGHT_TEXT
        )
    )
    drawing.add(
        String(
            145,
            72,
            f"Missing: {missing_count}",
            fontSize=9,
            fillColor=VOUGHT_TEXT
        )
    )

    return drawing


def _bar_chart(
    title,
    labels,
    values,
    bar_color=VOUGHT_BLUE
):
    drawing = Drawing(
        240,
        170
    )
    drawing.add(
        Rect(
            0,
            0,
            240,
            170,
            fillColor=VOUGHT_PANEL,
            strokeColor=colors.HexColor("#d8dee9")
        )
    )
    drawing.add(
        String(
            14,
            148,
            title,
            fontName="Helvetica-Bold",
            fontSize=11,
            fillColor=VOUGHT_NAVY
        )
    )

    chart = VerticalBarChart()
    chart.x = 28
    chart.y = 32
    chart.width = 178
    chart.height = 92
    chart.data = [
        [
            max(
                0,
                value
            )
            for value in values
        ]
    ]
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(
        values or [
            1
        ]
    ) + 1
    chart.valueAxis.valueStep = max(
        1,
        round(
            chart.valueAxis.valueMax / 4
        )
    )
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.angle = 25
    chart.categoryAxis.labels.fontSize = 6.8
    chart.valueAxis.labels.fontSize = 7
    chart.bars[0].fillColor = bar_color
    chart.bars[0].strokeColor = bar_color

    drawing.add(
        chart
    )

    return drawing


def _time_to_number(
    value
):
    match = re.search(
        r"\d+",
        str(
            value
        )
    )

    if not match:
        return 0

    return int(
        match.group()
    )


def _list_text(
    values
):
    values = [
        str(
            value
        )
        for value in values or []
        if str(
            value
        ).strip()
    ]

    return ", ".join(
        values
    ) if values else "None detected"


def generate_report(
    match_percentage,
    matched_skills,
    missing_skills,
    adjacent_skills,
    difficulty_map,
    time_estimates,
    ai_summary,
    learning_roadmap,
    chart_paths=None,
    analytics_data=None
):
    file_path = "career_audit_report.pdf"
    analytics_data = analytics_data or {}
    matched_count = analytics_data.get(
        "matched_count",
        len(
            matched_skills
        )
    )
    missing_count = analytics_data.get(
        "missing_count",
        len(
            missing_skills
        )
    )

    doc = SimpleDocTemplate(
        file_path,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch
    )

    styles = _build_styles()
    elements = []

    elements.append(
        Paragraph(
            "Executive Career Intelligence",
            styles["title"]
        )
    )
    elements.append(
        Spacer(
            1,
            10
        )
    )

    elements.append(
        Table(
            [[
                _score_card(
                    "Career Match",
                    f"{match_percentage}%",
                    styles
                ),
                _score_card(
                    "Role Fit",
                    analytics_data.get(
                        "role_fit",
                        "Not classified"
                    ),
                    styles
                ),
                _score_card(
                    "Resume Signal",
                    f"{analytics_data.get('resume_score', 'Unknown')}%",
                    styles
                )
            ]],
            colWidths=[2.35 * inch, 2.35 * inch, 2.35 * inch]
        )
    )
    elements.append(
        Spacer(
            1,
            16
        )
    )

    elements.append(
        Paragraph(
            "Strategic Intelligence Brief",
            styles["heading"]
        )
    )
    _add_markdown(
        elements,
        ai_summary,
        styles
    )

    elements.append(
        PageBreak()
    )

    elements.append(
        Paragraph(
            "Analytics Dashboard",
            styles["title"]
        )
    )

    difficulty_counts = Counter(
        difficulty_map.values()
    )
    top_time_items = sorted(
        time_estimates.items(),
        key=lambda item: _time_to_number(
            item[1]
        ),
        reverse=True
    )[:6]

    chart_grid = [
        [
            _match_pie(
                matched_count,
                missing_count
            ),
            _bar_chart(
                "Coverage Comparison",
                [
                    "Resume",
                    "Role"
                ],
                [
                    analytics_data.get(
                        "resume_skill_count",
                        matched_count
                    ),
                    analytics_data.get(
                        "job_skill_count",
                        matched_count + missing_count
                    )
                ],
                VOUGHT_BLUE
            )
        ],
        [
            _bar_chart(
                "Gap Difficulty",
                list(
                    difficulty_counts.keys()
                ) or [
                    "None"
                ],
                list(
                    difficulty_counts.values()
                ) or [
                    0
                ],
                VOUGHT_RED
            ),
            _bar_chart(
                "Learning Timeline",
                [
                    skill[:12]
                    for skill, _ in top_time_items
                ] or [
                    "None"
                ],
                [
                    _time_to_number(
                        estimate
                    )
                    for _, estimate in top_time_items
                ] or [
                    0
                ],
                VOUGHT_GOLD
            )
        ]
    ]

    elements.append(
        Table(
            chart_grid,
            colWidths=[3.45 * inch, 3.45 * inch],
            rowHeights=[1.9 * inch, 1.9 * inch],
            style=TableStyle([
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ALIGN", (0,0), (-1,-1), "CENTER")
            ])
        )
    )
    elements.append(
        Spacer(
            1,
            14
        )
    )

    summary_data = [
        [
            _cell(
                "Metric",
                styles["header"]
            ),
            _cell(
                "Value",
                styles["header"]
            )
        ],
        [
            _cell(
                "Fit Confidence",
                styles["body"]
            ),
            _cell(
                f"{analytics_data.get('fit_confidence', 'Unknown')}%",
                styles["body"]
            )
        ],
        [
            _cell(
                "Priority Missing Skills",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "priority_missing_skills",
                        missing_skills
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "Critical Gaps",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "critical_gaps",
                        []
                    )
                ),
                styles["body"]
            )
        ]
    ]
    elements.append(
        _styled_table(
            summary_data,
            col_widths=[2.2 * inch, 4.9 * inch]
        )
    )

    elements.append(
        PageBreak()
    )

    elements.append(
        Paragraph(
            "Strength and Gap Matrix",
            styles["title"]
        )
    )

    table_data = [
        [
            _cell(
                "Skill",
                styles["header"]
            ),
            _cell(
                "Status",
                styles["header"]
            ),
            _cell(
                "Difficulty",
                styles["header"]
            ),
            _cell(
                "Time",
                styles["header"]
            )
        ]
    ]

    for skill in matched_skills:
        table_data.append(
            [
                _cell(
                    skill,
                    styles["body"]
                ),
                _cell(
                    "Matched",
                    styles["body"]
                ),
                _cell(
                    "-",
                    styles["body"]
                ),
                _cell(
                    "-",
                    styles["body"]
                )
            ]
        )

    for skill in missing_skills:
        table_data.append(
            [
                _cell(
                    skill,
                    styles["body"]
                ),
                _cell(
                    "Missing",
                    styles["body"]
                ),
                _cell(
                    difficulty_map.get(
                        skill,
                        "Unknown"
                    ),
                    styles["body"]
                ),
                _cell(
                    time_estimates.get(
                        skill,
                        "Unknown"
                    ),
                    styles["body"]
                )
            ]
        )

    elements.append(
        _styled_table(
            table_data,
            col_widths=[2.55 * inch, 1.35 * inch, 1.5 * inch, 1.7 * inch]
        )
    )

    elements.append(
        PageBreak()
    )

    elements.append(
        Paragraph(
            "Job Fit and Resume Intelligence",
            styles["title"]
        )
    )

    intelligence_data = [
        [
            _cell(
                "Category",
                styles["header"]
            ),
            _cell(
                "Intelligence",
                styles["header"]
            )
        ],
        [
            _cell(
                "Short-Term Fixable Gaps",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "short_term_fixable_gaps",
                        []
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "Long-Term Gaps",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "long_term_gaps",
                        []
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "Resume Strengths",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "resume_strengths",
                        []
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "Resume Weaknesses",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "resume_weaknesses",
                        []
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "High-Signal Skills",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "high_signal_skills",
                        []
                    )
                ),
                styles["body"]
            )
        ],
        [
            _cell(
                "Low-Signal Sections",
                styles["body"]
            ),
            _cell(
                _list_text(
                    analytics_data.get(
                        "low_signal_sections",
                        []
                    )
                ),
                styles["body"]
            )
        ]
    ]

    elements.append(
        _styled_table(
            intelligence_data,
            col_widths=[2.25 * inch, 4.85 * inch],
            header_color=VOUGHT_BLUE
        )
    )

    semantic_matches = analytics_data.get(
        "semantic_matches",
        []
    )

    if semantic_matches:
        elements.append(
            Spacer(
                1,
                16
            )
        )
        elements.append(
            Paragraph(
                "Semantic Match Evidence",
                styles["heading"]
            )
        )

        semantic_data = [
            [
                _cell(
                    "Resume Skill",
                    styles["header"]
                ),
                _cell(
                    "Role Skill",
                    styles["header"]
                ),
                _cell(
                    "Relationship",
                    styles["header"]
                ),
                _cell(
                    "Relevance",
                    styles["header"]
                )
            ]
        ]

        for item in semantic_matches[:8]:
            semantic_data.append(
                [
                    _cell(
                        item.get(
                            "resume_skill",
                            "-"
                        ),
                        styles["small"]
                    ),
                    _cell(
                        item.get(
                            "jd_skill",
                            "-"
                        ),
                        styles["small"]
                    ),
                    _cell(
                        item.get(
                            "relationship",
                            "-"
                        ),
                        styles["small"]
                    ),
                    _cell(
                        item.get(
                            "hiring_relevance",
                            "-"
                        ),
                        styles["small"]
                    )
                ]
            )

        elements.append(
            _styled_table(
                semantic_data,
                col_widths=[1.45 * inch, 1.45 * inch, 1.35 * inch, 2.85 * inch],
                header_color=VOUGHT_RED
            )
        )

    elements.append(
        PageBreak()
    )

    elements.append(
        Paragraph(
            "Strategic Learning Roadmap",
            styles["title"]
        )
    )
    _add_markdown(
        elements,
        learning_roadmap,
        styles
    )

    if adjacent_skills:
        elements.append(
            PageBreak()
        )
        elements.append(
            Paragraph(
                "Adjacent Skill Leverage",
                styles["title"]
            )
        )

        adjacent_data = [
            [
                _cell(
                    "Existing Skill",
                    styles["header"]
                ),
                _cell(
                    "Can Support",
                    styles["header"]
                )
            ]
        ]

        for source_skill, mapped_skills in adjacent_skills.items():
            adjacent_data.append(
                [
                    _cell(
                        source_skill,
                        styles["body"]
                    ),
                    _cell(
                        _list_text(
                            mapped_skills if isinstance(
                                mapped_skills,
                                list
                            ) else [
                                mapped_skills
                            ]
                        ),
                        styles["body"]
                    )
                ]
            )

        elements.append(
            _styled_table(
                adjacent_data,
                col_widths=[2.5 * inch, 4.6 * inch],
                header_color=VOUGHT_BLUE
            )
        )

    elements.append(
        Spacer(
            1,
            18
        )
    )
    elements.append(
        Paragraph(
            "Developed by Aashrith Atmuri",
            ParagraphStyle(
                "CreatorCredit",
                parent=styles["small"],
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
                textColor=VOUGHT_MUTED
            )
        )
    )

    doc.build(
        elements
    )

    return file_path
