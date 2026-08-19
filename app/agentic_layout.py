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
        "retrieved": ("External evidence", "neutral"),
        "derived": ("System interpretation", "warn"),
        "human": ("Clinician judgment", "ok"),
    }
    label, css = mapping[kind]
    return chip(label, css)


def support_label(value: Any) -> str:
    raw = str(getattr(value, "value", value) or "").lower().strip()
    if raw in {"strong", "high", "well_supported", "well-supported"}:
        return "Strong support"
    if raw in {"moderate", "partial", "medium", "conditional"}:
        return "Partial support"
    if raw in {"insufficient", "low", "none", "withheld", "abstain", ""}:
        return "Insufficient evidence"
    return human(raw)


def inject_structure_css() -> None:
    st.markdown(
        """
<style>
.agent-shell{max-width:1280px;margin:0 auto}
.agent-hero{padding:8px 0 22px;border-bottom:1px solid var(--line);margin-bottom:18px}
.agent-hero h1{font-size:3.1rem;line-height:1.01;margin:7px 0 10px}
.agent-hero p{max-width:930px;color:var(--body);font-size:1.05rem;line-height:1.66;margin:0}
.agent-value{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}.agent-value span{font-size:.8rem;color:var(--muted);border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:6px 9px}
.status-strip{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px;margin:0 0 18px}.status-cell{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:10px 12px}.status-k{font:600 .66rem/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.status-v{font-size:.9rem;color:var(--ink);font-weight:650;margin-top:6px}.status-v.ok{color:var(--mint)!important}.status-v.warn{color:var(--warn)!important}.status-v.bad{color:var(--danger)!important}
.stage-guide{border:1px solid var(--linehi);background:linear-gradient(135deg,var(--panelhi),var(--panel));border-radius:16px;padding:17px 18px;margin:0 0 18px}.stage-guide-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.stage-guide-label{font:600 .67rem/1 var(--mono);text-transform:uppercase;letter-spacing:.09em;color:var(--accent2);margin-bottom:6px}.stage-guide-title{font-family:var(--serif);font-size:1.35rem;color:var(--ink);font-weight:500}.stage-guide-copy{font-size:.93rem;color:var(--body);line-height:1.55;margin-top:4px}.stage-guide-next{border-left:2px solid var(--accent);padding-left:12px}
.agent-turn{display:flex;gap:13px;margin:0 0 20px}.agent-avatar{width:35px;height:35px;flex:none;border-radius:9px;display:grid;place-items:center;font:700 .65rem/1 var(--mono);background:var(--panelhi);border:1px solid var(--line);color:var(--accent2)}.agent-avatar.user{background:var(--accent);color:#231a13;border-color:var(--accent)}.agent-bubble{flex:1;min-width:0}.agent-who{font:600 .68rem/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:5px 0 8px}.agent-text{font-size:1rem;line-height:1.68;color:var(--body)}.user-msg{background:var(--panelhi);border:1px solid var(--line);border-radius:12px;padding:13px 15px;color:var(--ink);font-size:1rem;line-height:1.62}
.workup-rail{display:flex;flex-direction:column;gap:4px}.rail-step{display:flex;gap:10px;align-items:center;padding:10px;border-radius:10px}.rail-step.active{background:var(--panelhi)}.rail-num{width:25px;height:25px;display:grid;place-items:center;flex:none;border:1px solid var(--line);border-radius:7px;font:700 .63rem/1 var(--mono);color:var(--muted)}.rail-step.done .rail-num{border-color:var(--mint);color:var(--mint);background:rgba(108,194,160,.1)}.rail-step.active .rail-num{border-color:var(--accent);background:var(--accent);color:#231a13}.rail-label{font-size:.9rem;color:var(--muted)}.rail-step.done .rail-label{color:var(--body)}.rail-step.active .rail-label{color:var(--ink);font-weight:650}
.fact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.fact-card{background:var(--panel2);border:1px solid var(--line2);border-radius:11px;padding:13px}.fact-key{font:600 .67rem/1.2 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.fact-value{font-size:1rem;color:var(--ink);font-weight:650;margin-top:7px;line-height:1.4}.fact-meta{font-size:.78rem;color:var(--muted);margin-top:7px}
.guardrail{border:1px solid var(--warn);background:rgba(224,176,98,.07);border-radius:14px;padding:16px 17px;margin:11px 0 16px}.guardrail strong{color:var(--warn);font-size:.95rem}.guardrail p{margin:7px 0 0;font-size:.9rem;color:var(--body);line-height:1.58}.clinical-takeaway{border:1px solid rgba(108,194,160,.28);background:rgba(108,194,160,.07);border-radius:14px;padding:15px 16px;margin:13px 0}.clinical-takeaway strong{color:var(--mint);font-size:.92rem}.clinical-takeaway p{font-size:.9rem;margin:6px 0 0;color:var(--body);line-height:1.55}
.action-card{border:1px solid var(--line);background:var(--panel);border-radius:15px;padding:16px;min-height:142px;margin-bottom:8px}.action-card.selected{border-color:var(--accent);background:var(--panelhi)}.action-icon{font-size:1.3rem;margin-bottom:9px}.action-title{font-family:var(--serif);font-size:1.25rem;color:var(--ink);font-weight:500}.action-copy{font-size:.86rem;color:var(--muted);line-height:1.5;margin-top:6px}.action-step{font:600 .64rem/1 var(--mono);text-transform:uppercase;letter-spacing:.09em;color:var(--accent2);margin-bottom:7px}
.review-nav{border-right:1px solid var(--line);padding-right:12px}.review-nav-note{font-size:.8rem;color:var(--muted);line-height:1.5;margin:4px 0 11px}.timeline{border-left:2px solid var(--linehi);margin:8px 0 0 8px;padding-left:18px}.timeline-item{position:relative;padding:0 0 18px}.timeline-item:before{content:"";position:absolute;left:-24px;top:5px;width:10px;height:10px;border-radius:50%;background:var(--accent);border:2px solid var(--bg)}.timeline-date{font:600 .66rem/1 var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.timeline-title{font-size:.97rem;color:var(--ink);font-weight:650;margin-top:5px}.timeline-copy{font-size:.84rem;color:var(--body);line-height:1.5;margin-top:3px}
.evidence-card{border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:14px 15px;margin:8px 0}.evidence-title{color:var(--ink);font-size:.98rem;font-weight:650}.evidence-copy{color:var(--body);font-size:.9rem;line-height:1.58;margin-top:6px}.evidence-meta{font:500 .68rem/1.4 var(--mono);color:var(--muted);margin-top:8px}.evidence-tier{display:inline-flex;border-radius:999px;padding:4px 7px;font:600 .62rem/1 var(--mono);text-transform:uppercase;letter-spacing:.05em;background:var(--panel2);border:1px solid var(--line);color:var(--accent2)}
.inspector{position:sticky;top:1rem}.inspect-head{font:600 .68rem/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:0 0 9px}.inspect-card{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:13px;margin-bottom:10px}.inspect-card.primary{border-color:var(--linehi);background:var(--panelhi)}.inspect-row{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid var(--line2);font-size:.83rem}.inspect-row:last-child{border-bottom:0}.inspect-k{color:var(--muted)}.inspect-v{color:var(--ink);text-align:right;font-weight:650;max-width:58%}.inspect-v.okv{color:var(--mint)}.inspect-v.warnv{color:var(--warn)}.inspect-v.badv{color:var(--danger)}.inspect-note{font-size:.78rem;line-height:1.5;color:var(--muted);margin-top:8px}.inspect-legend{display:flex;gap:4px;flex-wrap:wrap;margin-top:8px}
.activity{display:flex;gap:9px;padding:7px 0;border-bottom:1px solid var(--line2)}.activity:last-child{border-bottom:0}.activity-icon{width:19px;flex:none;font-weight:700;color:var(--muted)}.activity-icon.ok{color:var(--mint)!important}.activity-icon.warn{color:var(--warn)!important}.activity-icon.bad{color:var(--danger)!important}.activity-body{min-width:0}.activity-title{font-size:.82rem;color:var(--ink);font-weight:650}.activity-copy{font-size:.73rem;color:var(--muted);line-height:1.43;margin-top:2px}
.brief-section{border:1px solid var(--line);background:var(--panel);border-radius:13px;padding:16px 17px;margin:10px 0}.brief-title{font-family:var(--serif);font-size:1.45rem;color:var(--ink);font-weight:500}.brief-note{font-size:.84rem;color:var(--muted);margin:5px 0 11px;line-height:1.5}.brief-item{padding:11px 0;border-top:1px solid var(--line2)}.brief-label{font:600 .67rem/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.brief-value{font-size:.96rem;line-height:1.58;color:var(--body);margin-top:6px}.source-refs{font:500 .67rem/1.4 var(--mono);color:var(--mint);margin-top:6px}.legend{display:flex;gap:6px;flex-wrap:wrap;margin:7px 0 14px}.small-note{font-size:.8rem;color:var(--muted);line-height:1.52}
.logic-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0 0 18px}.logic-cell{border:1px solid var(--line2);background:var(--panel2);border-radius:10px;padding:11px 12px}.logic-k{font:600 .66rem/1 var(--mono);text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}.logic-v{font-size:.9rem;color:var(--ink);font-weight:650;margin-top:6px}
.board-agenda{counter-reset:item;margin:8px 0}.board-agenda-item{display:flex;gap:12px;padding:11px 0;border-bottom:1px solid var(--line2)}.board-agenda-num{width:27px;height:27px;border-radius:7px;background:var(--panelhi);border:1px solid var(--line);display:grid;place-items:center;color:var(--accent2);font:700 .68rem/1 var(--mono)}.board-agenda-copy{font-size:.95rem;color:var(--body);line-height:1.55;flex:1}
@media(max-width:1100px){.fact-grid{grid-template-columns:1fr}.agent-hero h1{font-size:2.5rem}.logic-strip{grid-template-columns:repeat(2,1fr)}.status-strip{grid-template-columns:repeat(2,1fr)}.stage-guide-grid{grid-template-columns:1fr}}
@media(max-width:720px){.logic-strip,.status-strip{grid-template-columns:1fr}}
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


def stage_guidance(title: str, now: str, next_action: str, why: str = "") -> None:
    why_html = f'<div class="stage-guide-copy">{escape(why)}</div>' if why else ""
    st.markdown(
        '<div class="stage-guide"><div class="stage-guide-grid">'
        f'<div><div class="stage-guide-label">You are here</div><div class="stage-guide-title">{escape(title)}</div>'
        f'<div class="stage-guide-copy">{escape(now)}</div></div>'
        f'<div class="stage-guide-next"><div class="stage-guide-label">What to do next</div>'
        f'<div class="stage-guide-title">{escape(next_action)}</div>{why_html}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def status_strip() -> None:
    case = st.session_state.get("ag_case")
    result = st.session_state.get("ag_result") or {}
    review = bool(st.session_state.get("ag_review_confirmed"))
    evidence = bool(st.session_state.get("ag_evidence_confirmed"))
    missing = result.get("missing_information_report") if isinstance(result, dict) else None
    final = result.get("final_decision") if isinstance(result, dict) else None
    case_state = "Confirmed" if review else ("Needs review" if case is not None else "Not started")
    evidence_state = "Reviewed" if evidence else ("Pending" if review else "Not started")
    if missing is not None:
        gaps = int(val(missing, "blocking_count", 0) or 0)
    elif case is not None:
        gaps = sum(1 for item in (case.missing_items or []) if val(item, "recommendation_blocking", False))
    else:
        gaps = 0
    decision_state = human(val(final, "decision_state", "Pending")) if final else "Pending"
    support = support_label(val(final, "decision_support_strength", "")) if final else "Not assessed"
    cells = [("Case", case_state, "ok" if review else "warn"),("Evidence", evidence_state, "ok" if evidence else "warn"),("Blocking gaps", str(gaps), "bad" if gaps else "ok"),("Decision", decision_state, "warn" if decision_state in {"Pending", "Abstain"} else "ok"),("Support", support, "warn" if support != "Strong support" else "ok")]
    html = "".join(f'<div class="status-cell"><div class="status-k">{escape(k)}</div><div class="status-v {css}">{escape(v)}</div></div>' for k,v,css in cells)
    st.markdown('<div class="status-strip">'+html+'</div>', unsafe_allow_html=True)


def sidebar(stage: str, reset_callback) -> None:
    current = STAGES.index(stage)
    with st.sidebar:
        st.markdown('<div class="fx-side-brand"><div class="fx-side-mark">TB</div><div><div class="fx-side-name">Tumor Board Intelligence</div><div class="fx-side-sub">Governed agentic workup</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="fx-side-label">This workup</div>', unsafe_allow_html=True)
        rows=[]
        for idx,item in enumerate(STAGES):
            css,num="rail-step",str(idx+1)
            if idx<current: css+=" done"; num="✓"
            elif idx==current: css+=" active"
            rows.append(f'<div class="{css}"><span class="rail-num">{num}</span><span class="rail-label">{escape(STAGE_LABELS[item])}</span></div>')
        st.markdown('<div class="workup-rail">'+"".join(rows)+'</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-note" style="margin:11px 3px 18px">The agent handles evidence gathering and synthesis. You intervene at explicit confirmation, evidence-attestation, conflict-resolution, and final judgment checkpoints.</div>', unsafe_allow_html=True)
        st.markdown('<div class="fx-side-label">Trust & reference</div>', unsafe_allow_html=True)
        st.page_link("pages/01_Validation.py", label="Validation & scope", use_container_width=True)
        st.page_link("pages/03_Architecture.py", label="Architecture", use_container_width=True)
        st.page_link("pages/02_About.py", label="Scientific scope", use_container_width=True)
        st.markdown('<div class="fx-side-label">Controls</div>', unsafe_allow_html=True)
        if st.button("Reset workup", use_container_width=True, key="ag_reset"): reset_callback()


def case_facts(case) -> None:
    program=PROGRAM_BY_ID.get(case.disease_program); program_label=program.display_name if program else human(case.disease_program)
    molecular=", ".join(" ".join(x for x in [m.gene,m.alteration_type or m.hgvs_p or m.hgvs_c] if x) for m in case.molecular_findings[:3]) or "Not documented"
    facts=[("Tumor board",program_label,None),("Diagnosis",txt(case.diagnosis.value),case.diagnosis),("Disease state",txt(case.disease_state.value),case.disease_state),("Stage",txt(case.stage.value) if case.stage else "Not represented",case.stage),("Patient",f"{case.age if case.age is not None else '?'} · {case.sex or 'sex not represented'}",None),("Performance status",txt(case.performance_status.value) if case.performance_status else "Not represented",case.performance_status),("Molecular profile",molecular,case.molecular_findings[0] if case.molecular_findings else None),("Board question",case.clinical_question.question,None)]
    html=[]
    for key,value,item in facts:
        meta=""
        if item is not None:
            refs=source_refs(item); meta=("Verified source" if source_ok(item) else "Source review needed")+(f" · {len(refs)} trace(s)" if refs else "")
        html.append(f'<div class="fact-card"><div class="fact-key">{escape(key)}</div><div class="fact-value">{escape(txt(value))}</div><div class="fact-meta">{escape(meta)}</div></div>')
    st.markdown('<div class="fact-grid">'+"".join(html)+'</div>', unsafe_allow_html=True)


def logic_strip(result: dict[str, Any]) -> None:
    routing=result.get("routing"); integrity=result.get("case_integrity_report"); missing=result.get("missing_information_report"); final=result.get("final_decision")
    values=[("Case integrity",human(val(integrity,"disposition","Not run"))),("Missing information",human(val(missing,"disposition","Not run"))),("Specialists used",str(len(val(routing,"selected_agents",[]) or []))),("Decision support",support_label(val(final,"decision_support_strength","insufficient")))]
    html="".join(f'<div class="logic-cell"><div class="logic-k">{escape(k)}</div><div class="logic-v">{escape(v)}</div></div>' for k,v in values)
    st.markdown('<div class="logic-strip">'+html+'</div>', unsafe_allow_html=True)


def _runtime_ready(status: dict[str, Any]) -> bool:
    return bool(status.get("ready",status.get("loaded",False)))


def _agent_consequence(agent_id: str, output: Any) -> tuple[str,str,str]:
    labels={"guideline":"Guideline evidence","molecular":"Molecular interpretation","safety":"Safety review","literature":"Literature review","clinical_trials":"Clinical trials","translational":"Translational biology"}; label=labels.get(agent_id,human(agent_id)); status=str(getattr(val(output,"status",""),"value",val(output,"status","")) or "").lower()
    if not output: return "○",label,"Not required or not yet run."
    if status in {"source_unavailable","tool_failure","error","failed"}:
        consequence={"literature":"Literature-dependent support is withheld.","translational":"Mechanistic support is unavailable and cannot strengthen the decision.","safety":"Safety-dependent claims are withheld; absence of a result is not evidence of safety.","clinical_trials":"No trial claim is made from this channel.","guideline":"Formal guideline support is unavailable.","molecular":"Patient-level molecular actionability is withheld."}.get(agent_id,"Dependent claims are withheld.")
        return "!",label,consequence
    if status in {"not_selected","not selected"}: return "○",label,"Not selected for this clinical question."
    if status in {"no_evidence","no evidence","no_match","no match"}: return "–",label,"No bounded match was found; this is not proof that no option or hazard exists."
    return "✓",label,"Completed within its governed evidence boundary."


def _activity_html(result: dict[str,Any]) -> str:
    if not result: return '<div class="activity"><div class="activity-icon">○</div><div class="activity-body"><div class="activity-title">Agent workflow</div><div class="activity-copy">Starts after case and evidence review.</div></div></div>'
    rows=[]; integrity=result.get("case_integrity_report"); missing=result.get("missing_information_report"); red=result.get("red_team_report"); consensus=result.get("consensus_report")
    integrity_ok=bool(val(integrity,"safe_to_route_to_specialists",False)) if integrity is not None else False; rows.append(("✓" if integrity_ok else "!","Case integrity","ok" if integrity_ok else "bad","Case representation passed routing checks." if integrity_ok else "Routing was stopped or constrained by case-integrity findings."))
    missing_ok=bool(val(missing,"safe_to_route_to_specialists",False)) if missing is not None else False; rows.append(("✓" if missing_ok else "!","Missing information","ok" if missing_ok else "bad","No recommendation-blocking gap prevented routing." if missing_ok else "Decision-critical information blocked or constrained analysis."))
    outputs=result.get("specialist_outputs",{}) or {}
    for key in ("guideline","molecular","safety","literature","clinical_trials","translational"):
        icon,label,consequence=_agent_consequence(key,outputs.get(key)); css="ok" if icon=="✓" else ("bad" if icon=="!" else "warn"); rows.append((icon,label,css,consequence))
    if red is not None:
        safe=bool(val(red,"safe_for_consensus",False)); rows.append(("✓" if safe else "!","Safety & challenge review","ok" if safe else "bad","No recommendation-blocking challenge remained." if safe else "A recommendation-blocking challenge prevented normal consensus."))
    if consensus is not None:
        state=human(val(consensus,"decision_state","Not established")); rows.append(("✓" if state not in {"Abstain","Not Established"} else "!","Tumor board decision status","ok" if state not in {"Abstain","Not Established"} else "warn",f"Adjudicated state: {state}."))
    return "".join(f'<div class="activity"><div class="activity-icon {css}">{escape(icon)}</div><div class="activity-body"><div class="activity-title">{escape(label)}</div><div class="activity-copy">{escape(copy)}</div></div></div>' for icon,label,css,copy in rows)


def inspector() -> None:
    case=st.session_state.get("ag_case"); result=st.session_state.get("ag_result") or {}; stage=st.session_state.get("ag_stage","intake"); validation=get_pathway_validation_status(case.disease_program if case else None); runtime=st.session_state.get("ag_runtime_status") or {}; evidence=st.session_state.get("ag_evidence_summary",{}) or {}
    st.markdown('<div class="inspector"><div class="inspect-head">Live workup inspector</div>', unsafe_allow_html=True)
    mode=st.segmented_control("Inspector view",["Clinical","Technical / Governance"],key="ag_inspector_mode",label_visibility="collapsed") or "Clinical"
    if mode=="Clinical":
        final=result.get("final_decision") if isinstance(result,dict) else None; missing=result.get("missing_information_report") if isinstance(result,dict) else None; red=result.get("red_team_report") if isinstance(result,dict) else None; brief=result.get("tumor_board_brief") if isinstance(result,dict) else None
        current_copy={"intake":"Start with a de-identified case or the guided demonstration.","review":"Confirm that the structured case matches the source before evidence gathering.","evidence":"Review what evidence is usable and attest only the source records you accept.","analysis":"Watch the governed agents analyze, challenge, and adjudicate the case.","brief":"Use the final brief to prepare the board discussion and identify remaining judgment calls."}[stage]
        st.markdown('<div class="inspect-card primary"><div class="inspect-head">What matters now</div>'+f'<div class="inspect-row"><span class="inspect-k">Stage</span><span class="inspect-v">{escape(STAGE_LABELS[stage])}</span></div><div class="inspect-note">{escape(current_copy)}</div></div>', unsafe_allow_html=True)
        if case is not None:
            blocking=int(val(missing,"blocking_count",0) or 0) if missing is not None else sum(1 for x in (case.missing_items or []) if val(x,"recommendation_blocking",False))
            review_cls="okv" if st.session_state.get("ag_review_confirmed") else "warnv"; evidence_cls="okv" if st.session_state.get("ag_evidence_confirmed") else "warnv"; gap_cls="badv" if blocking else "okv"
            st.markdown('<div class="inspect-card"><div class="inspect-head">Clinical readiness</div>'+f'<div class="inspect-row"><span class="inspect-k">Case reviewed</span><span class="inspect-v {review_cls}">{"Yes" if st.session_state.get("ag_review_confirmed") else "Not yet"}</span></div><div class="inspect-row"><span class="inspect-k">Evidence reviewed</span><span class="inspect-v {evidence_cls}">{"Yes" if st.session_state.get("ag_evidence_confirmed") else "Not yet"}</span></div><div class="inspect-row"><span class="inspect-k">Blocking gaps</span><span class="inspect-v {gap_cls}">{blocking}</span></div><div class="inspect-row"><span class="inspect-k">Decision support</span><span class="inspect-v">{escape(support_label(val(final,"decision_support_strength","")) if final else "Not assessed")}</span></div><div class="inspect-row"><span class="inspect-k">Brief ready</span><span class="inspect-v">{"Yes" if val(brief,"safe_to_display",False) else "Not yet"}</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="inspect-card"><div class="inspect-head">Agent activity</div>'+_activity_html(result)+'</div>', unsafe_allow_html=True)
        if result and red is not None and not bool(val(red,"safe_for_consensus",False)):
            st.markdown('<div class="inspect-card"><div class="inspect-head">Why the agent stopped</div><div class="inspect-note">The challenge review found a recommendation-blocking weakness. The system preserves the limitation instead of manufacturing a confident recommendation.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="inspect-card"><div class="inspect-head">Information legend</div><div class="inspect-legend">'+claim_chip("source")+claim_chip("retrieved")+claim_chip("derived")+claim_chip("human")+'</div><div class="inspect-note">Expand technical details only when you need provenance, evidence admission, or the audit trail.</div></div>', unsafe_allow_html=True)
    else:
        routing=result.get("routing") if isinstance(result,dict) else None; integrity=result.get("case_integrity_report") if isinstance(result,dict) else None; missing=result.get("missing_information_report") if isinstance(result,dict) else None; red=result.get("red_team_report") if isinstance(result,dict) else None; consensus=result.get("consensus_report") if isinstance(result,dict) else None; final=result.get("final_decision") if isinstance(result,dict) else None; audit=result.get("audit_events",[]) if isinstance(result,dict) else []
        st.markdown('<div class="inspect-card primary"><div class="inspect-head">Qualification boundary</div>'+f'<div class="inspect-row"><span class="inspect-k">Pathway</span><span class="inspect-v">{escape(validation.label)}</span></div><div class="inspect-row"><span class="inspect-k">Common core</span><span class="inspect-v okv">{"Qualified" if validation.common_core_qualified else "Not qualified"}</span></div><div class="inspect-row"><span class="inspect-k">Clinical validation</span><span class="inspect-v warnv">{"Established" if validation.clinically_validated else "Not established"}</span></div><div class="inspect-note">Software qualification, disease-specific validation, and clinical release are separate claims.</div></div>', unsafe_allow_html=True)
        if case is not None:
            source_items=[case.diagnosis,case.disease_state,case.stage,case.performance_status,*list(case.pathology),*list(case.imaging),*list(case.labs),*list(case.comorbidities),*list(case.toxicities),*list(case.current_medications)]; traceable=sum(1 for x in source_items if x is not None and source_ok(x))
            st.markdown('<div class="inspect-card"><div class="inspect-head">Provenance & admission</div>'+f'<div class="inspect-row"><span class="inspect-k">Traceable facts</span><span class="inspect-v">{traceable}</span></div><div class="inspect-row"><span class="inspect-k">Molecular candidates</span><span class="inspect-v">{int(evidence.get("molecular_candidates",0) or 0)}</span></div><div class="inspect-row"><span class="inspect-k">Molecular attested</span><span class="inspect-v">{int(evidence.get("molecular_attested",0) or 0)}</span></div><div class="inspect-row"><span class="inspect-k">Safety candidates</span><span class="inspect-v">{int(evidence.get("safety_candidates",0) or 0)}</span></div><div class="inspect-row"><span class="inspect-k">Safety attested</span><span class="inspect-v">{int(evidence.get("safety_attested",0) or 0)}</span></div></div>', unsafe_allow_html=True)
        if runtime:
            rows=[]
            for key in ("guideline","molecular","safety","pubmed","clinical_trials","translational","civic","openfda"):
                status=runtime.get(key,{}) or {}; ready=_runtime_ready(status); consequence="Available" if ready else "Unavailable → dependent claims withheld"; rows.append(f'<div class="inspect-row"><span class="inspect-k">{escape(human(key))}</span><span class="inspect-v {"okv" if ready else "warnv"}">{escape(consequence)}</span></div>')
            st.markdown('<div class="inspect-card"><div class="inspect-head">Evidence channels</div>'+"".join(rows)+'</div>', unsafe_allow_html=True)
        if result:
            selected=val(routing,"selected_agents",[]) or []
            st.markdown('<div class="inspect-card"><div class="inspect-head">Governance gates</div>'+f'<div class="inspect-row"><span class="inspect-k">Case integrity</span><span class="inspect-v">{escape(human(val(integrity,"disposition","Not run")))}</span></div><div class="inspect-row"><span class="inspect-k">Missing information</span><span class="inspect-v">{escape(human(val(missing,"disposition","Not run")))}</span></div><div class="inspect-row"><span class="inspect-k">Specialists routed</span><span class="inspect-v">{escape(", ".join(human(x) for x in selected) or "None")}</span></div><div class="inspect-row"><span class="inspect-k">Challenge review</span><span class="inspect-v">{escape(human(val(red,"disposition","Not run")))}</span></div><div class="inspect-row"><span class="inspect-k">Consensus</span><span class="inspect-v">{escape(human(val(consensus,"decision_state","Not run")))}</span></div><div class="inspect-row"><span class="inspect-k">Final state</span><span class="inspect-v">{escape(human(val(final,"decision_state","Not established")))}</span></div></div>', unsafe_allow_html=True)
            if audit:
                last=audit[-8:]; events="".join(f'<div class="activity"><div class="activity-icon ok">•</div><div class="activity-body"><div class="activity-title">{escape(txt(val(event,"event_type",val(event,"event","event"))))}</div><div class="activity-copy">{escape(txt(val(event,"details",val(event,"detail","")),""))}</div></div></div>' for event in last); st.markdown('<div class="inspect-card"><div class="inspect-head">Recent audit events</div>'+events+'</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
