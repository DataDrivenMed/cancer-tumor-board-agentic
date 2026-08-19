from __future__ import annotations

from html import escape

import streamlit as st

from app.agentic_core import goto, human, run_guarded_workflow, txt, val
from app.agentic_layout import claim_chip, turn
from app.chat_ui import render_governed_chat


def _render_specialist_outputs(result: dict) -> None:
    outputs = result.get("specialist_outputs", {}) or {}
    if not outputs:
        st.info("No specialist outputs were produced because a pre-routing guardrail may have stopped the workflow.")
        return
    for agent_id, output in outputs.items():
        with st.expander(f"{agent_id.replace('_', ' ').title()} · {human(val(output, 'status'))}"):
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


def render_analysis() -> None:
    if not st.session_state.ag_evidence_confirmed:
        goto("evidence")
        return
    if st.session_state.ag_result is None:
        try:
            with st.status("Running guarded multi-agent tumor-board workflow...", expanded=True) as status:
                status.write("Configuring fail-closed evidence channels")
                status.write("Checking semantic integrity, case integrity, conflicts, and missing information")
                status.write("Routing specialist agents and gathering evidence")
                status.write("Running synthesis, clinical red team, consensus, and decision-brief gates")
                result = run_guarded_workflow()
                status.update(label="Guarded analysis complete", state="complete")
        except Exception as exc:
            st.error(f"Workflow stopped safely: {type(exc).__name__}: {exc}")
            return
    else:
        result = st.session_state.ag_result

    turn(
        "Tumor Board Agent · Analysis",
        "The full workflow has run. Below are the actual specialist outputs, deterministic safety gates, synthesis, red-team challenge, and consensus. A pre-routing failure produces an abstention brief instead of management synthesis.",
        chips=[claim_chip("retrieved"), claim_chip("derived")],
    )
    _render_specialist_outputs(result)
    st.markdown("#### Preliminary synthesis")
    st.write(txt(result.get("preliminary_synthesis"), "No preliminary synthesis was produced."))

    red_team = result.get("red_team_report")
    findings = result.get("red_team_findings", []) or []
    with st.expander("Clinical red-team challenge", expanded=True):
        if red_team is not None:
            st.write(txt(val(red_team, "summary")))
        if not findings:
            st.caption("No red-team findings represented.")
        for finding in findings:
            st.markdown(f"**{human(val(finding, 'severity'))}:** {txt(val(finding, 'issue'))}")
            effect = txt(val(finding, "effect_on_recommendation"), "")
            if effect:
                st.caption(effect)

    consensus = result.get("consensus_report")
    with st.expander("Consensus adjudication", expanded=True):
        if consensus is None:
            st.info("Consensus was not run because an earlier safety gate stopped the workflow.")
        else:
            st.write(txt(val(consensus, "summary")))
            try:
                st.json(consensus.model_dump(mode="json"), expanded=False)
            except Exception:
                pass

    integrity = result.get("case_integrity_report")
    if integrity is not None:
        with st.expander("Case integrity gate"):
            st.write(txt(val(integrity, "summary")))
            for finding in val(integrity, "findings", []) or []:
                block = " · BLOCKING" if val(finding, "recommendation_blocking", False) else ""
                st.write(f"**{txt(val(finding, 'code'))}** · {human(val(finding, 'severity'))}{block}")
                st.caption(txt(val(finding, "message")))

    semantic = result.get("semantic_integrity_findings", []) or []
    if semantic:
        with st.expander("Semantic integrity findings"):
            for finding in semantic:
                st.write(f"**{human(val(finding, 'severity'))}:** {txt(val(finding, 'message'))}")

    missing = result.get("missing_information_report")
    if missing is not None and (val(missing, "items", []) or []):
        st.markdown('<div class="guardrail"><strong>Unresolved decision-critical information</strong><p>The backend identified missing, conflicting, pending, or unavailable information. Recommendation-blocking items remain blocking regardless of conversational fluency.</p></div>', unsafe_allow_html=True)
        with st.expander("Missing-information report", expanded=True):
            st.write(txt(val(missing, "summary")))
            for item in val(missing, "items", []) or []:
                block = " · BLOCKING" if val(item, "recommendation_blocking", False) else ""
                st.write(f"**{txt(val(item, 'field'))}** · {human(val(item, 'priority'))}{block}")
                st.caption(txt(val(item, "reason")))

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
    st.markdown('<div class="legend">' + claim_chip("source") + claim_chip("retrieved") + claim_chip("derived") + claim_chip("human") + '</div>', unsafe_allow_html=True)
    for section in val(brief, "sections", []) or []:
        items_html = []
        for item in val(section, "items", []) or []:
            category = claim_chip(_brief_category(txt(val(item, "epistemic_label"), "")))
            refs = val(item, "source_refs", []) or []
            limitations = val(item, "limitations", []) or []
            refs_html = f'<div class="source-refs">Sources: {escape(", ".join(map(str, refs)))}</div>' if refs else ""
            lim_html = f'<div class="brief-note">Limitations: {escape(" · ".join(map(str, limitations)))}</div>' if limitations else ""
            items_html.append('<div class="brief-item">'
                f'<div class="brief-label">{escape(txt(val(item, "label")))}</div>'
                f'<div class="brief-value">{escape(txt(val(item, "value")))}</div>'
                f'<div class="legend">{category}</div>{refs_html}{lim_html}</div>')
        note = txt(val(section, "section_note"), "")
        st.markdown('<div class="brief-section">'
            f'<div class="brief-title">{escape(txt(val(section, "title")))}</div>'
            f'<div class="brief-note">{escape(note)}</div>' + "".join(items_html) + '</div>', unsafe_allow_html=True)


def render_brief() -> None:
    result = st.session_state.ag_result
    if not result:
        goto("analysis")
        return
    brief = result.get("tumor_board_brief")
    final = result.get("final_decision")

    turn(
        "Tumor Board Agent · Decision brief",
        "This is the full governed tumor-board decision-support artifact. It preserves alternatives, conditions, uncertainties, missing information, evidence traceability, and any abstention. It is not an autonomous treatment order.",
        chips=[claim_chip("derived"), claim_chip("human")],
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Decision state", human(val(final, "decision_state")))
    c2.metric("Support", human(val(final, "decision_support_strength")))
    c3.metric("Source traces", val(brief, "source_trace_count", 0) or 0)
    c4.metric("Safe to display", "Yes" if val(brief, "safe_to_display", False) else "No")

    primary = txt(val(final, "primary_strategy"), "WITHHELD")
    st.markdown('<div class="fx-thirty"><div class="fx-kicker">Decision-support headline</div>'
        f'<div class="fx-thirty-title">{escape(primary)}</div>'
        f'<div class="fx-thirty-sub">State: {escape(human(val(final, "decision_state")))} · Support: {escape(human(val(final, "decision_support_strength")))}</div></div>', unsafe_allow_html=True)

    alternatives = val(final, "alternatives", []) or []
    conditions = val(final, "conditions", []) or []
    uncertainties = val(final, "major_uncertainties", []) or []
    priorities = val(final, "discussion_priorities", []) or []
    if alternatives:
        st.markdown("#### Alternatives")
        for item in alternatives:
            st.write("• " + txt(item))
    if conditions:
        st.markdown("#### Conditions / prerequisites")
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
    abstention = txt(val(final, "abstention_reason"), "")
    if abstention:
        st.error("Abstention: " + abstention)

    if brief is not None:
        _render_brief_sections(brief)
    else:
        st.error("No tumor-board brief object was produced.")

    specialist_outputs = result.get("specialist_outputs", {}) or {}
    trial_output = specialist_outputs.get("clinical_trials")
    if trial_output is not None:
        with st.expander("Trial opportunities and eligibility boundary"):
            st.write(txt(val(trial_output, "summary")))
            for match in val(trial_output, "matches", []) or []:
                st.write(f"**{txt(val(match, 'nct_id'))}:** {txt(val(match, 'title'))}")
                st.caption(txt(val(match, "rationale")))
            st.warning("TRIAL MATCH IS NOT TRIAL ELIGIBILITY. Site status and patient-specific inclusion/exclusion criteria require direct study-team confirmation.")

    safety_output = specialist_outputs.get("safety")
    if safety_output is not None:
        with st.expander("Safety / contraindication evidence"):
            st.write(txt(val(safety_output, "summary")))
            for finding in val(safety_output, "findings", []) or []:
                block = " · BLOCKING" if val(finding, "recommendation_blocking", False) else ""
                st.write(f"**{human(val(finding, 'severity'))}{block}:** {txt(val(finding, 'safety_issue'))}")
                st.caption(txt(val(finding, "source_locator"), ""))

    missing = result.get("missing_information_report")
    if missing is not None:
        with st.expander("Unresolved questions / missing information", expanded=bool(val(missing, "items", []))):
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

    st.markdown("#### Ask Tumor Board")
    st.caption("Follow-up answers are grounded in the current governed case and specialist outputs. They do not create a separate recommendation from unrestricted model memory.")
    render_governed_chat(result, st.session_state.ag_case, key_prefix="agentic_brief")
