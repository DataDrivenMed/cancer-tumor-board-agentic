from __future__ import annotations

from html import escape

import streamlit as st

from app.xai_theme import inject_xai_theme
from qualification.cases import CASES
from qualification.challenge_cases_v2 import (
    REPEATED_STOCHASTIC_CASE_IDS,
    REPEATED_STOCHASTIC_REPEATS,
    TARGETED_CASES,
    UNSEEN_CASES,
)
from qualification.remediation_cases_v25 import (
    REMEDIATION_CASES_V25,
    REMEDIATION_REPEAT_CASE_IDS_V25,
    REMEDIATION_REPEAT_COUNT_V25,
)
from services.oncology_programs import PROGRAMS
from services.pathway_validation import COMMON_CORE_QUALIFICATION, get_pathway_validation_status


def _nav(active: str) -> None:
    with st.sidebar:
        st.markdown(
            '<div class="fx-side-brand"><div class="fx-side-mark">TB</div><div>'
            '<div class="fx-side-name">Tumor Board</div>'
            '<div class="fx-side-sub">Governed research decision support</div></div></div>',
            unsafe_allow_html=True,
        )
        links = [
            ("pages/04_Agentic_Workspace.py", "Agentic Workspace", "agentic"),
            ("pages/01_Validation.py", "Validation & scope", "validation"),
            ("pages/03_Architecture.py", "Architecture", "architecture"),
            ("pages/02_About.py", "Scientific scope", "about"),
        ]
        st.markdown('<div class="fx-side-label">Navigate</div>', unsafe_allow_html=True)
        for page, label, key in links:
            st.page_link(page, label=label, disabled=active == key, use_container_width=True)
        st.markdown(
            '<div class="fx-side-label">System</div><div class="fx-side-system">'
            '<div><i></i><strong>Common core qualified</strong></div>'
            '<span>Frozen synthetic software qualification record available</span>'
            '<div><i class="amber"></i><strong>Clinical release not established</strong></div></div>',
            unsafe_allow_html=True,
        )


def _base(active: str) -> None:
    inject_xai_theme()
    _nav(active)
    st.markdown(
        """
<style>
.ref-hero{padding:18px 0 26px;max-width:960px;border-bottom:1px solid var(--line);margin-bottom:22px}
.ref-hero h1{font-size:46px;line-height:1.04;margin:7px 0 10px}.ref-hero p{font-size:15px;line-height:1.65;color:var(--body);max-width:880px}
.ref-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:12px 0 22px}.ref-grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}.ref-grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.ref-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:15px}.ref-card.primary{background:var(--panelhi);border-color:var(--linehi)}.ref-card h3{font-size:18px;margin:0 0 6px}.ref-card p{font-size:12.5px;line-height:1.55;margin:0;color:var(--body)}
.ref-kpi{font-family:var(--serif);font-size:30px;color:var(--ink);font-weight:500}.ref-kpi-label{font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-top:5px}
.ref-section{font-family:var(--serif);font-size:28px;color:var(--ink);font-weight:500;margin:31px 0 6px}.ref-sub{font-size:13px;color:var(--muted);line-height:1.55;max-width:900px;margin-bottom:12px}
.ref-row{display:grid;grid-template-columns:1.25fr 1fr 2.4fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line2);font-size:12px}.ref-row strong{color:var(--ink)}.ref-row span{color:var(--body)}
.ref-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:14px 0}.ref-node{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:13px}.ref-node b{display:block;color:var(--ink);font-size:13px}.ref-node small{display:block;color:var(--muted);font-size:10.5px;line-height:1.45;margin-top:5px}
.ref-warning{background:rgba(224,176,98,.08);border:1px solid rgba(224,176,98,.3);border-radius:var(--r);padding:14px 15px;color:var(--body);font-size:12.5px;line-height:1.55}.ref-ok{background:rgba(108,194,160,.08);border:1px solid rgba(108,194,160,.28);border-radius:var(--r);padding:14px 15px;color:var(--body);font-size:12.5px;line-height:1.55}
.ref-policy{display:grid;grid-template-columns:90px 1fr;gap:12px;padding:11px 0;border-bottom:1px solid var(--line2)}.ref-policy b{font:700 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em}.ref-policy span{font-size:12px;color:var(--body);line-height:1.5}
.ref-stream{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:13px 14px;margin:7px 0}.ref-stream strong{font-size:13px;color:var(--ink)}.ref-stream small{display:block;font-size:11px;color:var(--muted);line-height:1.45;margin-top:4px}.ref-stream .count{font-family:var(--serif);font-size:26px;color:var(--accent2);white-space:nowrap}
@media(max-width:900px){.ref-grid,.ref-grid.four,.ref-grid.two{grid-template-columns:1fr}.ref-flow{grid-template-columns:1fr}.ref-row{grid-template-columns:1fr}.ref-hero h1{font-size:38px}}
</style>
""",
        unsafe_allow_html=True,
    )


def _footer() -> None:
    st.markdown(
        '<div class="fx-footer"><div>Research decision support · source-traced and auditable</div>'
        '<div>Software qualification is not clinical validation</div></div>',
        unsafe_allow_html=True,
    )


def _policy_row(label: str, text: str) -> str:
    return f'<div class="ref-policy"><b>{escape(label)}</b><span>{escape(text)}</span></div>'


def render_validation() -> None:
    _base("validation")
    q = COMMON_CORE_QUALIFICATION
    challenge_planned = len(TARGETED_CASES) + len(UNSEEN_CASES) + len(REPEATED_STOCHASTIC_CASE_IDS) * REPEATED_STOCHASTIC_REPEATS
    remediation_planned = len(REMEDIATION_CASES_V25) + len(REMEDIATION_REPEAT_CASE_IDS_V25) * REMEDIATION_REPEAT_COUNT_V25

    st.markdown(
        '<div class="ref-hero"><div class="fx-kicker">Validation, qualification, and trust boundary</div>'
        '<h1>What has been tested, what has not, and what the system is allowed to claim.</h1>'
        '<p>This page is intentionally layered for clinicians, governance reviewers, and research or publication reviewers. '
        'The product separates software qualification, disease-specific validation, prospective clinical validation, and governed clinical release.</p></div>',
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)
    a.metric("Common-core result", str(q.get("result", "unknown")).upper())
    b.metric("Matrix executions", q.get("matrix_executions", 0))
    c.metric("Dedicated tests", q.get("dedicated_pan_oncology_tests_passed", 0))
    d.metric("Full regression tests", q.get("full_regression_tests_passed", 0))
    st.caption(
        f"Qualified build: {q.get('qualified_build', 'not represented')} · "
        f"CI run: {q.get('workflow_run_id', 'not represented')} · "
        f"date: {q.get('qualification_date', 'not represented')}"
    )

    st.markdown('<div class="ref-section">The validation ladder</div><div class="ref-sub">Each rung answers a different question. A higher rung requires evidence that a lower rung cannot substitute for.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-flow">'
        '<div class="ref-node"><b>1. Architecture ready</b><small>Registered routing, schemas, deterministic gates, and fail-closed behavior exist.</small></div>'
        '<div class="ref-node"><b>2. Common-core qualified</b><small>Synthetic software qualification of shared behavior across registered programs.</small></div>'
        '<div class="ref-node"><b>3. Disease-specific qualified</b><small>Disease-specific rules and evidence packages tested against predefined software criteria.</small></div>'
        '<div class="ref-node"><b>4. Clinical validation</b><small>Independent clinical reference-standard evaluation, ideally including silent prospective assessment.</small></div>'
        '<div class="ref-node"><b>5. Clinical release</b><small>Governance, monitoring, accountability, privacy, security, and institution-specific authorization.</small></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">Qualification stack</div><div class="ref-sub">The original application developed several distinct test streams. They are retained as separate evidence because they answer different reliability questions.</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ref-stream"><div><strong>Baseline extraction qualification</strong><small>Q01 to Q10. Tests straightforward extraction, missing information, conflict preservation, pending-result non-inference, chronology, molecular over-interpretation, historical contamination, and safe abstention.</small></div><div class="count">{len(CASES)}</div></div>'
        f'<div class="ref-stream"><div><strong>Challenge validation v2</strong><small>{len(TARGETED_CASES)} targeted cases plus {len(UNSEEN_CASES)} unseen cases. Six frozen cases are each repeated three times to detect stochastic instability.</small></div><div class="count">{challenge_planned}</div></div>'
        f'<div class="ref-stream"><div><strong>Remediation validation v2.5</strong><small>{len(REMEDIATION_CASES_V25)} frozen remediation cases plus six repeated cases run three times. Targets failure modes discovered during earlier qualification cycles.</small></div><div class="count">{remediation_planned}</div></div>'
        f'<div class="ref-stream"><div><strong>Pan-oncology common-core qualification</strong><small>Fourteen registered tumor-board programs across fifteen common scenarios, with dedicated and full-regression test gates.</small></div><div class="count">{q.get("matrix_executions", 0)}</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Challenge v2 acceptance policy and failure modes", expanded=True):
        st.markdown(
            _policy_row("Green", "100% strict overall pass across a stream, 100% exact provenance, zero prohibited assertions, and zero unsupported provenance assertions.")
            + _policy_row("Amber", "At least 95% strict overall pass with exact provenance still 100%, zero prohibited or unsupported assertions, and no repeated-subset case failing more than once.")
            + _policy_row("Red", "Below 95%, any provenance failure, any prohibited or unsupported assertion, or recurrent failure of the same repeated-subset case."),
            unsafe_allow_html=True,
        )
        st.markdown("**Targeted failure modes represented**")
        modes = [case.target_failure_mode for case in TARGETED_CASES]
        st.write(" · ".join(modes))
        st.markdown("**Unseen generalization stream**")
        st.caption(
            "Colorectal, breast, melanoma, lung, ovarian, pancreatic, renal, prostate, CNS, and unknown-primary cases test whether the extraction and safety logic generalizes beyond the initial hematologic examples."
        )

    with st.expander("Remediation v2.5 acceptance policy and cases", expanded=True):
        st.markdown(
            _policy_row("Green", "30/30 strict passes, 100% exact provenance, zero prohibited assertions, zero unsupported provenance assertions, zero semantic-integrity errors, no duplicate treatment episodes, deterministic missing-information ontology consistency, and every repeated case 3/3.")
            + _policy_row("Amber", "29/30 strict passes with all provenance, safety, duplicate-treatment, and ontology-integrity gates perfect, with no repeated case failing more than once.")
            + _policy_row("Red", "28/30 or fewer strict passes, any provenance or safety failure, any semantic-integrity error, any duplicate treatment episode, any ontology mismatch, or any repeated case failing more than once."),
            unsafe_allow_html=True,
        )
        rows = [
            {
                "Case": case.case_id,
                "Scenario": case.title,
                "Failure mode": case.target_failure_mode,
                "Strict core gate": case.strict_core_gate,
            }
            for case in REMEDIATION_CASES_V25
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown('<div class="ref-section">Current program status</div><div class="ref-sub">All registered oncology programs share the qualified common architecture. That does not establish disease-specific treatment correctness.</div>', unsafe_allow_html=True)
    program_rows = []
    for program in PROGRAMS:
        status = get_pathway_validation_status(program.program_id)
        program_rows.append(
            {
                "Program": program.display_name,
                "State": status.label,
                "Common-core qualified": status.common_core_qualified,
                "Disease-specific software qualified": status.disease_specific_software_qualified,
                "Clinically validated": status.clinically_validated,
            }
        )
    st.dataframe(program_rows, use_container_width=True, hide_index=True)

    st.markdown('<div class="ref-section">What the common-core qualification tested</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid">'
        '<div class="ref-card"><h3>Routing and program assignment</h3><p>Registered programs, ordinary routing, safety retention, safety-only routing, molecular and trial question routing, pediatric tie-breaking, and deterministic reassignment of incorrect program metadata.</p></div>'
        '<div class="ref-card"><h3>Integrity and missingness</h3><p>Pending diagnosis, high-severity conflicts, missing or conflicting decision-critical information, explicit stage handling, and prevention of specialist routing when blocking information is unresolved.</p></div>'
        '<div class="ref-card"><h3>Fail-closed evidence behavior</h3><p>Empty evidence channels cannot create guideline, molecular-actionability, translational-actionability, literature, trial-match, or safety claims.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "A stage-matching defect discovered during qualification allowed Stage II to match Stage III under generic token matching. "
        "The matcher was corrected to exact canonical stage comparison, and the complete qualification gate was rerun successfully on the recorded build."
    )

    st.markdown('<div class="ref-section">Guardrail coverage in the live workflow</div><div class="ref-sub">These controls are enforced in code and surfaced in the Agentic Workspace inspector.</div>', unsafe_allow_html=True)
    guards = [
        ("Semantic integrity", "Pre-routing", "Blocks model/schema contradictions before downstream reasoning."),
        ("Case integrity", "Pre-routing", "Checks provenance, unresolved conflicts, and unsafe case representation."),
        ("Missing information", "Pre-routing", "Blocking gaps prevent specialist routing; nonblocking gaps remain visible."),
        ("Explicit stage prerequisite", "Guideline", "Stage-dependent guidance requires verified provenance, clinician confirmation, and exact stage match."),
        ("Guideline evidence boundary", "Guideline", "Only current, verified, authorized guidance can support formal guideline claims."),
        ("Molecular evidence boundary", "Molecular", "Gene identity or model memory cannot create actionability; evidence requires source and human verification."),
        ("Safety evidence boundary", "Safety", "Warnings and contraindications require verified attested evidence; a nonmatch is never treated as proof of safety."),
        ("Literature claim boundary", "Literature", "PubMed retrieval surfaces candidate literature but does not itself verify a clinical claim."),
        ("Trial eligibility boundary", "Trials", "A ClinicalTrials.gov match is explicitly not patient eligibility."),
        ("Translational boundary", "Translational", "Mechanistic evidence cannot establish treatment efficacy or patient-level actionability."),
        ("Clinical red team", "Post-synthesis", "Searches for unsupported leaps, conflicts, missing prerequisites, and recommendation-changing weaknesses."),
        ("Consensus gate", "Post-red-team", "Only adjudicated, supportable outputs can reach the final brief."),
        ("Brief claim preservation", "Presentation", "The brief and PDF are presentation transforms and cannot create new evidence."),
        ("Governed follow-up chat", "Presentation", "Follow-up answers are restricted to the represented case and governed outputs; unsupported questions abstain."),
    ]
    for name, layer, purpose in guards:
        st.markdown(
            f'<div class="ref-row"><strong>{escape(name)}</strong><span>{escape(layer)}</span><span>{escape(purpose)}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ref-section">Claims this product intentionally does not make</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-warning"><b>Not established:</b> disease-specific treatment correctness, completeness of disease-specific biomarker rules, correctness of every staging system, patient-specific drug appropriateness, clinical-trial eligibility, patient outcomes, unrestricted real-world safety, clinical validation, regulatory authorization, or institutional approval for routine patient-care use.</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "The challenge and remediation protocols define rigorous acceptance criteria. This page does not label an individual challenge or remediation stream as passed unless a frozen executed study result is available in the repository. The common-core PASS is supported by a frozen qualification record."
    )
    _footer()


def render_about() -> None:
    _base("about")
    st.markdown(
        '<div class="ref-hero"><div class="fx-kicker">Scientific scope and governance</div>'
        '<h1>A tumor-board instrument, not a general oncology chatbot.</h1>'
        '<p>The system is designed to improve how a multidisciplinary team represents a case, commissions evidence, exposes uncertainty, challenges its own synthesis, and records an auditable decision-support brief. It does not replace multidisciplinary clinical judgment.</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">Four information classes remain distinct</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid four">'
        '<div class="ref-card primary"><h3>Source fact</h3><p>A patient or case assertion with represented provenance. Human confirmation is recorded separately from extraction.</p></div>'
        '<div class="ref-card"><h3>Retrieved evidence</h3><p>Guideline, PubMed, CIViC, FDA label, ClinicalTrials.gov, or translational evidence brought into a bounded specialist channel.</p></div>'
        '<div class="ref-card"><h3>Derived interpretation</h3><p>Deterministic or agent-generated synthesis whose support and limitations remain linked to its source channels.</p></div>'
        '<div class="ref-card"><h3>Human judgment</h3><p>Clinician confirmation, evidence attestation, conflict resolution, or tumor-board adjudication. It is never silently inferred from a model response.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">Evidence model</div>', unsafe_allow_html=True)
    evidence = [
        ("Guidance", "Governed", "Current verified sources; exact stage and molecular prerequisites where required."),
        ("Molecular", "Retrieve + attest", "CIViC candidate retrieval plus explicit human attestation before patient-level use."),
        ("Safety", "Retrieve + attest", "FDA label candidate retrieval plus human attestation; label text remains distinct from a patient-specific contraindication or dose."),
        ("Literature", "Bounded retrieval", "PubMed retrieval identifies candidate literature; it is not critical appraisal or a treatment recommendation."),
        ("Clinical trials", "Bounded retrieval", "ClinicalTrials.gov matching; a match is not eligibility and does not recommend enrollment."),
        ("Translational", "Mechanistic", "Mechanistic, preclinical, and human-translational evidence remains separate from clinical actionability."),
    ]
    for name, state, purpose in evidence:
        st.markdown(
            f'<div class="ref-row"><strong>{escape(name)}</strong><span>{escape(state)}</span><span>{escape(purpose)}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ref-section">Human control points</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid">'
        '<div class="ref-card"><h3>Case review</h3><p>Confirm that the structured representation matches the source. Unsupported facts do not become verified merely because a clinician continues.</p></div>'
        '<div class="ref-card"><h3>Evidence attestation</h3><p>Review candidate molecular and safety evidence before it is admitted to patient-level reasoning.</p></div>'
        '<div class="ref-card"><h3>Decision adjudication</h3><p>The system produces decision support, alternatives, conditions, uncertainty, and abstention. Final patient-care decisions remain with qualified clinicians and local governance.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">Privacy and deployment boundary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-warning">The public research deployment is intended for synthetic or appropriately de-identified data. Secrets are supplied through deployment secret management rather than committed files. A clinical deployment would require institution-specific privacy, security, validation, monitoring, accountability, and release controls.</div>',
        unsafe_allow_html=True,
    )
    _footer()


def render_architecture() -> None:
    _base("architecture")
    st.markdown(
        '<div class="ref-hero"><div class="fx-kicker">System architecture</div>'
        '<h1>The conversation is the surface. The governed pipeline is the system.</h1>'
        '<p>The Agentic Workspace does not replace the original engine. It presents the underlying case, evidence, safety, challenge, consensus, and audit logic as a cleaner stage-by-stage conversation with a live inspector.</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">End-to-end execution path</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-flow">'
        '<div class="ref-node"><b>1. Intake</b><small>Synthetic fixture, de-identified text, or document parsing; extraction v2.5; source provenance.</small></div>'
        '<div class="ref-node"><b>2. Human review</b><small>Confirm the structured representation while preserving unsupported, pending, conflicting, and missing facts.</small></div>'
        '<div class="ref-node"><b>3. Evidence commissioning</b><small>Guidance matching, CIViC and FDA candidate retrieval, human attestation, and bounded public-source channels.</small></div>'
        '<div class="ref-node"><b>4. Governed analysis</b><small>Semantic integrity, case integrity, missing information, routing, specialists, synthesis, red team, and consensus.</small></div>'
        '<div class="ref-node"><b>5. Decision brief</b><small>Alternatives, conditions, uncertainty, trials, safety, provenance, audit, governed follow-up, and PDF export.</small></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">What happens underneath the conversation</div>', unsafe_allow_html=True)
    layers = [
        ("Representation", "Canonical CancerTumorBoardCase", "Source-traced facts, status, provenance, treatments, molecular findings, conflicts, missing items, and clinical question."),
        ("Pre-routing safety", "Deterministic gates", "Semantic integrity, quality checks, Case Integrity / Data QA, and Missing Information can stop routing before any specialist synthesis."),
        ("Routing", "Question-aware router", "Selects only the specialist agents required by the represented question and complexity."),
        ("Specialists", "Bounded agents", "Guideline, molecular, literature, clinical trials, safety, and translational agents operate inside distinct evidence boundaries."),
        ("Challenge", "Clinical Red Team", "Looks for unsupported leaps, missing prerequisites, conflict, and recommendation-changing weaknesses."),
        ("Adjudication", "Consensus", "Produces an explicit decision state, alternatives, conditions, uncertainty, discussion priorities, and support strength."),
        ("Presentation", "Brief, chat, PDF", "Transforms governed outputs into readable artifacts without adding evidence or silently changing the decision state."),
    ]
    for layer, system, purpose in layers:
        st.markdown(
            f'<div class="ref-row"><strong>{escape(layer)}</strong><span>{escape(system)}</span><span>{escape(purpose)}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ref-section">Why the right-side inspector exists</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid">'
        '<div class="ref-card"><h3>Explain execution</h3><p>Shows stage, selected agents, runtime evidence channels, current decision state, and latest audit event without polluting the main conversation.</p></div>'
        '<div class="ref-card"><h3>Expose guardrails</h3><p>Shows source-trace state, human confirmation, evidence attestation, integrity disposition, blocking gaps, red-team state, and safe-to-display status.</p></div>'
        '<div class="ref-card"><h3>Preserve epistemic boundaries</h3><p>Source fact, retrieved evidence, derived interpretation, and human judgment remain visually distinct throughout the workup.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ref-section">Failure behavior</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-warning"><b>Fail closed by design:</b> an unavailable evidence source, failed verification, unresolved blocking information, semantic-integrity failure, or unsupported specialist claim cannot silently fall back to general model knowledge. The workflow can abstain, withhold synthesis, or complete with explicit limitations.</div>',
        unsafe_allow_html=True,
    )
    _footer()
