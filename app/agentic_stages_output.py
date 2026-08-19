from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from app.agentic_core import goto, human, run_guarded_workflow, txt, val
from app.agentic_layout import claim_chip, logic_strip, stage_guidance, support_label, turn
from app.chat_ui import render_governed_chat
from services.tumor_board_pdf import build_tumor_board_pdf

_AGENT_LABELS = {"guideline":"Guideline / consensus evidence","molecular":"Molecular interpretation","safety":"Safety and contraindication review","literature":"Published literature","clinical_trials":"Clinical trials","translational":"Translational biology"}


def _status_text(output: Any) -> str:
    value=val(output,"status",""); value=value.value if hasattr(value,"value") else value; return str(value or "").strip().lower()


def _clinical_consequence(agent_id: str, output: Any) -> str:
    status=_status_text(output)
    if output is None: return "This domain was not selected or did not produce an output for the current question."
    if status in {"source_unavailable","tool_failure","error","failed"}:
        return {"literature":"The literature channel was unavailable, so literature-dependent support is withheld.","translational":"The translational channel was unavailable, so mechanistic support cannot strengthen the decision.","safety":"The safety channel was unavailable, so safety-dependent claims are withheld; absence of a result is not evidence of safety.","clinical_trials":"The trial channel was unavailable, so no trial claim is made from this run.","guideline":"Formal guideline support could not be established in this run.","molecular":"Patient-level molecular actionability could not be established from this channel."}.get(agent_id,"Dependent claims are withheld because the governed source channel was unavailable.")
    if status in {"no_evidence","no evidence","no_match","no match"}: return "No bounded match was found. This is not proof that no relevant option, hazard, biomarker, or study exists."
    if status in {"not_selected","not selected"}: return "This specialist was not required for the represented clinical question."
    summary=txt(val(output,"summary"),""); return summary or "This specialist completed within its governed evidence boundary."


def _render_specialist_outputs(result: dict) -> None:
    outputs=result.get("specialist_outputs",{}) or {}
    if not outputs: st.info("No specialist synthesis was produced because an earlier integrity or missing-information guardrail stopped the workflow."); return
    order=("guideline","molecular","safety","literature","clinical_trials","translational"); keys=[k for k in order if k in outputs]+[k for k in outputs if k not in order]
    for agent_id in keys:
        output=outputs[agent_id]; label=_AGENT_LABELS.get(agent_id,human(agent_id)); consequence=_clinical_consequence(agent_id,output)
        with st.expander(label+" · clinician view",expanded=False):
            st.write(consequence); warnings=val(output,"warnings",[]) or []; limitations=val(output,"limitations",[]) or []
            if warnings:
                st.markdown("**What to pay attention to**")
                for item in warnings[:8]: st.warning(txt(item))
            if limitations:
                st.markdown("**Limitations**")
                for item in limitations[:8]: st.write("• "+txt(item))
            with st.expander("Technical output"):
                try: st.json(output.model_dump(mode="json"),expanded=False)
                except Exception:
                    if isinstance(output,dict): st.json(output,expanded=False)


def _render_gate_summary(result: dict) -> None:
    integrity=result.get("case_integrity_report"); missing=result.get("missing_information_report"); semantic=result.get("semantic_integrity_findings",[]) or []; routing=result.get("routing"); final=result.get("final_decision"); brief=result.get("tumor_board_brief")
    st.markdown("### Why this result is supportable"); logic_strip(result); cols=st.columns(3,gap="medium")
    with cols[0]: st.markdown("**Case readiness**"); st.caption(f"Case integrity: {human(val(integrity,'disposition','not run'))}. Semantic findings: {len(semantic)}. Blocking information gaps: {val(missing,'blocking_count',0) or 0}.")
    with cols[1]:
        st.markdown("**Evidence used**"); selected=val(routing,"selected_agents",[]) or []; st.caption("Specialists: "+(", ".join(_AGENT_LABELS.get(x,human(x)) for x in selected) if selected else "none routed"))
    with cols[2]: st.markdown("**Decision state**"); st.caption(f"{human(val(final,'decision_state','not established'))} · {support_label(val(final,'decision_support_strength','insufficient'))} · brief {'available' if val(brief,'safe_to_display',False) else 'not available'}.")


def _next_steps_from_missing(missing: Any) -> list[str]:
    steps=[]
    for item in val(missing,"items",[]) or []:
        if not val(item,"recommendation_blocking",False): continue
        action=txt(val(item,"action"),""); field=txt(val(item,"field")); reason=txt(val(item,"reason")); steps.append(f"{human(action)}: {field}. {reason}" if action else f"Resolve {field}. {reason}")
    return steps


def _render_missing_actions(result: dict) -> None:
    missing=result.get("missing_information_report")
    if missing is None: return
    items=val(missing,"items",[]) or []
    if not items: return
    blocking=[item for item in items if val(item,"recommendation_blocking",False)]
    if blocking:
        st.markdown('<div class="guardrail"><strong>Recommendation withheld until decision-critical information is resolved</strong><p>Abstention is an actionable state. The system is showing what must be clarified instead of filling the gap with a plausible answer.</p></div>', unsafe_allow_html=True); st.markdown("#### What to obtain or clarify next")
        for step in _next_steps_from_missing(missing): st.write("• "+step)
    with st.expander("All unresolved or incomplete information",expanded=bool(blocking)):
        st.write(txt(val(missing,"summary")))
        for item in items:
            block=" · BLOCKING" if val(item,"recommendation_blocking",False) else ""; st.write(f"**{txt(val(item,'field'))}** · {human(val(item,'priority'))}{block}"); st.caption(txt(val(item,"reason")))


def _render_why_conclusion(result: dict) -> None:
    with st.expander("Why this conclusion? · See the reasoning chain",expanded=True):
        integrity=result.get("case_integrity_report"); missing=result.get("missing_information_report"); routing=result.get("routing"); red=result.get("red_team_report"); consensus=result.get("consensus_report"); final=result.get("final_decision")
        st.markdown("**1. Case representation**"); st.write(f"Case integrity: **{human(val(integrity,'disposition','not run'))}**. Missing-information state: **{human(val(missing,'disposition','not run'))}**.")
        st.markdown("**2. Specialists consulted**"); selected=val(routing,"selected_agents",[]) or []; st.write(", ".join(_AGENT_LABELS.get(x,human(x)) for x in selected) if selected else "No specialist routing occurred.")
        st.markdown("**3. Safety & challenge review**")
        if red is not None: st.write(f"Challenge disposition: **{human(val(red,'disposition','not represented'))}**. Recommendation-blocking findings: **{val(red,'blocking_count',0) or 0}**.")
        else: st.write("Challenge review was not reached because an earlier guardrail stopped the workflow.")
        st.markdown("**4. Tumor board decision status**")
        if consensus is not None: st.write(f"Adjudicated state: **{human(val(consensus,'decision_state','not represented'))}**. Final support: **{support_label(val(final,'decision_support_strength','insufficient'))}**.")
        else: st.write("Consensus was withheld because an earlier guardrail prevented adjudication.")


def render_analysis() -> None:
    if not st.session_state.ag_evidence_confirmed: goto("evidence"); return
    stage_guidance("Agent analysis","The governed engine is checking the case, routing only the needed specialists, challenging the synthesis, and deciding whether a board-ready brief is supportable.","Review what the agents agreed on—and what they refused to conclude","A missing source or unresolved blocker has a clinical consequence: dependent claims are withheld rather than silently replaced.")
    if st.session_state.ag_result is None:
        try:
            with st.status("Running the governed multi-agent workup...",expanded=True) as status:
                status.write("Checking semantic integrity and case integrity"); status.write("Checking missing decision-critical information"); status.write("Routing only the specialists needed for the clinical question"); status.write("Running bounded evidence analysis"); status.write("Running safety & challenge review"); status.write("Adjudicating consensus and rendering the decision-support brief"); result=run_guarded_workflow(); status.update(label="Governed analysis complete",state="complete")
        except Exception as exc:
            st.error(f"Workflow stopped safely: {type(exc).__name__}: {exc}"); st.caption("The system does not generate a fallback patient-specific clinical claim when the governed workflow fails."); return
    else: result=st.session_state.ag_result
    final=result.get("final_decision"); red=result.get("red_team_report"); consensus=result.get("consensus_report")
    if red is not None and not bool(val(red,"safe_for_consensus",False)): headline="The safety & challenge review found a recommendation-blocking weakness. The system preserved the limitation and withheld normal consensus."
    elif consensus is not None: headline=txt(val(consensus,"summary"),"The governed analysis reached an adjudicated decision-support state.")
    else: headline="The workflow stopped at a pre-routing guardrail before specialist consensus."
    turn("Tumor Board Agent · Analysis",escape(headline),chips=[claim_chip("retrieved"),claim_chip("derived")]); _render_gate_summary(result)
    st.markdown('<div class="clinical-takeaway"><strong>Clinical takeaway</strong><p>'+escape(f"Current decision state: {human(val(final,'decision_state','not established'))}. Decision support: {support_label(val(final,'decision_support_strength','insufficient'))}. Use the challenge findings and missing-information actions below to understand what still requires clinician judgment.")+'</p></div>', unsafe_allow_html=True)
    _render_missing_actions(result); findings=result.get("red_team_findings",[]) or []
    with st.expander("Safety & challenge review · What could make the synthesis wrong",expanded=True):
        if red is not None: st.write(txt(val(red,"summary")))
        if not findings: st.caption("No challenge findings are represented.")
        for finding in findings:
            severity=human(val(finding,"severity")); st.markdown(f"**{severity}:** {txt(val(finding,'issue'))}"); effect=txt(val(finding,"effect_on_recommendation"),"")
            if effect: st.caption("Why it matters: "+effect)
    with st.expander("Tumor board decision status · How the system adjudicated the evidence",expanded=True):
        if consensus is None: st.info("Consensus was not run because an earlier safety gate stopped the workflow.")
        else:
            st.write(txt(val(consensus,"summary"))); st.caption(f"Adjudicated decision state: {human(val(consensus,'decision_state','not represented'))}")
            with st.expander("Technical consensus object"):
                try: st.json(consensus.model_dump(mode="json"),expanded=False)
                except Exception: pass
    _render_why_conclusion(result)
    with st.expander("Specialist evidence domains · Optional deep dive"): _render_specialist_outputs(result)
    if st.button("Open board-ready decision brief",type="primary",use_container_width=True,key="ag_to_brief"): goto("brief")


def _brief_category(epistemic: str) -> str:
    normalized=epistemic.upper()
    if normalized in {"OBSERVED","SOURCE_FACT"}: return "source"
    if normalized in {"INTERPRETED","DERIVED"}: return "derived"
    if normalized in {"HUMAN","ADJUDICATED"}: return "human"
    return "retrieved"


def _render_brief_sections(brief) -> None:
    st.markdown('<div class="legend">'+claim_chip("source")+claim_chip("retrieved")+claim_chip("derived")+claim_chip("human")+'</div>', unsafe_allow_html=True)
    for section in val(brief,"sections",[]) or []:
        items_html=[]
        for item in val(section,"items",[]) or []:
            category=claim_chip(_brief_category(txt(val(item,"epistemic_label"),""))); refs=val(item,"source_refs",[]) or []; limitations=val(item,"limitations",[]) or []; refs_html=f'<div class="source-refs">Sources: {escape(", ".join(map(str,refs)))}</div>' if refs else ""; lim_html=f'<div class="brief-note">Limitations: {escape(" · ".join(map(str,limitations)))}</div>' if limitations else ""; items_html.append('<div class="brief-item">'+f'<div class="brief-label">{escape(txt(val(item,"label")))}</div><div class="brief-value">{escape(txt(val(item,"value")))}</div><div class="legend">{category}</div>{refs_html}{lim_html}</div>')
        note=txt(val(section,"section_note"),""); st.markdown('<div class="brief-section">'+f'<div class="brief-title">{escape(txt(val(section,"title")))}</div><div class="brief-note">{escape(note)}</div>'+"".join(items_html)+'</div>', unsafe_allow_html=True)


def _render_decision_dimensions(final) -> None:
    alternatives=val(final,"alternatives",[]) or []; conditions=val(final,"conditions",[]) or []; uncertainties=val(final,"major_uncertainties",[]) or []; priorities=val(final,"discussion_priorities",[]) or []
    if alternatives:
        st.markdown("#### Reasonable alternatives")
        for item in alternatives: st.write("• "+txt(item))
    else: st.caption("No ranked alternative is represented. The system does not force a ranking when support is insufficient.")
    if conditions:
        st.markdown("#### Conditions and prerequisites")
        for item in conditions: st.write("• "+txt(item))
    if uncertainties:
        st.markdown("#### Major uncertainties")
        for item in uncertainties: st.warning(txt(item))
    if priorities:
        st.markdown("#### Tumor-board discussion priorities")
        for item in priorities: st.write("• "+txt(item))


def _trial_summary(result: dict) -> tuple[str,list[str]]:
    output=(result.get("specialist_outputs",{}) or {}).get("clinical_trials")
    if output is None: return "No governed trial output is available for this run.",[]
    matches=val(output,"matches",[]) or []
    if not matches: return _clinical_consequence("clinical_trials",output),[]
    labels=[]
    for match in matches[:5]: labels.append(f"{txt(val(match,'nct_id'),'NCT not represented')} · {txt(val(match,'title'),'Untitled study')}")
    return f"{len(matches)} possible governed trial match(es) surfaced. Trial matching is not eligibility.",labels


def _safety_summary(result: dict) -> str:
    output=(result.get("specialist_outputs",{}) or {}).get("safety"); return "No governed safety output is available for this run." if output is None else _clinical_consequence("safety",output)


def _board_agenda(result: dict) -> list[str]:
    final=result.get("final_decision"); missing=result.get("missing_information_report"); red_findings=result.get("red_team_findings",[]) or []; agenda=[]
    for item in _next_steps_from_missing(missing)[:4]: agenda.append(item)
    for finding in red_findings[:4]:
        issue=txt(val(finding,"issue"),"")
        if issue: agenda.append("Resolve challenge review question: "+issue)
    for item in val(final,"discussion_priorities",[]) or []: agenda.append(txt(item))
    _,trials=_trial_summary(result)
    if trials: agenda.append("Decide whether any surfaced trial warrants direct site-level eligibility confirmation.")
    if st.session_state.get("ag_patient_context"): agenda.append("Incorporate the recorded patient goals/preferences into the board's final judgment.")
    if not agenda: agenda.append("Confirm whether the best-supported strategy fits the patient's clinical context and preferences.")
    return list(dict.fromkeys(x for x in agenda if x))[:8]


def _render_board_agenda(result: dict) -> None:
    agenda=_board_agenda(result); st.markdown("### Questions for today's tumor board"); st.caption("This is the working discussion agenda—not an autonomous treatment order."); html="".join(f'<div class="board-agenda-item"><div class="board-agenda-num">{i}</div><div class="board-agenda-copy">{escape(item)}</div></div>' for i,item in enumerate(agenda,1)); st.markdown('<div class="board-agenda">'+html+'</div>', unsafe_allow_html=True)


def _render_trial_safety_boundaries(result: dict) -> None:
    specialist_outputs=result.get("specialist_outputs",{}) or {}; trial_output=specialist_outputs.get("clinical_trials")
    if trial_output is not None:
        with st.expander("Clinical trials · Why they matched and what still needs verification"):
            st.write(_clinical_consequence("clinical_trials",trial_output)); matches=val(trial_output,"matches",[]) or []
            if not matches: st.caption("No governed possible trial matches are represented.")
            for match in matches:
                st.write(f"**{txt(val(match,'nct_id'))}:** {txt(val(match,'title'))}"); rationale=txt(val(match,"rationale"),"")
                if rationale: st.caption("Why it matched: "+rationale)
                unresolved=val(match,"unresolved_eligibility_domains",[]) or []
                if unresolved: st.caption("Still unresolved for eligibility: "+", ".join(map(str,unresolved)))
            st.warning("A trial match is not trial eligibility. Recruitment status, site availability, and patient-specific inclusion/exclusion criteria require direct study-team confirmation.")
    safety_output=specialist_outputs.get("safety")
    if safety_output is not None:
        with st.expander("Safety · Potential issue, why it matters, and what to verify"):
            st.write(_clinical_consequence("safety",safety_output)); findings=val(safety_output,"findings",[]) or []
            if not findings: st.caption("No matched governed safety finding is represented. A non-match is not evidence of safety.")
            for finding in findings:
                block=" · BLOCKING" if val(finding,"recommendation_blocking",False) else ""; st.write(f"**{human(val(finding,'severity'))}{block}:** {txt(val(finding,'safety_issue'))}"); locator=txt(val(finding,"source_locator"),"")
                if locator: st.caption("Source: "+locator)


def _render_pdf_download(result: dict) -> None:
    try:
        pdf_bytes=build_tumor_board_pdf(result); case=result.get("case"); case_id=txt(val(case,"case_id"),"case").replace(" ","-"); st.download_button("Download governed tumor-board brief (PDF)",data=pdf_bytes,file_name=f"tumor-board-intelligence-{case_id}.pdf",mime="application/pdf",use_container_width=True,key="ag_pdf_download"); st.caption("The PDF is a presentation transform of the governed brief. It cannot add evidence or change a workflow gate.")
    except Exception as exc: st.caption(f"PDF export unavailable: {type(exc).__name__}. The on-screen governed brief remains available.")


def _render_executive_summary(result: dict) -> None:
    case=result.get("case"); final=result.get("final_decision"); missing=result.get("missing_information_report"); trial_text,trials=_trial_summary(result); safety_text=_safety_summary(result); diagnosis=txt(val(val(case,"diagnosis"),"value")); disease_state=txt(val(val(case,"disease_state"),"value")); question=txt(val(val(case,"clinical_question"),"question")); primary=txt(val(final,"primary_strategy"),"WITHHELD"); alternatives=val(final,"alternatives",[]) or []; blocking=int(val(missing,"blocking_count",0) or 0); support=support_label(val(final,"decision_support_strength","insufficient"))
    st.markdown("### Tumor-board summary"); st.markdown('<div class="brief-section"><div class="brief-title">What is the clinical problem?</div>'+f'<div class="brief-value">{escape(diagnosis)} · {escape(disease_state)}<br>{escape(question)}</div></div>', unsafe_allow_html=True); st.markdown('<div class="brief-section"><div class="brief-title">What is the best-supported strategy?</div>'+f'<div class="brief-value">{escape(primary)}</div><div class="brief-note">Decision support: {escape(support)}</div></div>', unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="medium")
    with c1:
        st.markdown("**Reasonable alternatives**")
        if alternatives:
            for item in alternatives: st.write("• "+txt(item))
        else: st.caption("No ranked alternative is represented.")
        st.markdown("**Safety considerations**"); st.write(safety_text)
    with c2:
        st.markdown("**Clinical trials**"); st.write(trial_text)
        for item in trials[:4]: st.caption("• "+item)
        st.markdown("**Missing information**"); st.write(f"{blocking} recommendation-blocking gap(s)." if blocking else "No recommendation-blocking gap is represented in the final workflow state.")


def _render_human_context() -> None:
    context=str(st.session_state.get("ag_patient_context") or "").strip(); override=str(st.session_state.get("ag_clinician_override") or "").strip(); reason=str(st.session_state.get("ag_clinician_override_reason") or "").strip()
    if not context and not override: return
    st.markdown("### Clinician judgment recorded separately")
    if context: st.markdown('<div class="brief-section"><div class="brief-title">Patient goals / clinician context</div>'+f'<div class="brief-value">{escape(context)}</div><div class="legend">{claim_chip("human")}</div></div>', unsafe_allow_html=True)
    if override:
        st.markdown('<div class="brief-section"><div class="brief-title">Clinician disagreement or override note</div>'+f'<div class="brief-note">{escape(reason or "Clinician judgment")}</div><div class="brief-value">{escape(override)}</div><div class="legend">{claim_chip("human")}</div></div>', unsafe_allow_html=True); st.caption("The system conclusion and clinician judgment are both preserved; the original system output is not rewritten.")


def _render_change_log() -> None:
    changes=st.session_state.get("ag_change_log",[]) or []
    if not changes: return
    with st.expander("What changed during this workup"):
        for item in changes: st.write("• "+str(item))
        st.caption("A future persisted case workflow can extend this into version-to-version impact analysis when new pathology, imaging, or molecular results arrive.")


def render_brief() -> None:
    result=st.session_state.ag_result
    if not result: goto("analysis"); return
    stage_guidance("Decision brief","The agent has finished the governed workup. The first screen is intentionally board-ready; full evidence, provenance, technical outputs, and audit detail remain available underneath.","Prepare the tumor-board discussion","Review the strategy, alternatives, safety, trials, missing information, and board agenda. Final patient-care judgment remains with the clinical team.")
    brief=result.get("tumor_board_brief"); final=result.get("final_decision")
    turn("Tumor Board Agent · Decision brief","This brief is designed to help you arrive at tumor board more complete and better prepared. It shows what is supported, what is uncertain, what the agents challenged, what evidence failed or was unavailable, and where clinician judgment is still required.",chips=[claim_chip("derived"),claim_chip("human")])
    c1,c2,c3,c4=st.columns(4); c1.metric("Decision state",human(val(final,"decision_state"))); c2.metric("Decision support",support_label(val(final,"decision_support_strength"))); c3.metric("Source traces",val(brief,"source_trace_count",0) or 0); c4.metric("Board brief","Ready" if val(brief,"safe_to_display",False) else "Withheld")
    abstention=txt(val(final,"abstention_reason"),"")
    if abstention:
        st.error("Recommendation withheld: "+abstention); next_steps=_next_steps_from_missing(result.get("missing_information_report"))
        if next_steps:
            st.markdown("**To move the case forward:**")
            for step in next_steps: st.write("• "+step)
    _render_executive_summary(result); _render_board_agenda(result); _render_human_context(); _render_decision_dimensions(final)
    st.markdown("### What could change the decision?"); changes=list(val(final,"conditions",[]) or [])+list(val(final,"major_uncertainties",[]) or [])
    if changes:
        for item in list(dict.fromkeys(txt(x) for x in changes))[:10]: st.write("• "+item)
    else: st.caption("No explicit recommendation-changing condition is represented beyond the limitations already shown.")
    _render_why_conclusion(result); _render_trial_safety_boundaries(result)
    with st.expander("Full governed brief · Evidence, provenance, and limitations"):
        if brief is not None: _render_brief_sections(brief)
        else: st.error("No tumor-board brief object was produced.")
    audit=result.get("audit_events",[]) or []
    with st.expander("Technical / governance detail · Provenance and audit trail"):
        st.write(f"{len(audit)} workflow audit event(s) recorded.")
        for event in audit:
            event_name=txt(val(event,"event_type",val(event,"event","event"))); detail=txt(val(event,"details",val(event,"detail","")),""); st.write(f"**{event_name}**"+(f" — {detail}" if detail else ""))
    _render_change_log(); _render_pdf_download(result); st.markdown("### Ask Tumor Board"); st.caption("Follow-up answers are restricted to the current structured case and governed specialist outputs. The conversational layer cannot invent a new patient-specific recommendation from unrestricted model memory."); render_governed_chat(result,result.get("case"),key_prefix="brief")
    with st.expander("Safety commitments"):
        st.markdown("""
- Never invent missing patient facts.
- Never treat a trial match as trial eligibility.
- Never treat molecular evidence as automatically actionable.
- Never hide unresolved recommendation-blocking information.
- Never silently substitute model memory when a governed evidence source fails.
- Never present software qualification as clinical validation.
- Preserve source provenance and clinician judgment separately.
        """)
