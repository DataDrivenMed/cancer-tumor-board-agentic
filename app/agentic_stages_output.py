from __future__ import annotations

from html import escape

import streamlit as st

from app.agentic_core import goto, human, run_guarded_workflow, txt, val
from app.agentic_layout import claim_chip, logic_strip, turn
from app.chat_ui import render_governed_chat
from services.tumor_board_pdf import build_tumor_board_pdf


def _render_specialist_outputs(result: dict) -> None:
    outputs = result.get("specialist_outputs", {}) or {}
    if not outputs:
        st.info("No specialist outputs were produced because a pre-routing guardrail may have stopped the workflow.")
        return

    order = ("guideline", "molecular", "safety", "literature", "clinical_trials", "translational")
    keys = [k for k in order if k in outputs] + [k for k in outputs if k not in order]
    for agent_id in keys:
        output = outputs[agent_id]
        status = human(val(output, "status"))
        with st.expander(f"{agent_id.replace('_', ' ').title()} · {status}"):
            st.write(txt(val(output, "summary")))
            warnings = val(output, "warnings", []) or []
            limitations = val(output, "limitations", []) or []
            if warnings:
                st.markdown("**Warnings**")
                for item in warnings:
                    st.warning(txt(item))
            if limitations:
                st.markdown("**Limitations**")
                for item in limitations:
                    st.caption("• " + txt(item))
            try:
                st.json(output.model_dump(mode="json"), expanded=False)
            except Exception:
                if isinstance(output, dict):
                    st.json(output, expanded=False)


def _render_gate_summary(result: dict) -> None:
    integrity = result.get("case_integrity_report")
    missing = result.get("missing_information_report")
    semantic = result.get("semantic_integrity_findings", []) or []
    routing = result.get("routing")
    final = result.get("final_decision")
    brief = result.get("tumor_board_brief")

    st.markdown("#### Why this result is allowed to exist")
    logic_strip(result)

    cols = st.columns(3, gap="small")
    with cols[0]:
        st.markdown("**Pre-routing safety**")
        st.caption(
            f"Case integrity: {human(val(integrity, 'disposition', 'not run'))}. "
            f"Semantic findings: {len(semantic)}. "
            f"Blocking information gaps: {val(missing, 'blocking_count', 0) or 0}."
        )
    with cols[1]:
        st.markdown("**Evidence routing**")
        selected = val(routing, "selected_agents", []) or []
        st.caption("Specialists: " + (", ".join(human(x) for x in selected) if selected else "none routed"))
    with cols[2]:
        st.markdown("**Release state**")
        st.caption(
            f"Decision: {human(val(final, 'decision_state', 'not established'))}. "
            f"Support: {human(val(final, 'decision_support_strength', 'insufficient'))}. "
            f"Brief safe to display: {'yes' if val(brief, 'safe_to_display', False) else 'no'}."
        )


def render_analysis() -> None:
    if not st.session_state.ag_evidence_confirmed:
        goto("evidence")
        return

    if st.session_state.ag_result is None:
        try:
            with st.status("Running governed multi-agent tumor-board workflow...", expanded=True) as status:
                status.write("Configuring fail-closed evidence channels")
                status.write("Checking semantic integrity, case integrity, conflicts, and missing information")
                status.write("Routing only the specialists required by the represented clinical question")
                status.write("Running evidence-bounded specialist analysis")
                status.write("Running clinical red-team challenge and consensus adjudication")
                status.write("Rendering the structured decision-support brief")
                result = run_guarded_workflow()
                status.update(label="Governed analysis complete", state="complete")
        except Exception as exc:
            st.error(f"Workflow stopped safely: {type(exc).__name__}: {exc}")
            st.caption("No fallback clinical claim is generated when the governed workflow fails.")
            return
    else:
        result = st.session_state.ag_result

    turn(
        "Tumor Board Agent · Analysis",
        "The original governed workflow has now run underneath this conversational surface. "
        "The center column shows the clinically useful synthesis. The right inspector exposes the execution state, "
        "evidence admission, routing, safety gates, and audit trail.",
        chips=[claim_chip("retrieved"), claim_chip("derived")],
    )

    _render_gate_summary(result)

    preliminary = txt(result.get("preliminary_synthesis"), "")
    if preliminary:
        st.markdown("#### Preliminary synthesis")
        st.write(preliminary)

    red_team = result.get("red_team_report")
    findings = result.get("red_team_findings", []) or []
    with st.expander("Clinical red-team challenge", expanded=True):
        if red_team is not None:
            st.write(txt(val(red_team, "summary")))
        if not findings:
            st.caption("No red-team findings represented.")
        for finding in findings:
            severity = human(val(finding, "severity"))
            st.markdown(f"**{severity}:** {txt(val(finding, 'issue'))}")
            effect = txt(val(finding, "effect_on_recommendation"), "")
            if effect:
                st.caption("Effect on recommendation: " + effect)

    consensus = result.get("consensus_report")
    with st.expander("Consensus adjudication", expanded=True):
        if consensus is None:
            st.info("Consensus was not run because an earlier safety gate stopped the workflow.")
        else:
            st.write(txt(val(consensus, "summary")))
            decision_state = human(val(consensus, "decision_state", "not represented"))
            st.caption(f"Adjudicated decision state: {decision_state}")
            try:
                st.json(consensus.model_dump(mode="json"), expanded=False)
            except Exception:
                pass

    missing = result.get("missing_information_report")
    if missing is not None and (val(missing, "items", []) or []):
        st.markdown(
            '<div class="guardrail"><strong>Unresolved decision-critical information</strong>'
            '<p>Missing, conflicting, pending, or unavailable information remains visible after synthesis. '
            'Recommendation-blocking gaps cannot be bypassed by fluent language or by a high-confidence model response.</p></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Missing-information report", expanded=True):
            st.write(txt(val(missing, "summary")))
            for item in val(missing, "items", []) or []:
                block = " · BLOCKING" if val(item, "recommendation_blocking", False) else ""
                st.write(f"**{txt(val(item, 'field'))}** · {human(val(item, 'priority'))}{block}")
                st.caption(txt(val(item, "reason")))

    with st.expander("All specialist outputs and machine-readable evidence"):
        _render_specialist_outputs(result)

    if st.button("Open full decision brief", type="primary", use_container_width=True, key="ag_to_brief"):
        goto("brief")


def _brief_category(epistemic: str) -> str:
    normalized = epistemic.upper()
    if normalized in {"OBSERVED", "SOURCE_FACT"}:
        return "source"
    if normalized in {"INTERPRETED", "DERIVED"}:
        return "derived"
    if normalized in {"HUMAN", "ADJUDICATED"}:
        return "human"
    return "retrieved"


def _render_brief_sections(brief) -> None:
    st.markdown(
        '<div class="legend">'
        + claim_chip("source")
        + claim_chip("retrieved")
        + claim_chip("derived")
        + claim_chip("human")
        + "</div>",
        unsafe_allow_html=True,
    )
    for section in val(brief, "sections", []) or []:
        items_html = []
        for item in val(section, "items", []) or []:
            category = claim_chip(_brief_category(txt(val(item, "epistemic_label"), "")))
            refs = val(item, "source_refs", []) or []
            limitations = val(item, "limitations", []) or []
            refs_html = f'<div class="source-refs">Sources: {escape(", ".join(map(str, refs)))}</div>' if refs else ""
            lim_html = f'<div class="brief-note">Limitations: {escape(" · ".join(map(str, limitations)))}</div>' if limitations else ""
            items_html.append(
                '<div class="brief-item">'
                f'<div class="brief-label">{escape(txt(val(item, "label")))}</div>'
                f'<div class="brief-value">{escape(txt(val(item, "value")))}</div>'
                f'<div class="legend">{category}</div>{refs_html}{lim_html}</div>'
            )
        note = txt(val(section, "section_note"), "")
        st.markdown(
            '<div class="brief-section">'
            f'<div class="brief-title">{escape(txt(val(section, "title")))}</div>'
            f'<div class="brief-note">{escape(note)}</div>'
            + "".join(items_html)
            + "</div>",
            unsafe_allow_html=True,
        )


def _render_decision_dimensions(final) -> None:
    alternatives = val(final, "alternatives", []) or []
    conditions = val(final, "conditions", []) or []
    uncertainties = val(final, "major_uncertainties", []) or []
    priorities = val(final, "discussion_priorities", []) or []

    if alternatives:
        st.markdown("#### Reasonable alternatives")
        for item in alternatives:
            st.write("• " + txt(item))
    if conditions:
        st.markdown("#### Conditions and prerequisites")
        for item in conditions:
            st.write("• " + txt(item))
    if uncertainties:
        st.markdown("#### Major uncertainties")
        for item in uncertainties:
            st.warning(txt(item))
    if priorities:
        st.markdown("#### Tumor-board discussion priorities")
        for item in priorities:
            st.write("• " + txt(item))


def _render_trial_safety_boundaries(result: dict) -> None:
    specialist_outputs = result.get("specialist_outputs", {}) or {}

    trial_output = specialist_outputs.get("clinical_trials")
    if trial_output is not None:
        with st.expander("Clinical-trial opportunities and eligibility boundary"):
            st.write(txt(val(trial_output, "summary")))
            matches = val(trial_output, "matches", []) or []
            if not matches:
                st.caption("No governed possible trial matches are represented.")
            for match in matches:
                st.write(f"**{txt(val(match, 'nct_id'))}:** {txt(val(match, 'title'))}")
                st.caption(txt(val(match, "rationale")))
                unresolved = val(match, "unresolved_eligibility_domains", []) or []
                if unresolved:
                    st.caption("Eligibility still unresolved: " + ", ".join(map(str, unresolved)))
            st.warning(
                "TRIAL MATCH IS NOT TRIAL ELIGIBILITY. Site status and patient-specific inclusion/exclusion criteria "
                "require direct study-team confirmation."
            )

    safety_output = specialist_outputs.get("safety")
    if safety_output is not None:
        with st.expander("Safety, contraindication, and monitoring evidence"):
            st.write(txt(val(safety_output, "summary")))
            findings = val(safety_output, "findings", []) or []
            if not findings:
                st.caption("No matched governed safety finding is represented. A non-match is not evidence of safety.")
            for finding in findings:
                block = " · BLOCKING" if val(finding, "recommendation_blocking", False) else ""
                st.write(f"**{human(val(finding, 'severity'))}{block}:** {txt(val(finding, 'safety_issue'))}")
                locator = txt(val(finding, "source_locator"), "")
                if locator:
                    st.caption(locator)


def _render_pdf_download(result: dict) -> None:
    try:
        pdf_bytes = build_tumor_board_pdf(result)
        case = result.get("case")
        case_id = txt(val(case, "case_id"), "case").replace(" ", "-")
        st.download_button(
            "Download governed tumor-board brief (PDF)",
            data=pdf_bytes,
            file_name=f"tumor-board-intelligence-{case_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="ag_pdf_download",
        )
        st.caption("The PDF is a presentation transform of the governed brief. It cannot add evidence or change a workflow gate.")
    except Exception as exc:
        st.caption(f"PDF export unavailable: {type(exc).__name__}. The on-screen governed brief remains available.")


def render_brief() -> None:
    result = st.session_state.ag_result
    if not result:
        goto("analysis")
        return

    brief = result.get("tumor_board_brief")
    final = result.get("final_decision")

    turn(
        "Tumor Board Agent · Decision brief",
        "This is the final governed decision-support artifact from the original tumor-board engine, presented conversationally. "
        "It preserves the primary strategy, alternatives, prerequisites, safety concerns, trial opportunities, unresolved questions, "
        "provenance, confidence boundary, limitations, and abstention state.",
        chips=[claim_chip("derived"), claim_chip("human")],
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Decision state", human(val(final, "decision_state")))
    c2.metric("Support", human(val(final, "decision_support_strength")))
    c3.metric("Source traces", val(brief, "source_trace_count", 0) or 0)
    c4.metric("Safe to display", "Yes" if val(brief, "safe_to_display", False) else "No")

    primary = txt(val(final, "primary_strategy"), "WITHHELD")
    st.markdown(
        '<div class="fx-thirty"><div class="fx-kicker">Decision-support headline</div>'
        f'<div class="fx-thirty-title">{escape(primary)}</div>'
        f'<div class="fx-thirty-sub">State: {escape(human(val(final, "decision_state")))} · '
        f'Support: {escape(human(val(final, "decision_support_strength")))}</div></div>',
        unsafe_allow_html=True,
    )

    abstention = txt(val(final, "abstention_reason"), "")
    if abstention:
        st.error("Abstention: " + abstention)

    _render_decision_dimensions(final)

    st.markdown("#### Full governed brief")
    if brief is not None:
        _render_brief_sections(brief)
    else:
        st.error("No tumor-board brief object was produced.")

    _render_trial_safety_boundaries(result)

    missing = result.get("missing_information_report")
    if missing is not None:
        with st.expander("Unresolved questions and missing information", expanded=bool(val(missing, "items", []))):
            st.write(txt(val(missing, "summary")))
            for item in val(missing, "items", []) or []:
                block = " · BLOCKING" if val(item, "recommendation_blocking", False) else ""
                st.write(f"**{txt(val(item, 'field'))}** · {human(val(item, 'priority'))}{block}")
                st.caption(txt(val(item, "reason")))

    audit = result.get("audit_events", []) or []
    with st.expander("Provenance and audit trail"):
        st.write(f"{len(audit)} workflow audit event(s) recorded.")
        for event in audit:
            event_name = txt(val(event, "event_type", val(event, "event", "event")))
            detail = txt(val(event, "detail", val(event, "message", "")), "")
            st.caption(f"{event_name} · {detail}")

    st.markdown("#### Export")
    _render_pdf_download(result)

    st.markdown("#### Ask Tumor Board")
    st.caption(
        "Follow-up answers are restricted to the current structured case and governed specialist outputs. "
        "The conversational layer cannot invent a new patient-specific recommendation from unrestricted model memory."
    )
    render_governed_chat(result, st.session_state.ag_case, key_prefix="agentic_brief")
