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
    txt,
    val,
)
from app.agentic_layout import case_facts, claim_chip, turn
from services.evidence_commissioning import safety_candidate_excerpt
from services.eln_aml_guidance import public_eln_aml_store


def render_intake() -> None:
    turn(
        "Tumor Board Agent · Intake",
        "I will build a source-traced case, pause for your confirmation of the structured representation, gather bounded evidence, run deterministic safety gates, challenge the synthesis, and then produce a decision-support brief.",
        chips=[claim_chip("human")],
    )
    st.markdown(
        '<div class="guardrail"><strong>Guardrail 1 · Case source</strong><p>Choose a provenance-bearing synthetic case, paste a de-identified narrative, or upload a document. Extracted text is not treated as clinical truth until source traces and the structured representation are reviewed.</p></div>',
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["Synthetic case", "Paste narrative", "Upload document"])
    with tabs[0]:
        st.caption("Validated synthetic AML fixture. It remains explicitly labeled synthetic throughout the workup.")
        if st.button("Load synthetic case", type="primary", use_container_width=True, key="ag_load_syn"):
            st.session_state.ag_case = load_synthetic()
            st.session_state.ag_raw_extraction = None
            st.session_state.ag_extraction_package = None
            goto("review")
    with tabs[1]:
        narrative = st.text_area("De-identified case narrative", height=220, placeholder="Paste a de-identified tumor-board summary...", key="ag_text")
        if st.button("Extract and review", type="primary", use_container_width=True, key="ag_extract_text"):
            if not narrative.strip():
                st.warning("Paste a narrative first.")
            else:
                try:
                    with st.status("Parsing and extracting a source-traced case...", expanded=True) as status:
                        package = extract_text_case(narrative)
                        status.update(label="Extraction complete. Human review required.", state="complete")
                    st.session_state.ag_case = package.case
                    st.session_state.ag_raw_extraction = package.raw_extraction
                    st.session_state.ag_extraction_package = package
                    goto("review")
                except Exception as exc:
                    st.error(f"Extraction failed safely: {type(exc).__name__}: {exc}")
    with tabs[2]:
        upload = st.file_uploader("Upload a de-identified document", type=["txt", "md", "pdf", "docx"], key="ag_upload")
        if st.button("Parse, extract, and review", type="primary", use_container_width=True, key="ag_extract_upload"):
            if upload is None:
                st.warning("Upload a document first.")
            else:
                try:
                    with st.status("Parsing and extracting a source-traced case...", expanded=True) as status:
                        package = extract_upload_case(upload)
                        status.update(label="Extraction complete. Human review required.", state="complete")
                    st.session_state.ag_case = package.case
                    st.session_state.ag_raw_extraction = package.raw_extraction
                    st.session_state.ag_extraction_package = package
                    goto("review")
                except Exception as exc:
                    st.error(f"Extraction failed safely: {type(exc).__name__}: {exc}")


def render_review() -> None:
    case = st.session_state.ag_case
    if case is None:
        goto("intake")
        return
    turn(
        "Tumor Board Agent · Case review",
        "I structured the case. Review the represented facts and source traces before evidence retrieval begins.",
        chips=[claim_chip("source")],
    )
    case_facts(case)
    package = st.session_state.ag_extraction_package
    if package is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Provenance rate", f"{getattr(package, 'provenance_rate', 0.0)*100:.0f}%")
        c2.metric("Verified traces", getattr(package, "provenance_verified", 0))
        c3.metric("Trace failures", len(getattr(package, "provenance_failures", []) or []))
        c4.metric("Extraction", getattr(package, "extraction_version", "v2.5"))
        warnings = getattr(package, "warnings", []) or []
        if warnings:
            with st.expander("Extraction warnings"):
                for warning in warnings:
                    st.warning(warning)
    with st.expander("Full represented case and provenance"):
        st.json(case.model_dump(mode="json"), expanded=False)
    st.markdown(
        '<div class="guardrail"><strong>Guardrail 2 · Clinician confirmation</strong><p>Confirmation means the structured representation matches the source material. It does not validate the diagnosis, treatment choice, molecular actionability, or evidence. Only facts that already carry verified provenance are marked human-reviewed.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Confirm source-traced representation and gather evidence", type="primary", use_container_width=True, key="ag_confirm_review"):
        st.session_state.ag_case = confirm_case_representation(case)
        st.session_state.ag_review_confirmed = True
        st.session_state.ag_guideline_store = public_eln_aml_store()
        goto("evidence")


def _render_guideline(report) -> None:
    matches = val(report, "matched_guidance", []) or []
    if not matches:
        st.info(txt(val(report, "summary")))
        return
    for match in matches:
        st.markdown(
            '<div class="evidence-card">'
            f'<div class="evidence-title">{escape(txt(val(match, "recommendation_text")))}</div>'
            f'<div class="evidence-copy">Source: {escape(txt(val(match, "source_title")))}<br>{escape(txt(val(match, "source_excerpt")))}</div>'
            f'<div class="evidence-meta">{escape(txt(val(match, "source_locator"), ""))}</div></div>',
            unsafe_allow_html=True,
        )


def render_evidence() -> None:
    case = st.session_state.ag_case
    if case is None or not st.session_state.ag_review_confirmed:
        goto("review")
        return

    if st.session_state.ag_evidence_candidates is None and not st.session_state.ag_evidence_error:
        with st.status("Gathering governed evidence channels...", expanded=True) as status:
            status.write("Matching public ELN guidance where applicable")
            status.write("Retrieving candidate CIViC molecular evidence")
            status.write("Retrieving candidate FDA label safety sections")
            ensure_evidence_candidates()
            if st.session_state.ag_evidence_error:
                status.update(label="External evidence retrieval stopped safely", state="error")
            else:
                status.update(label="Candidate evidence retrieved. Human attestation is required where shown.", state="complete")

    guideline_store = st.session_state.ag_guideline_store or public_eln_aml_store()
    st.session_state.ag_guideline_store = guideline_store
    report = GuidelineAgent(guideline_store).run(case)
    st.session_state.ag_guideline_report = report
    turn(
        "Tumor Board Agent · Evidence",
        f"Guidance matching finished with status <b>{escape(human(val(report, 'status')))}</b>. Candidate evidence from external sources is displayed below for explicit attestation before it can support patient-level reasoning.",
        chips=[claim_chip("retrieved")],
    )
    with st.expander("Guideline evidence", expanded=True):
        _render_guideline(report)

    if st.session_state.ag_evidence_error:
        st.warning("External evidence commissioning could not complete: " + st.session_state.ag_evidence_error)
        candidates = None
    else:
        candidates = st.session_state.ag_evidence_candidates

    molecular_records = list(val(candidates, "molecular_records", []) or [])
    safety_records = list(val(candidates, "safety_records", []) or [])
    warnings = list(val(candidates, "warnings", []) or [])
    if warnings:
        with st.expander("Retrieval warnings"):
            for warning in warnings:
                st.warning(warning)

    st.markdown("#### Molecular evidence commissioning")
    st.caption("CIViC records are retrieved evidence candidates, not patient-specific truth. Select only records you have reviewed and are willing to attest for this workup.")
    molecular_selected: set[str] = set()
    if molecular_records:
        for record in molecular_records[:30]:
            evidence_id = txt(val(record, "evidence_id"))
            checked = st.checkbox(
                f"Attest {evidence_id} · {txt(val(record, 'gene'))} · {txt(val(record, 'therapy'), 'no therapy represented')}",
                key=f"ag_mol_{evidence_id}",
            )
            if checked:
                molecular_selected.add(evidence_id)
            with st.expander(f"Evidence details · {evidence_id}"):
                st.write(txt(val(record, "evidence_summary")))
                st.caption(txt(val(record, "source_locator"), "Source locator not represented"))
    else:
        st.info("No candidate CIViC molecular records were retrieved for this case.")

    st.markdown("#### Safety evidence commissioning")
    st.caption("FDA label text is source evidence. Attesting a label section does not itself establish a patient-specific contraindication, dose, or treatment decision.")
    safety_selected: set[int] = set()
    if safety_records:
        for idx, record in enumerate(safety_records[:30]):
            checked = st.checkbox(
                f"Attest FDA section {idx + 1} · {txt(val(record, 'therapy'))} · {human(val(record, 'section'))}",
                key=f"ag_safe_{idx}",
            )
            if checked:
                safety_selected.add(idx)
            with st.expander(f"Label details · {txt(val(record, 'therapy'))} · {human(val(record, 'section'))}"):
                st.write(safety_candidate_excerpt(record))
                st.caption(txt(val(record, "source_url"), "Source URL not represented"))
    else:
        st.info("No candidate FDA label safety sections were retrieved for this case.")

    st.markdown(
        '<div class="guardrail"><strong>Guardrail 3 · Evidence sufficiency and attestation</strong><p>The agent can gather evidence automatically, but only human-attested candidate molecular and safety records enter the governed patient-level evidence stores. Trial matches remain matches, not eligibility. Literature retrieval remains candidate literature until clinically appraised.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Use attested evidence and run guarded analysis", type="primary", use_container_width=True, key="ag_run_analysis"):
        try:
            commission_evidence(molecular_records, molecular_selected, safety_records, safety_selected)
            goto("analysis")
        except Exception as exc:
            st.error(f"Evidence commissioning stopped safely: {type(exc).__name__}: {exc}")
