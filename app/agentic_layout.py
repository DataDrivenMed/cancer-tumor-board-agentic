from __future__ import annotations

from html import escape
from typing import Any, Iterable

import streamlit as st

from app.agentic_core import STAGES, STAGE_LABELS, human, source_ok, source_refs, txt, val
from services.oncology_programs import PROGRAM_BY_ID
from services.pathway_validation import get_pathway_validation_status


def chip(label: str, kind: str = "neutral") -> str:
    return f'<span class="chip {kind}">{escape(label)}</span>'


def claim_chip(kind: str) -> str:
    mapping = {
        "source": ("Source fact", "ok"),
        "retrieved": ("Retrieved evidence", "neutral"),
        "derived": ("Derived interpretation", "warn"),
        "human": ("Human judgment", "ok"),
    }
    label, css = mapping[kind]
    return chip(label, css)


def inject_structure_css() -> None:
    st.markdown(
        """
<style>
.agent-shell{max-width:1200px;margin:0 auto}.agent-hero{padding:6px 0 18px;border-bottom:1px solid var(--line);margin-bottom:20px}.agent-hero h1{font-size:46px;line-height:1.02;margin:6px 0 8px}.agent-hero p{max-width:820px;color:var(--body);font-size:15px;line-height:1.6;margin:0}
.agent-turn{display:flex;gap:12px;margin:0 0 17px}.agent-avatar{width:31px;height:31px;flex:none;border-radius:8px;display:grid;place-items:center;font:700 10px/1 var(--mono);background:var(--panelhi);border:1px solid var(--line);color:var(--accent2)}.agent-avatar.user{background:var(--accent);color:#231a13;border-color:var(--accent)}.agent-bubble{flex:1;min-width:0}.agent-who{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:4px 0 7px}.agent-text{font-size:14px;line-height:1.62;color:var(--body)}.user-msg{background:var(--panelhi);border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--ink)}
.workup-rail{display:flex;flex-direction:column;gap:3px}.rail-step{display:flex;gap:10px;align-items:center;padding:9px;border-radius:9px}.rail-step.active{background:var(--panelhi)}.rail-num{width:22px;height:22px;display:grid;place-items:center;flex:none;border:1px solid var(--line);border-radius:6px;font:700 9px/1 var(--mono);color:var(--muted)}.rail-step.done .rail-num{border-color:var(--mint);color:var(--mint);background:rgba(108,194,160,.1)}.rail-step.active .rail-num{border-color:var(--accent);background:var(--accent);color:#231a13}.rail-label{font-size:13px;color:var(--muted)}.rail-step.done .rail-label{color:var(--body)}.rail-step.active .rail-label{color:var(--ink);font-weight:600}
.fact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.fact-card{background:var(--panel2);border:1px solid var(--line2);border-radius:10px;padding:11px}.fact-key{font:600 9px/1.2 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.fact-value{font-size:14px;color:var(--ink);font-weight:600;margin-top:6px}.fact-meta{font-size:10.5px;color:var(--muted);margin-top:6px}
.guardrail{border:1px solid var(--warn);background:rgba(224,176,98,.07);border-radius:14px;padding:15px 16px;margin:10px 0 15px}.guardrail strong{color:var(--warn);font-size:13px}.guardrail p{margin:6px 0 0;font-size:12.5px;color:var(--body);line-height:1.55}
.evidence-card{border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:13px 14px;margin:8px 0}.evidence-title{color:var(--ink);font-size:13.5px;font-weight:600}.evidence-copy{color:var(--body);font-size:12.5px;line-height:1.55;margin-top:5px}.evidence-meta{font:500 10px/1.35 var(--mono);color:var(--muted);margin-top:7px}
.inspector{position:sticky;top:1rem}.inspect-head{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:0 0 9px}.inspect-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:9px}.inspect-row{display:flex;justify-content:space-between;gap:8px;padding:5px 0;border-bottom:1px solid var(--line2);font-size:11.5px}.inspect-row:last-child{border-bottom:0}.inspect-k{color:var(--muted)}.inspect-v{color:var(--ink);text-align:right;font-weight:600}.inspect-note{font-size:10.5px;line-height:1.45;color:var(--muted);margin-top:7px}
.brief-section{border:1px solid var(--line);background:var(--panel);border-radius:13px;padding:15px 16px;margin:10px 0}.brief-title{font-family:var(--serif);font-size:22px;color:var(--ink);font-weight:500}.brief-note{font-size:11.5px;color:var(--muted);margin:4px 0 10px}.brief-item{padding:9px 0;border-top:1px solid var(--line2)}.brief-label{font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.brief-value{font-size:13.5px;line-height:1.55;color:var(--body);margin-top:5px}.source-refs{font:500 9.5px/1.35 var(--mono);color:var(--mint);margin-top:5px}.legend{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 14px}.small-note{font-size:11px;color:var(--muted);line-height:1.5}
@media(max-width:1050px){.fact-grid{grid-template-columns:1fr}.agent-hero h1{font-size:40px}}
</style>
""",
        unsafe_allow_html=True,
    )


def turn(role: str, text: str, *, user: bool = False, chips: Iterable[str] = ()) -> None:
    chip_html = " ".join(chips)
    avatar = "YOU" if user else "TB"
    body_cls = "user-msg" if user else "agent-text"
    st.markdown(
        f'<div class="agent-turn"><div class="agent-avatar {"user" if user else ""}">{avatar}</div>'
        f'<div class="agent-bubble"><div class="agent-who">{escape(role)}</div>'
        f'<div class="{body_cls}">{text}</div><div class="legend">{chip_html}</div></div></div>',
        unsafe_allow_html=True,
    )


def sidebar(stage: str, reset_callback) -> None:
    current = STAGES.index(stage)
    with st.sidebar:
        st.markdown('<div class="fx-side-brand"><div class="fx-side-mark">TB</div><div><div class="fx-side-name">Tumor Board</div><div class="fx-side-sub">Agentic workup</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="fx-side-label">This workup</div>', unsafe_allow_html=True)
        rows = []
        for idx, item in enumerate(STAGES):
            css, num = "rail-step", str(idx + 1)
            if idx < current:
                css += " done"; num = "✓"
            elif idx == current:
                css += " active"
            rows.append(f'<div class="{css}"><span class="rail-num">{num}</span><span class="rail-label">{escape(STAGE_LABELS[item])}</span></div>')
        st.markdown('<div class="workup-rail">' + "".join(rows) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-note" style="margin:10px 3px 18px">The agent advances the workup. Human action is required only at explicit guardrails.</div>', unsafe_allow_html=True)
        st.markdown('<div class="fx-side-label">Reference</div>', unsafe_allow_html=True)
        st.page_link("pages/03_Architecture.py", label="Architecture", use_container_width=True)
        st.page_link("pages/01_Validation.py", label="Validation & scope", use_container_width=True)
        st.page_link("pages/02_About.py", label="About", use_container_width=True)
        st.markdown('<div class="fx-side-label">Alternative workflow</div>', unsafe_allow_html=True)
        st.page_link("pages/00_Clinical_Workspace.py", label="Classic Clinical Workspace", use_container_width=True)
        if st.button("Reset workup", use_container_width=True, key="ag_reset"):
            reset_callback()


def case_facts(case) -> None:
    program = PROGRAM_BY_ID.get(case.disease_program)
    program_label = program.display_name if program else human(case.disease_program)
    molecular = ", ".join(" ".join(x for x in [m.gene, m.alteration_type or m.hgvs_p or m.hgvs_c] if x) for m in case.molecular_findings[:3]) or "Not documented"
    facts = [
        ("Tumor board", program_label, None),
        ("Diagnosis", txt(case.diagnosis.value), case.diagnosis),
        ("Disease state", txt(case.disease_state.value), case.disease_state),
        ("Stage", txt(case.stage.value) if case.stage else "Not represented", case.stage),
        ("Patient", f"{case.age if case.age is not None else '?'} · {case.sex or 'sex not represented'}", None),
        ("Performance", txt(case.performance_status.value) if case.performance_status else "Not represented", case.performance_status),
        ("Molecular", molecular, case.molecular_findings[0] if case.molecular_findings else None),
        ("Question", case.clinical_question.question, None),
    ]
    html = []
    for key, value, item in facts:
        meta = ""
        if item is not None:
            refs = source_refs(item)
            meta = ("verified source" if source_ok(item) else "source review needed") + (f" · {len(refs)} trace(s)" if refs else "")
        html.append(f'<div class="fact-card"><div class="fact-key">{escape(key)}</div><div class="fact-value">{escape(txt(value))}</div><div class="fact-meta">{escape(meta)}</div></div>')
    st.markdown('<div class="fact-grid">' + "".join(html) + '</div>', unsafe_allow_html=True)


def inspector() -> None:
    case = st.session_state.ag_case
    result = st.session_state.ag_result or {}
    stage = st.session_state.ag_stage
    validation = get_pathway_validation_status(case.disease_program if case else None)
    routing = result.get("routing") if isinstance(result, dict) else None
    integrity = result.get("case_integrity_report") if isinstance(result, dict) else None
    missing = result.get("missing_information_report") if isinstance(result, dict) else None
    red = result.get("red_team_report") if isinstance(result, dict) else None
    consensus = result.get("consensus_report") if isinstance(result, dict) else None
    audit = result.get("audit_events", []) if isinstance(result, dict) else []
    runtime = st.session_state.ag_runtime_status or {}

    st.markdown('<div class="inspector"><div class="inspect-head">Live workup inspector</div>', unsafe_allow_html=True)
    st.markdown('<div class="inspect-card">'
        f'<div class="inspect-row"><span class="inspect-k">Stage</span><span class="inspect-v">{escape(STAGE_LABELS[stage])}</span></div>'
        f'<div class="inspect-row"><span class="inspect-k">Pathway</span><span class="inspect-v">{escape(validation.label)}</span></div>'
        f'<div class="inspect-row"><span class="inspect-k">Clinical validation</span><span class="inspect-v">{"Yes" if validation.clinically_validated else "No"}</span></div>'
        f'<div class="inspect-row"><span class="inspect-k">Common core</span><span class="inspect-v">{"Qualified" if validation.common_core_qualified else "Not qualified"}</span></div>'
        '<div class="inspect-note">Software qualification is not clinical validation. Decision support remains research-use only.</div></div>', unsafe_allow_html=True)

    if case is not None:
        source_items = [case.diagnosis, case.disease_state, case.stage, case.performance_status] + list(case.pathology) + list(case.imaging) + list(case.labs) + list(case.comorbidities) + list(case.toxicities)
        traceable = sum(1 for x in source_items if x is not None and source_ok(x))
        st.markdown('<div class="inspect-card"><div class="inspect-head">Case representation</div>'
            f'<div class="inspect-row"><span class="inspect-k">Source-traced facts</span><span class="inspect-v">{traceable}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Clinician review</span><span class="inspect-v">{"Confirmed" if st.session_state.ag_review_confirmed else "Pending"}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Case type</span><span class="inspect-v">{escape(human(case.case_type))}</span></div></div>', unsafe_allow_html=True)

    if runtime:
        rows = []
        for channel in ("guideline", "molecular", "translational", "safety", "pubmed", "clinical_trials"):
            status = runtime.get(channel, {}) or {}
            ready = status.get("ready", status.get("loaded", False))
            rows.append(f'<div class="inspect-row"><span class="inspect-k">{escape(channel.replace("_", " ").title())}</span><span class="inspect-v">{"Ready" if ready else "Fail closed"}</span></div>')
        st.markdown('<div class="inspect-card"><div class="inspect-head">Evidence runtime</div>' + "".join(rows) + '</div>', unsafe_allow_html=True)

    if result:
        selected = val(routing, "selected_agents", []) or []
        st.markdown('<div class="inspect-card"><div class="inspect-head">Safety gates</div>'
            f'<div class="inspect-row"><span class="inspect-k">Case integrity</span><span class="inspect-v">{escape(human(val(integrity, "disposition", "not run")))}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Missing info</span><span class="inspect-v">{escape(human(val(missing, "disposition", "not run")))}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Red team</span><span class="inspect-v">{escape(human(val(red, "disposition", val(red, "status", "not run"))))}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Consensus</span><span class="inspect-v">{escape(human(val(consensus, "decision_state", val(consensus, "status", "not run"))))}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Agents routed</span><span class="inspect-v">{len(selected)}</span></div>'
            f'<div class="inspect-row"><span class="inspect-k">Audit events</span><span class="inspect-v">{len(audit)}</span></div></div>', unsafe_allow_html=True)
        if audit:
            latest = audit[-1]
            st.markdown('<div class="inspect-card"><div class="inspect-head">Latest audit event</div>'
                f'<div class="inspect-note">{escape(txt(val(latest, "event_type", val(latest, "event", "event"))))}<br>{escape(txt(val(latest, "detail", val(latest, "message", "")), ""))}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
