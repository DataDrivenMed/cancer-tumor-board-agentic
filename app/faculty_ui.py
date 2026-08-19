from __future__ import annotations

import csv
import io
from html import escape
from typing import Any

import streamlit as st

from app.xai_theme import inject_xai_theme
from services.oncology_programs import PROGRAMS, PROGRAM_BY_ID
from services.pathway_validation import COMMON_CORE_QUALIFICATION, get_pathway_validation_status


def _val(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _txt(value: Any, default: str = "Not available") -> str:
    if value is None:
        return default
    if hasattr(value, "value"):
        value = value.value
    text = str(value).strip()
    return text or default


def faculty_css() -> None:
    inject_xai_theme()
    st.markdown(
        """
<style>
.fx-context{display:grid;grid-template-columns:1fr 1fr 1fr 1fr 2fr;gap:8px;margin:8px 0 14px}.fx-context>div,.fx-mini{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:11px}.fx-lbl{font:600 9px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.fx-val{font-size:13px;color:var(--ink);font-weight:600;margin-top:5px}.fx-question .fx-val{white-space:normal}.fx-panel-title{font-family:var(--serif);font-size:22px;color:var(--ink);font-weight:500;margin:18px 0 4px}.fx-panel-sub{font-size:12px;color:var(--muted);margin-bottom:10px}.fx-thirty-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px}.fx-thirty-cell{background:var(--panel);border:1px solid var(--line2);border-radius:11px;padding:11px}.fx-source-chip{display:inline-flex;padding:4px 7px;border-radius:999px;background:var(--panel2);border:1px solid var(--line2);font:600 9px/1 var(--mono);color:var(--body);margin:3px 3px 0 0}.fx-program-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.fx-program{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:12px}.fx-program strong{color:var(--ink);font-size:13px}.fx-program span{display:block;color:var(--muted);font-size:11px;margin-top:4px}@media(max-width:900px){.fx-context,.fx-thirty-grid,.fx-program-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.fx-context,.fx-thirty-grid,.fx-program-grid{grid-template-columns:1fr}}
</style>
""",
        unsafe_allow_html=True,
    )


def product_header(mode: str = "Faculty evaluation") -> None:
    st.markdown(
        '<div class="fx-side-brand"><div class="fx-side-mark">TB</div><div><div class="fx-side-name">Pan-Oncology Tumor Board Intelligence</div>'
        f'<div class="fx-side-sub">{escape(mode)} · Research decision support</div></div></div>',
        unsafe_allow_html=True,
    )


def top_navigation(active: str) -> None:
    inject_xai_theme()
    links = [
        ("pages/04_Agentic_Workspace.py", "Agentic Workspace", "agentic"),
        ("pages/00_Clinical_Workspace.py", "Classic Workspace", "workspace"),
        ("pages/01_Validation.py", "Validation", "validation"),
        ("pages/03_Architecture.py", "Architecture", "architecture"),
        ("pages/02_About.py", "About", "about"),
    ]
    with st.sidebar:
        st.markdown('<div class="fx-side-label">Navigate</div>', unsafe_allow_html=True)
        for page, label, key in links:
            st.page_link(page, label=label, use_container_width=True, disabled=active == key)
        st.markdown('<div class="fx-side-label">System</div><div class="fx-mini"><span class="chip warn">Research mode</span><p style="font-size:11px">Clinical release not established.</p></div>', unsafe_allow_html=True)


def research_footer() -> None:
    st.markdown('<div class="fx-footer"><div>Research decision support · de-identified or synthetic data only</div><div>Not clinically validated for unrestricted patient-care use</div></div>', unsafe_allow_html=True)


def render_case_context(case: Any) -> None:
    program = PROGRAM_BY_ID.get(getattr(case, "disease_program", None))
    validation = get_pathway_validation_status(getattr(case, "disease_program", None))
    values = [
        ("Tumor board", program.display_name if program else _txt(getattr(case, "disease_program", None))),
        ("Diagnosis", _txt(_val(getattr(case, "diagnosis", None), "value"))),
        ("Disease state", _txt(_val(getattr(case, "disease_state", None), "value"))),
        ("Validation", validation.label),
        ("Tumor board question", _txt(_val(getattr(case, "clinical_question", None), "question"))),
    ]
    html = '<div class="fx-context">'
    for idx, (label, value) in enumerate(values):
        css = ' class="fx-question"' if idx == 4 else ''
        html += f'<div{css}><div class="fx-lbl">{escape(label)}</div><div class="fx-val">{escape(value)}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def _brief_item(result: dict[str, Any], *needles: str) -> str:
    brief = result.get("tumor_board_brief")
    for section in _val(brief, "sections", []) or []:
        sid = _txt(_val(section, "section_id", ""), "").lower()
        title = _txt(_val(section, "title", ""), "").lower()
        if any(n.lower() in sid or n.lower() in title for n in needles):
            items = _val(section, "items", []) or []
            if items:
                return _txt(_val(items[0], "value"))
    return "Not available from the current governed brief"


def render_thirty_second_view(result: dict[str, Any], case: Any) -> None:
    final = result.get("final_decision")
    cells = [
        ("Diagnosis", _txt(_val(case.diagnosis, "value"))),
        ("Disease state", _txt(_val(case.disease_state, "value"))),
        ("Decision state", _txt(_val(final, "decision_state")).replace("_", " ").title()),
        ("Primary strategy", _txt(_val(final, "primary_strategy"), "WITHHELD")),
        ("Evidence strength", _txt(_val(final, "decision_support_strength"))),
        ("Biggest uncertainty", _brief_item(result, "uncertainty", "missing")),
        ("Source traces", str(_val(result.get("tumor_board_brief"), "source_trace_count", 0))),
        ("Question", _txt(_val(case.clinical_question, "question"))),
    ]
    html = '<div class="fx-thirty"><div class="fx-kicker">30-second Tumor Board View</div><div class="fx-thirty-grid">'
    for label, value in cells:
        html += f'<div class="fx-thirty-cell"><div class="fx-lbl">{escape(label)}</div><div class="fx-val">{escape(value)}</div></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_treatment_timeline(case: Any) -> None:
    st.markdown('<div class="fx-panel-title">Treatment history</div><div class="fx-panel-sub">Represented treatment sequence. Missing history remains explicit.</div>', unsafe_allow_html=True)
    treatments = getattr(case, "treatments", []) or []
    if not treatments:
        st.info("No treatment history is represented in the current case.")
        return
    rows = []
    for item in treatments:
        rows.append({
            "Regimen": _txt(getattr(item, "regimen", None)),
            "Status": _txt(getattr(item, "treatment_status", None)).replace("_", " ").title(),
            "Line": getattr(item, "line_of_therapy", None),
            "Response": _txt(getattr(item, "best_response", None)),
            "Human verified": "Yes" if getattr(item, "human_verified", False) else "No",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_molecular_table(case: Any) -> None:
    st.markdown('<div class="fx-panel-title">Molecular findings</div><div class="fx-panel-sub">Structured alterations remain distinct from clinical actionability.</div>', unsafe_allow_html=True)
    findings = getattr(case, "molecular_findings", []) or []
    if not findings:
        st.info("No molecular findings are represented.")
        return
    rows = []
    for item in findings:
        rows.append({
            "Gene": _txt(getattr(item, "gene", None)),
            "Alteration": _txt(getattr(item, "alteration_type", None)),
            "HGVS": _txt(getattr(item, "hgvs_p", None), _txt(getattr(item, "hgvs_c", None))),
            "VAF": getattr(item, "variant_allele_frequency", None),
            "Human verified": "Yes" if getattr(item, "human_verified", False) else "No",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_feedback() -> None:
    st.markdown('<div class="fx-panel-title">Faculty evaluation</div><div class="fx-panel-sub">Optional research/usability feedback.</div>', unsafe_allow_html=True)
    with st.form("faculty_feedback"):
        usefulness = st.select_slider("Clinical usefulness", options=["Very low", "Low", "Moderate", "High", "Very high"], value="Moderate")
        evidence = st.select_slider("Evidence completeness", options=["Very low", "Low", "Moderate", "High", "Very high"], value="Moderate")
        trust = st.select_slider("Overall trust", options=["Very low", "Low", "Moderate", "High", "Very high"], value="Moderate")
        comments = st.text_area("Optional comments")
        submitted = st.form_submit_button("Add feedback", use_container_width=True)
    if submitted:
        st.session_state.setdefault("faculty_feedback_rows", []).append({"clinical_usefulness": usefulness, "evidence_completeness": evidence, "overall_trust": trust, "comments": comments})
        st.success("Feedback added to this session.")
    rows = st.session_state.get("faculty_feedback_rows", [])
    if rows:
        output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=list(rows[0].keys())); writer.writeheader(); writer.writerows(rows)
        st.download_button("Download feedback CSV", data=output.getvalue(), file_name="tumor_board_faculty_feedback.csv", mime="text/csv", use_container_width=True)


def render_validation_page() -> None:
    faculty_css(); top_navigation("validation")
    st.title("Validation & scope")
    st.write("Software qualification and clinical validation are kept explicitly separate.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Common-core result", str(COMMON_CORE_QUALIFICATION.get("result", "unknown")).upper())
    c2.metric("Matrix executions", COMMON_CORE_QUALIFICATION.get("matrix_executions", 0))
    c3.metric("Regression tests", COMMON_CORE_QUALIFICATION.get("full_regression_tests_passed", 0))
    rows = []
    for program in PROGRAMS:
        status = get_pathway_validation_status(program.program_id)
        rows.append({"Program": program.display_name, "State": status.label, "Disease-specific qualified": status.disease_specific_software_qualified, "Clinically validated": status.clinically_validated})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    research_footer()


def render_about_page() -> None:
    faculty_css(); top_navigation("about")
    st.title("About")
    st.write("Pan-oncology research decision support built around source provenance, bounded evidence retrieval, explicit missingness, conflict detection, abstention, clinical red-team challenge, consensus gating, and an auditable tumor-board brief.")
    st.warning("The platform is not clinically validated for autonomous treatment decisions and does not establish trial eligibility.")
    research_footer()
