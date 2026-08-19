from __future__ import annotations

from html import escape
from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

REPORT_VERSION = "1.0.0"


def _value(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _text(value: Any, default: str = "Not represented") -> str:
    if value is None:
        return default
    if hasattr(value, "value"):
        value = value.value
    text = str(value).strip()
    return text or default


def _safe(value: Any) -> str:
    return escape(_text(value, ""))


def build_tumor_board_pdf(result: dict[str, Any]) -> bytes:
    """Presentation-only export of the governed tumor-board brief.

    The renderer adds no clinical claims and does not alter workflow gates.
    """
    case = result.get("case")
    brief = result.get("tumor_board_brief")
    if case is None or brief is None:
        raise ValueError("case and tumor_board_brief are required for PDF export")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.65 * inch,
        title=f"Tumor Board Intelligence - {_text(_value(case, 'case_id'))}",
        author="Tumor Board Intelligence",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TBTitle", parent=styles["Title"], fontSize=19, leading=23, spaceAfter=8)
    section_style = ParagraphStyle("TBSection", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=8, spaceAfter=5)
    body = ParagraphStyle("TBBody", parent=styles["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("TBSmall", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#666666"))

    diagnosis = _text(_value(_value(case, "diagnosis"), "value"))
    disease_state = _text(_value(_value(case, "disease_state"), "value"))
    stage = _text(_value(_value(case, "stage"), "value"))
    question = _text(_value(_value(case, "clinical_question"), "question"))

    story = [
        Paragraph("Tumor Board Intelligence", title),
        Paragraph("Evidence-grounded multidisciplinary decision-support brief", body),
        Spacer(1, 7),
    ]
    summary_rows = [
        ["Case", _text(_value(case, "case_id")), "Diagnosis", diagnosis],
        ["Disease state", disease_state, "Stage", stage],
        ["Question", question, "Case type", _text(_value(case, "case_type"))],
    ]
    table = Table(summary_rows, colWidths=[0.9*inch, 2.45*inch, 1.0*inch, 2.55*inch])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D9D9D9")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F3F3F3")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#F3F3F3")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [table, Spacer(1, 8)]

    story.append(Paragraph("Decision controls", section_style))
    story.append(Paragraph(
        _safe(
            f"Decision state: {_text(_value(brief, 'decision_state'))}. "
            f"Decision-support strength: {_text(_value(brief, 'decision_support_strength'))}. "
            f"Brief status: {_text(_value(brief, 'status'))}. "
            f"Source trace count: {_value(brief, 'source_trace_count', 0)}."
        ), body
    ))
    summary = _value(brief, "summary")
    if summary:
        story += [Paragraph("Executive summary", section_style), Paragraph(_safe(summary), body)]

    warnings = list(_value(brief, "critical_warnings", []) or [])
    if warnings:
        story.append(Paragraph("Critical warnings", section_style))
        for warning in warnings:
            story.append(Paragraph("• " + _safe(warning), body))

    for section in list(_value(brief, "sections", []) or []):
        story.append(Paragraph(_safe(_value(section, "title")), section_style))
        note = _value(section, "section_note")
        if note:
            story.append(Paragraph(_safe(note), small))
        items = list(_value(section, "items", []) or [])
        if not items:
            story.append(Paragraph("No items represented.", body))
        for item in items:
            label = _text(_value(item, "label"))
            value = _text(_value(item, "value"))
            epistemic = _text(_value(item, "epistemic_label"), "")
            refs = list(_value(item, "source_refs", []) or [])
            limitations = list(_value(item, "limitations", []) or [])
            story.append(Paragraph(f"<b>{_safe(label)}</b>: {_safe(value)}", body))
            metadata = []
            if epistemic:
                metadata.append(epistemic)
            if refs:
                metadata.append("Sources: " + ", ".join(str(x) for x in refs))
            if limitations:
                metadata.append("Limitations: " + "; ".join(str(x) for x in limitations))
            if metadata:
                story.append(Paragraph(_safe(" | ".join(metadata)), small))
            story.append(Spacer(1, 3))

    story += [
        Spacer(1, 8),
        Paragraph("Report controls", section_style),
        Paragraph(
            _safe(
                f"Renderer version {REPORT_VERSION}. This PDF is generated only from the structured workflow output and does not add clinical claims."
            ),
            small,
        ),
        Paragraph(
            "Research decision support only. Clinical trial matching does not establish eligibility. Management output must not be treated as an autonomous treatment directive.",
            small,
        ),
    ]
    doc.build(story)
    return buffer.getvalue()
