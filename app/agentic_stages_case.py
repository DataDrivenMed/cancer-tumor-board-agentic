from __future__ import annotations

from html import escape

import streamlit as st

from agents.guideline import GuidelineAgent
from app.agentic_core import (
    commission_evidence,
    confirm_case_representation,
    ensure_evidence_candidates,
    extract_text_case,
    extract_upload_case,
    goto,
    human,
    load_synthetic,
    source_ok,
    source_refs,
    txt,
    val,
)
from app.agentic_layout import case_facts, claim_chip, stage_guidance, turn
from services.evidence_commissioning import safety_candidate_excerpt
from services.eln_aml_guidance import public_eln_aml_store


def _select_intake_mode(mode: str) -> None:
    st.session_state.ag_intake_mode = mode
    st.rerun()


def _action_card(icon: str, title: str, copy: str, button: str, mode: str, *, primary: bool = False) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div class="action-step">Choose a starting point</div>'
            f'<div class="action-icon">{escape(icon)}</div>'
            f'<div class="action-title">{escape(title)}</div>'
            f'<div class="action-copy">{escape(copy)}</div>',
            unsafe_allow_html=True,
        )
        if st.button(button, type="primary" if primary else "secondary", use_container_width=True, key=f"ag_mode_{mode}"):
            _select_intake_mode(mode)


def render_intake() -> None:
    stage_guidance(
        "Case intake",
        "Give the agent a de-identified case. It will structure the record and preserve source traces before any clinical synthesis occurs.",
        "Choose how to start",
        "For a real case, paste a narrative or upload a document. Use the guided demonstration to learn the workflow safely.",
    )
    turn(
        "Tumor Board Agent · Intake",
        "I will prepare the case for tumor board, but I will not treat extracted text as clinical truth. You will review the structured case before I gather patient-level evidence or run the specialist agents.",
        chips=[claim_chip("human")],
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        _action_card("✦", "Start a new case", "Paste a de-identified tumor-board narrative. Best for concise referral summaries or cases already prepared in text.", "Paste case narrative", "narrative", primary=True)
    with c2:
        _action_card("↑", "Upload a case document", "Upload a de-identified PDF, DOCX, TXT, or MD file and let the source-traced extraction pipeline build the case.", "Upload document", "upload")
    with c3:
        _action_card("◎", "Review the guided demo", "Walk through a synthetic AML case with prompts that explain where the agent works and where clinician judgment is required.", "Load demonstration case", "demo")

    with st.expander("How the governed agentic workup works"):
        st.markdown(
            """
1. **Provide the case.** Paste or upload a de-identified source.
2. **Verify the representation.** Confirm that diagnosis, disease state, prior therapy, molecular findings, conflicts, and missing information match the source.
3. **Review evidence.** The system retrieves bounded evidence; molecular and safety records require explicit clinician attestation before patient-level use.
4. **Let the agents analyze.** Integrity gates, specialist agents, challenge review, and consensus run under the conversational surface.
5. **Prepare the board discussion.** The final brief shows the best-supported strategy, reasonable alternatives, safety issues, trials, missing information, uncertainty, and what the board still needs to decide.
            """
        )
        st.info("The tool is designed to prepare and structure tumor-board decision support. It is not an autonomous treatment recommender.")

    mode = st.session_state.get("ag_intake_mode", "new")
    if mode == "demo":
        st.markdown('<div class="clinical-takeaway"><strong>Guided demonstration</strong><p>The demonstration uses a synthetic qualification case. As you move through the workflow, the interface will explain each human checkpoint and what the agent is allowed to do.</p></div>', unsafe_allow_html=True)
        if st.button("Begin guided demonstration", type="primary", use_container_width=True, key="ag_load_syn"):
            st.session_state.ag_case = load_synthetic(); st.session_state.ag_raw_extraction = None; st.session_state.ag_extraction_package = None; st.session_state.ag_demo_mode = True; goto("review")
    elif mode == "narrative":
        st.markdown("### Paste a de-identified case narrative")
        st.caption("Include the clinical question if you know it. The extraction pipeline will preserve uncertainty, pending results, conflicts, prior treatment chronology, and source provenance rather than filling gaps from model memory.")
        deidentified = st.checkbox("I confirm that this case text is appropriately de-identified for this research deployment.", key="ag_text_deidentified")
        narrative = st.text_area("Case narrative", height=260, placeholder="Paste a de-identified tumor-board referral or clinical summary...", key="ag_text")
        if st.button("Build source-traced case", type="primary", use_container_width=True, key="ag_extract_text"):
            if not deidentified:
                st.warning("Confirm de-identification before processing the case.")
            elif not narrative.strip():
                st.warning("Paste a narrative first.")
            else:
                try:
                    with st.status("Building the source-traced case...", expanded=True) as status:
                        status.write("Parsing the source and assigning provenance anchors"); status.write("Extracting diagnosis, disease state, therapy history, molecular findings, conflicts, and missing information"); status.write("Applying deterministic normalization and provenance checks"); package = extract_text_case(narrative); status.update(label="Case built. Clinician review is required.", state="complete")
                    st.session_state.ag_case = package.case; st.session_state.ag_raw_extraction = package.raw_extraction; st.session_state.ag_extraction_package = package; st.session_state.ag_demo_mode = False; goto("review")
                except Exception as exc:
                    st.error(f"Extraction stopped safely: {type(exc).__name__}: {exc}")
    elif mode == "upload":
        st.markdown("### Upload a de-identified case document")
        st.caption("Supported formats: PDF, DOCX, TXT, and MD. The agent will not infer a missing stage, response, molecular result, or clinical fact from general oncology knowledge.")
        deidentified = st.checkbox("I confirm that this document is appropriately de-identified for this research deployment.", key="ag_upload_deidentified")
        upload = st.file_uploader("Choose a case file", type=["txt", "md", "pdf", "docx"], key="ag_upload")
        if st.button("Upload and build source-traced case", type="primary", use_container_width=True, key="ag_extract_upload"):
            if not deidentified:
                st.warning("Confirm de-identification before processing the document.")
            elif upload is None:
                st.warning("Choose a document first.")
            else:
                try:
                    with st.status("Building the source-traced case...", expanded=True) as status:
                        status.write("Parsing the document"); status.write("Extracting and reconciling clinically important facts"); status.write("Checking provenance and preserving uncertainty"); package = extract_upload_case(upload); status.update(label="Case built. Clinician review is required.", state="complete")
                    st.session_state.ag_case = package.case; st.session_state.ag_raw_extraction = package.raw_extraction; st.session_state.ag_extraction_package = package; st.session_state.ag_demo_mode = False; goto("review")
                except Exception as exc:
                    st.error(f"Extraction stopped safely: {type(exc).__name__}: {exc}")
    else:
        st.caption("Choose one of the three starting options above.")


def _provenance_line(item) -> str:
    refs = source_refs(item); state = "Verified source" if source_ok(item) else "Source review required"
    return f"{state} · {len(refs)} trace(s) · " + ", ".join(refs[:4]) if refs else state


def _treatment_timeline(case) -> None:
    treatments = list(case.treatments or [])
    if not treatments:
        st.info("No treatment episodes are represented in the current case."); return
    rows = []
    for episode in treatments:
        start = txt(val(episode, "start_date"), ""); end = txt(val(episode, "end_date"), ""); when = start or end or "Date not represented"; regimen = txt(val(episode, "regimen"), "Regimen not represented"); response = txt(val(episode, "best_response"), "Response not represented"); status = human(val(episode, "treatment_status", "unknown")); agents = ", ".join(map(str, val(episode, "agents", []) or [])); details = status
        if agents: details += f" · {agents}"
        if response and response != "Response not represented": details += f" · Best response: {response}"
        rows.append(f'<div class="timeline-item"><div class="timeline-date">{escape(when)}</div><div class="timeline-title">{escape(regimen)}</div><div class="timeline-copy">{escape(details)}</div></div>')
    st.markdown('<div class="timeline">' + "".join(rows) + '</div>', unsafe_allow_html=True)


def _render_treatment_history(case) -> None:
    st.markdown("#### Longitudinal treatment course"); st.caption("Major treatment episodes are shown in chronological source order when dates are represented."); _treatment_timeline(case)
    for idx, episode in enumerate(list(case.treatments or []), 1):
        regimen = txt(val(episode, "regimen"), "Regimen not represented")
        with st.expander(f"Details · {idx}. {regimen}", expanded=False):
            agents = ", ".join(map(str, val(episode, "agents", []) or []))
            if agents: st.write("**Agents:** " + agents)
            st.write("**Treatment status:** " + human(val(episode, "treatment_status", "unknown")))
            response = txt(val(episode, "best_response"), "")
            if response: st.write("**Best response:** " + response)
            reason = txt(val(episode, "reason_stopped"), "")
            if reason: st.write("**Reason stopped:** " + reason)
            toxicities = val(episode, "toxicities", []) or []
            if toxicities: st.write("**Recorded toxicities:** " + ", ".join(map(str, toxicities)))
            st.caption(_provenance_line(episode))


def _render_molecular_pathology(case) -> None:
    st.markdown("#### Molecular profile")
    if case.molecular_findings:
        for item in case.molecular_findings:
            gene = txt(val(item, "gene")); alteration = txt(val(item, "alteration_type") or val(item, "hgvs_p") or val(item, "hgvs_c")); vaf = val(item, "variant_allele_frequency"); vaf_text = f"{float(vaf) * 100:.1f}%" if vaf is not None else "Not represented"; interpretation = txt(val(item, "laboratory_interpretation"), "")
            st.markdown('<div class="evidence-card">'+f'<div class="evidence-title">{escape(gene)} · {escape(alteration)}</div><div class="evidence-copy">VAF: {escape(vaf_text)}'+(f'<br>Laboratory interpretation: {escape(interpretation)}' if interpretation else '')+'</div>'+f'<div class="evidence-meta">{escape(_provenance_line(item))}</div></div>', unsafe_allow_html=True)
    else:
        st.info("No molecular findings are represented in the current case.")
    st.markdown("#### Pathology and imaging")
    represented = [("Pathology", x) for x in case.pathology] + [("Imaging", x) for x in case.imaging]
    if not represented: st.caption("No pathology or imaging facts are represented.")
    for kind, fact in represented:
        st.markdown(f'<div class="evidence-card"><div class="evidence-title">{escape(kind)} · {escape(txt(val(fact, "field")))}</div><div class="evidence-copy">{escape(txt(val(fact, "value")))}</div><div class="evidence-meta">{escape(_provenance_line(fact))}</div></div>', unsafe_allow_html=True)


def _render_conflicts_missing(case) -> None:
    conflicts = list(case.conflicts or []); missing = list(case.missing_items or [])
    st.markdown("#### Data conflicts"); st.caption("When two represented source statements disagree, the system keeps both rather than silently choosing one.")
    if not conflicts: st.success("No source-level conflicts are represented at this stage.")
    for conflict in conflicts:
        severity = human(val(conflict, "severity", "not represented")); st.markdown('<div class="guardrail"><strong>'+escape(f"{txt(val(conflict, 'field'))} · {severity}")+'</strong><p>'+escape(f"Source statement A: {txt(val(conflict, 'value_a'))}")+'<br>'+escape(f"Source statement B: {txt(val(conflict, 'value_b'))}")+'</p></div>', unsafe_allow_html=True)
    st.markdown("#### Missing decision-critical information")
    if not missing: st.success("No missing-item records are represented yet. The deterministic Missing Information Agent runs again before specialist routing.")
    for item in missing:
        blocking = bool(val(item, "recommendation_blocking", False)); st.markdown(f'<div class="evidence-card"><div class="evidence-title">{escape(txt(val(item, "field")))}{" · BLOCKING" if blocking else ""}</div><div class="evidence-copy">{escape(txt(val(item, "reason")))}</div><div class="evidence-meta">Availability: {escape(txt(val(item, "availability")))} · Importance: {escape(human(val(item, "importance")))}</div></div>', unsafe_allow_html=True)
    if any(bool(val(item, "recommendation_blocking", False)) for item in missing): st.info("If a blocking item remains unresolved, the later workflow will abstain and tell you what information is needed next instead of manufacturing a recommendation.")


def _render_case_summary(case) -> None:
    case_facts(case); st.markdown("#### Clinical course snapshot"); _treatment_timeline(case)
    blocking = [x for x in (case.missing_items or []) if val(x, "recommendation_blocking", False)]; conflicts = list(case.conflicts or []); what_we_know = [f"Diagnosis represented as {txt(case.diagnosis.value)}.", f"Disease state represented as {txt(case.disease_state.value)}.", f"{len(case.treatments or [])} treatment episode(s) and {len(case.molecular_findings or [])} molecular finding(s) are represented."]; attention = []
    if case.stage is None: attention.append("Stage is not explicitly represented.")
    if blocking: attention.append(f"{len(blocking)} recommendation-blocking missing item(s) are already represented.")
    if conflicts: attention.append(f"{len(conflicts)} source conflict(s) require attention.")
    if not attention: attention.append("No obvious blocking issue is represented yet; the formal integrity and missing-information gates run again before analysis.")
    c1,c2 = st.columns(2,gap="medium")
    with c1:
        st.markdown("**What we know from the represented case**")
        for item in what_we_know: st.write("• "+item)
    with c2:
        st.markdown("**What still needs attention**")
        for item in attention: st.write("• "+item)


def _review_nav() -> str:
    options=[("summary","1","Case summary","Diagnosis, disease state, board question, and clinical course."),("treatment","2","Treatment history","Prior regimens, response, toxicity, and timing."),("biology","3","Molecular & pathology","Molecular findings, pathology, imaging, and source traces."),("gaps","4","Conflicts & missing","Source disagreements and decision-critical gaps.")]; current=st.session_state.get("ag_review_section","summary"); st.markdown('<div class="review-nav-note">Review each panel before confirming the case.</div>', unsafe_allow_html=True)
    for key,num,title,copy in options:
        if st.button(f"{num}. {title}", type="primary" if current==key else "secondary", use_container_width=True, key=f"ag_review_nav_{key}"): st.session_state.ag_review_section=key; st.rerun()
        st.caption(copy)
    return current


def render_review() -> None:
    case=st.session_state.ag_case
    if case is None: goto("intake"); return
    stage_guidance("Case review","Check whether the structured record actually matches the source before the system gathers patient-level evidence.","Confirm the representation","Review the four panels, add any relevant clinician context, then explicitly confirm the source-traced case.")
    turn("Tumor Board Agent · Case review","I structured the case into the information a tumor board usually needs. Your job here is not to agree with a treatment recommendation; it is only to verify that I represented the source correctly.",chips=[claim_chip("source"),claim_chip("human")])
    left,right=st.columns([0.7,2.3],gap="large")
    with left: current=_review_nav()
    with right:
        if current=="summary": _render_case_summary(case)
        elif current=="treatment": _render_treatment_history(case)
        elif current=="biology": _render_molecular_pathology(case)
        else: _render_conflicts_missing(case)
    package=st.session_state.ag_extraction_package
    if package is not None:
        with st.expander("Detailed extraction quality and provenance"):
            c1,c2,c3,c4=st.columns(4); c1.metric("Verified provenance",f"{getattr(package,'provenance_rate',0.0)*100:.0f}%"); c2.metric("Verified traces",getattr(package,"provenance_verified",0)); c3.metric("Trace failures",len(getattr(package,"provenance_failures",[]) or [])); c4.metric("Extraction build",getattr(package,"extraction_version","v2.5")); warnings=getattr(package,"warnings",[]) or []
            if warnings:
                st.markdown("**Extraction warnings**")
                for warning in warnings: st.warning(warning)
    with st.expander("Optional clinician context: patient goals, preferences, or context not represented in the source"):
        st.text_area("Clinician context",key="ag_patient_context",height=100,placeholder="Examples: patient prioritizes outpatient therapy; strong interest in clinical trials; travel constraints; fertility goals..."); st.caption("This is recorded as clinician-provided context. It is not silently converted into a source fact and does not rewrite the original extraction.")
    with st.expander("If you disagree with the representation"):
        st.selectbox("Reason",["","Clinical context not represented","Source extraction is incorrect","Patient preference","Institutional practice","Other"],key="ag_clinician_override_reason"); st.text_area("Clinician note",key="ag_clinician_override",height=90,placeholder="Describe what should be revisited. The original extraction remains preserved for auditability."); st.caption("The current product preserves the system representation and your clinician note separately rather than rewriting history.")
    with st.expander("Technical detail · Full canonical case and provenance object"): st.json(case.model_dump(mode="json"),expanded=False)
    st.markdown('<div class="guardrail"><strong>Human checkpoint · Confirm the case representation</strong><p>Confirmation means the structured case matches the source material. It does not validate the diagnosis, molecular actionability, treatment choice, or evidence. Only source-traced facts can be marked human-reviewed.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="clinical-takeaway"><strong>Clinical takeaway</strong><p>Before continuing, you should be able to answer: “Is this the patient and clinical question I intend to bring to tumor board?”</p></div>', unsafe_allow_html=True)
    if st.button("Confirm case and continue to evidence",type="primary",use_container_width=True,key="ag_confirm_review"):
        st.session_state.ag_case=confirm_case_representation(case); st.session_state.ag_review_confirmed=True; st.session_state.ag_guideline_store=public_eln_aml_store(); st.session_state.ag_change_log.append("Clinician confirmed the source-traced case representation."); goto("evidence")


def _render_guideline(report) -> None:
    matches=val(report,"matched_guidance",[]) or []
    if not matches: st.info(txt(val(report,"summary"))); return
    for match in matches:
        date_value=txt(val(match,"publication_date"),""); date_html=f"<br>Publication/update date: {escape(date_value)}" if date_value else ""
        st.markdown('<div class="evidence-card"><span class="evidence-tier">Guideline / consensus</span>'+f'<div class="evidence-title" style="margin-top:8px">{escape(txt(val(match,"recommendation_text")))}</div><div class="evidence-copy">Source: {escape(txt(val(match,"source_title")))}<br>{escape(txt(val(match,"source_excerpt")))}{date_html}</div><div class="evidence-meta">{escape(txt(val(match,"source_locator"),""))}</div></div>', unsafe_allow_html=True)


def render_evidence() -> None:
    case=st.session_state.ag_case
    if case is None or not st.session_state.ag_review_confirmed: goto("review"); return
    stage_guidance("Evidence review","The agent is gathering evidence across distinct channels. Each channel keeps its own claim boundary.","Review what is usable","Attest only molecular and safety records you have reviewed. A retrieved record is not automatically patient-specific evidence.")
    if st.session_state.ag_evidence_candidates is None and not st.session_state.ag_evidence_error:
        with st.status("Gathering governed evidence...",expanded=True) as status:
            status.write("Matching verified guidance where applicable"); status.write("Retrieving candidate CIViC molecular evidence"); status.write("Retrieving candidate FDA label safety sections"); status.write("Preparing PubMed, ClinicalTrials.gov, and translational channels for later question-aware routing"); ensure_evidence_candidates(); status.update(label="External evidence retrieval was incomplete" if st.session_state.ag_evidence_error else "Evidence candidates retrieved. Human review is required where shown.",state="error" if st.session_state.ag_evidence_error else "complete")
    guideline_store=st.session_state.ag_guideline_store or public_eln_aml_store(); st.session_state.ag_guideline_store=guideline_store; report=GuidelineAgent(guideline_store).run(case); st.session_state.ag_guideline_report=report
    turn("Tumor Board Agent · Evidence review","I keep formal guidance, molecular evidence, safety labels, literature, trials, and translational evidence separate. That prevents a database hit or mechanistic paper from being promoted into a treatment recommendation without the required support.",chips=[claim_chip("retrieved"),claim_chip("human")])
    st.markdown('<div class="logic-strip"><div class="logic-cell"><div class="logic-k">Guideline / consensus</div><div class="logic-v">Verified source matching</div></div><div class="logic-cell"><div class="logic-k">Molecular</div><div class="logic-v">Retrieve → clinician attest</div></div><div class="logic-cell"><div class="logic-k">Safety</div><div class="logic-v">Retrieve → clinician attest</div></div><div class="logic-cell"><div class="logic-k">Literature & trials</div><div class="logic-v">Bounded downstream retrieval</div></div></div>', unsafe_allow_html=True)
    with st.expander("Guideline / consensus evidence · What formal guidance supports",expanded=True): _render_guideline(report); st.caption("If formal guidance cannot be matched under its stage, disease-state, molecular, source, or currency prerequisites, the system does not substitute model memory.")
    if st.session_state.ag_evidence_error:
        st.warning("Some external evidence sources could not be commissioned in this run. The later workflow will show the clinical consequence and withhold dependent claims.")
        with st.expander("Technical retrieval error"): st.code(st.session_state.ag_evidence_error)
        candidates=None
    else: candidates=st.session_state.ag_evidence_candidates
    molecular_records=list(val(candidates,"molecular_records",[]) or []); safety_records=list(val(candidates,"safety_records",[]) or []); warnings=list(val(candidates,"warnings",[]) or [])
    if warnings:
        with st.expander("Evidence-source warnings"):
            for warning in warnings: st.warning(warning)
    st.markdown("### Molecular evidence"); st.caption("CIViC results are candidate evidence. Select only records you reviewed and accept for this workup. A molecular database record does not automatically establish actionability for this patient.")
    molecular_selected=set()
    if molecular_records:
        for record in molecular_records[:30]:
            evidence_id=txt(val(record,"evidence_id")); checked=st.checkbox(f"Accept for this workup · {evidence_id} · {txt(val(record,'gene'))} · {txt(val(record,'therapy'),'no therapy represented')}",key=f"ag_mol_{evidence_id}")
            if checked: molecular_selected.add(evidence_id)
            with st.expander(f"Why this record was retrieved · {evidence_id}"):
                st.write(txt(val(record,"evidence_summary"))); locator=txt(val(record,"source_locator"),"")
                if locator: st.caption("Source: "+locator)
    else: st.info("No candidate CIViC molecular records were retrieved for this case.")
    st.markdown("### Safety evidence"); st.caption("FDA label text is source evidence. Accepting a source span verifies the label evidence you reviewed; it does not automatically establish a patient-specific contraindication, dose, or treatment decision.")
    safety_selected=set()
    if safety_records:
        for idx,record in enumerate(safety_records[:30]):
            checked=st.checkbox(f"Accept for this workup · {txt(val(record,'therapy'))} · {human(val(record,'section'))}",key=f"ag_safe_{idx}")
            if checked: safety_selected.add(idx)
            with st.expander(f"Why this safety record matters · {txt(val(record,'therapy'))} · {human(val(record,'section'))}"):
                st.write(safety_candidate_excerpt(record)); url=txt(val(record,"source_url"),"")
                if url: st.caption("Source: "+url)
    else: st.info("No FDA label candidates were retrieved for the represented therapies.")
    guideline_matches=len(val(report,"matched_guidance",[]) or [])
    st.markdown('<div class="clinical-takeaway"><strong>What is usable vs. still provisional</strong><p>'+escape(f"Formal guidance matches: {guideline_matches}. Molecular candidates selected: {len(molecular_selected)} of {len(molecular_records)}. Safety candidates selected: {len(safety_selected)} of {len(safety_records)}. Literature and trial channels remain bounded downstream retrieval channels.")+'</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="guardrail"><strong>Human checkpoint · Admit reviewed evidence</strong><p>The agent can retrieve evidence automatically, but it cannot promote candidate molecular or safety records into patient-level reasoning until you explicitly accept the source records you reviewed.</p></div>', unsafe_allow_html=True)
    if st.button("Confirm reviewed evidence and run agent analysis",type="primary",use_container_width=True,key="ag_confirm_evidence"):
        commission_evidence(molecular_records,molecular_selected,safety_records,safety_selected); st.session_state.ag_change_log.append(f"Clinician attested {len(molecular_selected)} molecular and {len(safety_selected)} safety evidence record(s)."); goto("analysis")
