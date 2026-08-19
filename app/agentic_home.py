from __future__ import annotations

from html import escape

import streamlit as st

from app.agentic_core import STAGE_LABELS, initialize_state, reset_workup
from app.agentic_layout import inject_structure_css, inspector, sidebar
from app.agentic_stages_case import render_evidence, render_intake, render_review
from app.agentic_stages_output import render_analysis, render_brief
from app.xai_theme import inject_xai_theme
from services.pathway_validation import COMMON_CORE_QUALIFICATION


def render_agentic_home() -> None:
    initialize_state()
    inject_xai_theme()
    inject_structure_css()
    stage = st.session_state.ag_stage
    sidebar(stage, reset_workup)

    st.markdown(
        '<div class="agent-shell"><div class="agent-hero"><div class="fx-kicker">Agentic tumor board intelligence</div>'
        '<h1>Full logic, cleaner conversation.</h1><p>The conversational surface is simple. Underneath it, the original tumor-board engine preserves provenance, deterministic integrity gates, missing-information blocking, evidence commissioning, specialist routing, clinical red-team challenge, consensus adjudication, abstention, and an auditable final brief.</p></div></div>',
        unsafe_allow_html=True,
    )

    main, right = st.columns([2.25, 0.95], gap="large")
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
        '<div class="fx-footer"><div>Research / software qualification use · not clinically validated for autonomous patient-care decisions</div>'
        f'<div>Common-core qualification: {escape(result)} · build {escape(build)}</div></div>',
        unsafe_allow_html=True,
    )
