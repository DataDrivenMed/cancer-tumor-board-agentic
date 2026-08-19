from __future__ import annotations

from html import escape

import streamlit as st

from app.agentic_core import STAGE_LABELS, initialize_state, reset_workup
from app.agentic_layout import inject_structure_css, inspector, sidebar, status_strip
from app.agentic_stages_case import render_evidence, render_intake, render_review
from app.agentic_stages_output import render_analysis, render_brief
from app.xai_theme import inject_xai_theme
from services.pathway_validation import COMMON_CORE_QUALIFICATION


def _onboarding() -> None:
    if not st.session_state.get("ag_onboarding_open", True):
        return
    with st.expander("New here? · 30-second guided overview", expanded=True):
        st.markdown(
            """
**The goal:** prepare a more complete tumor-board case, faster, while seeing exactly what the AI did and where clinician judgment is still required.

1. **Provide a de-identified case.** Paste a narrative, upload a document, or use the guided synthetic demonstration.
2. **Confirm the structured case.** The agent shows diagnosis, disease state, treatment history, molecular findings, conflicts, missing information, and source traces.
3. **Review evidence.** Evidence channels stay separate; some retrieved records require explicit clinician attestation before patient-level use.
4. **Let the agents work.** Integrity checks, specialist agents, safety/challenge review, and consensus run under the conversational surface.
5. **Prepare the board discussion.** The final brief shows the strategy, alternatives, evidence, safety, trials, missing information, uncertainty, and questions the board still needs to decide.
            """
        )
        if st.button("Got it · hide this guide", use_container_width=True, key="ag_hide_onboarding"):
            st.session_state.ag_onboarding_open = False
            st.rerun()


def render_agentic_home() -> None:
    initialize_state()
    inject_xai_theme()
    inject_structure_css()
    stage = st.session_state.ag_stage
    sidebar(stage, reset_workup)

    st.markdown(
        '<div class="agent-shell"><div class="agent-hero"><div class="fx-kicker">Tumor Board Intelligence · Guided mode</div>'
        '<h1>Prepare a more complete tumor-board case, faster.</h1>'
        '<p>The agent structures the case, gathers bounded evidence, checks what is missing, routes the right specialists, '
        'challenges its own synthesis, and prepares a board-ready brief—while showing you exactly where human judgment is still required.</p>'
        '<div class="agent-value"><span>Save preparation time</span><span>Catch missing information</span>'
        '<span>Organize board discussion</span><span>Make AI behavior inspectable</span></div></div></div>',
        unsafe_allow_html=True,
    )

    status_strip()
    if stage == "intake":
        _onboarding()

    main, right = st.columns([2.32, 0.92], gap="large")
    with main:
        if stage == "intake":
            render_intake()
        elif stage == "review":
            render_review()
        elif stage == "evidence":
            render_evidence()
        elif stage == "analysis":
            render_analysis()
        elif stage == "brief":
            render_brief()
        else:
            st.error(f"Unknown workup stage: {STAGE_LABELS.get(stage, stage)}")
    with right:
        inspector()

    result = str(COMMON_CORE_QUALIFICATION.get("result", "not represented")).upper()
    build = str(COMMON_CORE_QUALIFICATION.get("qualified_build", "not represented"))
    st.markdown(
        '<div class="fx-footer"><div>Research / software qualification use · de-identified cases only in this public deployment</div>'
        f'<div>Common-core qualification: {escape(result)} · build {escape(build)}</div></div>',
        unsafe_allow_html=True,
    )
