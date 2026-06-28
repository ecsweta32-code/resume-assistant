# src/report_builder.py
"""
Generates a clean, styled PDF screening report using ReportLab's Platypus engine.
No HTML/CSS knowledge required — all styling is done via Python objects.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Colour palette ──────────────────────────────────────────────────────────
INDIGO      = colors.HexColor("#4F46E5")
INDIGO_LIGHT= colors.HexColor("#EEF2FF")
SLATE_DARK  = colors.HexColor("#1E293B")
SLATE_MID   = colors.HexColor("#475569")
SLATE_LIGHT = colors.HexColor("#F8FAFC")
GREEN       = colors.HexColor("#16A34A")
RED         = colors.HexColor("#DC2626")
AMBER       = colors.HexColor("#D97706")
WHITE       = colors.white


def _build_styles() -> dict:
    """Return a dict of named ParagraphStyles."""
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#C7D2FE"),
            alignment=TA_CENTER,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=INDIGO,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE_DARK,
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE_DARK,
            leading=14,
            leftIndent=12,
            spaceAfter=3,
        ),
        "score_big": ParagraphStyle(
            "ScoreBig",
            fontName="Helvetica-Bold",
            fontSize=32,
            textColor=INDIGO,
            alignment=TA_CENTER,
        ),
        "score_label": ParagraphStyle(
            "ScoreLabel",
            fontName="Helvetica",
            fontSize=8,
            textColor=SLATE_MID,
            alignment=TA_CENTER,
        ),
        "skill_tag": ParagraphStyle(
            "SkillTag",
            fontName="Helvetica",
            fontSize=8,
            textColor=SLATE_DARK,
        ),
        "question_num": ParagraphStyle(
            "QuestionNum",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=INDIGO,
        ),
        "question_text": ParagraphStyle(
            "QuestionText",
            fontName="Helvetica",
            fontSize=9,
            textColor=SLATE_DARK,
            leading=13,
            leftIndent=16,
            spaceAfter=6,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=7,
            textColor=SLATE_MID,
            alignment=TA_CENTER,
        ),
    }


def _score_color(score: int) -> colors.HexColor:
    if score >= 75:
        return GREEN
    elif score >= 50:
        return AMBER
    return RED


def _header_block(candidate_name: str, styles: dict) -> list:
    """Dark indigo banner with candidate name and timestamp."""
    timestamp = datetime.now().strftime("%B %d, %Y  •  %H:%M")

    header_data = [[
        Paragraph(f"AI Candidate Screening Report", styles["title"]),
    ]]
    sub_data = [[
        Paragraph(f"{candidate_name}  ·  Generated {timestamp}", styles["subtitle"]),
    ]]

    banner = Table(header_data, colWidths=[170 * mm])
    banner.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), INDIGO),
        ("TOPPADDING",  (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [6]),
    ]))

    sub_banner = Table(sub_data, colWidths=[170 * mm])
    sub_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), INDIGO),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ]))

    return [banner, sub_banner, Spacer(1, 8 * mm)]


def _score_section(score: int, styles: dict) -> list:
    """Circular-style score card + colour-coded bar."""
    sc = _score_color(score)

    # Score card (two-column: big number | label)
    score_card = Table(
        [[
            Paragraph(f"{score}", styles["score_big"]),
            Paragraph("out of 100", styles["score_label"]),
        ]],
        colWidths=[40 * mm, 130 * mm],
    )
    score_card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), INDIGO_LIGHT),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (0, 0),   20),
        ("ROUNDEDCORNERS", [6]),
    ]))

    # Progress bar (filled portion as coloured table cell)
    fill_w = max(1, int(170 * score / 100))
    rest_w = 170 - fill_w

    bar_data = [[" ", " "]]
    bar = Table(bar_data, colWidths=[fill_w * mm, rest_w * mm])
    bar.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), sc),
        ("BACKGROUND",    (1, 0), (1, 0), colors.HexColor("#E2E8F0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [4]),
    ]))

    label_verb = "Strong Match" if score >= 75 else ("Partial Match" if score >= 50 else "Weak Match")

    return [
        Paragraph("Overall Match Score", styles["section_heading"]),
        score_card,
        Spacer(1, 3 * mm),
        bar,
        Paragraph(
            f"<font color='#{sc.hexval()[2:]}'>● {label_verb}</font>",
            styles["body"]
        ),
        Spacer(1, 4 * mm),
    ]


def _skills_section(matched: list, missing: list, styles: dict) -> list:
    """Two-column skills table: matched (green) | missing (red)."""

    def tag_rows(skills: list, colour: str) -> list:
        return [[Paragraph(f"• {s}", styles["skill_tag"])] for s in skills] or \
               [[Paragraph("None identified", styles["skill_tag"])]]

    matched_rows = tag_rows(matched, "#16A34A")
    missing_rows = tag_rows(missing, "#DC2626")

    # Pad to same length
    max_len = max(len(matched_rows), len(missing_rows))
    matched_rows += [[""] * 1] * (max_len - len(matched_rows))
    missing_rows += [[""] * 1] * (max_len - len(missing_rows))

    combined = [[m[0], ms[0]] for m, ms in zip(matched_rows, missing_rows)]

    header = [[
        Paragraph("<b>✓ Matched Skills</b>", ParagraphStyle("mh", fontName="Helvetica-Bold",
                  fontSize=9, textColor=GREEN)),
        Paragraph("<b>✗ Missing Skills</b>", ParagraphStyle("mh2", fontName="Helvetica-Bold",
                  fontSize=9, textColor=RED)),
    ]]

    table = Table(header + combined, colWidths=[85 * mm, 85 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), SLATE_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))

    return [
        Paragraph("Skill Breakdown", styles["section_heading"]),
        table,
        Spacer(1, 4 * mm),
    ]


def _summary_section(summary_text: str, styles: dict) -> list:
    """Candidate summary — strips markdown symbols, renders paragraphs."""
    elements = [Paragraph("Candidate Summary", styles["section_heading"])]

    for line in summary_text.split("\n"):
        clean = line.strip().lstrip("#*- ").strip()
        if not clean:
            elements.append(Spacer(1, 2 * mm))
            continue
        if line.strip().startswith(("- ", "* ", "• ")):
            elements.append(Paragraph(f"• {clean}", styles["bullet"]))
        else:
            elements.append(Paragraph(clean, styles["body"]))

    elements.append(Spacer(1, 4 * mm))
    return elements


def _questions_section(questions: list, styles: dict) -> list:
    """Numbered interview questions in a light card."""
    elements = [Paragraph("Recommended Interview Questions", styles["section_heading"])]

    for i, q in enumerate(questions, 1):
        clean_q = q.strip().lstrip("0123456789.-) ").strip()
        block = KeepTogether([
            Paragraph(f"Q{i}", styles["question_num"]),
            Paragraph(clean_q, styles["question_text"]),
        ])
        elements.append(block)

    return elements


def build_pdf_report(candidate_name: str, final_output: dict) -> bytes:
    """
    Main entry point.

    Args:
        candidate_name : display name of the candidate
        final_output   : the dict returned by langgraph_app.invoke()
                         expects keys: score_report, summary, interview_questions

    Returns:
        Raw PDF bytes ready for st.download_button()
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Screening Report – {candidate_name}",
        author="AI Resume Screening Assistant",
    )

    styles = _build_styles()

    # ── Unpack data ──────────────────────────────────────────────────────────
    score_report = final_output.get("score_report", {})
    score        = score_report.get("score", 0)
    matched      = score_report.get("matched_skills", [])
    missing      = score_report.get("missing_skills", [])
    summary      = final_output.get("summary", "")
    questions    = final_output.get("interview_questions", [])

    # ── Assemble story ───────────────────────────────────────────────────────
    story = []
    story += _header_block(candidate_name, styles)
    story += _score_section(score, styles)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
    story += _skills_section(matched, missing, styles)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
    story += _summary_section(summary, styles)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
    story += _questions_section(questions, styles)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "Generated by Enterprise AI Resume Screener  ·  Powered by LangGraph & Gemini 2.5",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()