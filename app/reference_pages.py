from __future__ import annotations

from html import escape

import streamlit as st

from app.xai_theme import inject_xai_theme
from services.oncology_programs import PROGRAMS
from services.pathway_validation import COMMON_CORE_QUALIFICATION, get_pathway_validation_status


def _nav(active: str) -> None:
    with st.sidebar:
        st.markdown('<div class="fx-side-brand"><div class="fx-side-mark">TB</div><div><div class="fx-side-name">Tumor Board</div><div class="fx-side-sub">Research decision support</div></div></div>', unsafe_allow_html=True)
        links = [
            ("pages/04_Agentic_Workspace.py", "Agentic Workspace", "agentic"),
            ("pages/00_Clinical_Workspace.py", "Classic Workspace", "classic"),
            ("pages/01_Validation.py", "Validation & scope", "validation"),
            ("pages/03_Architecture.py", "Architecture", "architecture"),
            ("pages/02_About.py", "About", "about"),
        ]
        st.markdown('<div class="fx-side-label">Navigate</div>', unsafe_allow_html=True)
        for page, label, key in links:
            st.page_link(page, label=label, disabled=active == key, use_container_width=True)
        st.markdown('<div class="fx-side-label">System</div><div class="fx-side-system"><div><i class="amber"></i><strong>Research mode</strong></div><span>Clinical release not established</span></div>', unsafe_allow_html=True)


def _base(active: str) -> None:
    inject_xai_theme()
    _nav(active)
    st.markdown(
        """
<style>
.ref-hero{padding:20px 0 24px;max-width:930px}.ref-hero h1{font-size:46px;line-height:1.04;margin:7px 0 10px}.ref-hero p{font-size:15px;line-height:1.65;color:var(--body);max-width:850px}.ref-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:12px 0 20px}.ref-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:15px}.ref-card h3{font-size:18px;margin:0 0 6px}.ref-card p{font-size:12.5px;line-height:1.55;margin:0;color:var(--body)}.ref-kpi{font-family:var(--serif);font-size:30px;color:var(--ink);font-weight:500}.ref-kpi-label{font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-top:5px}.ref-section{font-family:var(--serif);font-size:28px;color:var(--ink);font-weight:500;margin:30px 0 6px}.ref-sub{font-size:13px;color:var(--muted);line-height:1.55;max-width:880px;margin-bottom:12px}.ref-row{display:grid;grid-template-columns:1.25fr 1fr 2.4fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line2);font-size:12px}.ref-row strong{color:var(--ink)}.ref-row span{color:var(--body)}.ref-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:14px 0}.ref-node{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:13px}.ref-node b{display:block;color:var(--ink);font-size:13px}.ref-node small{display:block;color:var(--muted);font-size:10.5px;line-height:1.45;margin-top:5px}.ref-warning{background:rgba(224,176,98,.08);border:1px solid rgba(224,176,98,.3);border-radius:var(--r);padding:14px 15px;color:var(--body);font-size:12.5px;line-height:1.55}.ref-ok{background:rgba(108,194,160,.08);border:1px solid rgba(108,194,160,.28);border-radius:var(--r);padding:14px 15px;color:var(--body);font-size:12.5px;line-height:1.55}@media(max-width:900px){.ref-grid{grid-template-columns:1fr}.ref-flow{grid-template-columns:1fr}.ref-row{grid-template-columns:1fr}}
</style>
""",
        unsafe_allow_html=True,
    )


def _footer() -> None:
    st.markdown('<div class="fx-footer"><div>Research decision support · source-traced and auditable</div><div>Software qualification does not equal clinical validation</div></div>', unsafe_allow_html=True)


def render_validation() -> None:
    _base("validation")
    q = COMMON_CORE_QUALIFICATION
    st.markdown('<div class="ref-hero"><div class="fx-kicker">Validation, qualification, and trust boundary</div><h1>What has been tested, what has not, and what the system is allowed to claim.</h1><p>This page is intentionally layered for clinicians, governance reviewers, and research/publication reviewers. Software qualification, disease-specific validation, prospective silent validation, and clinical release are separate states.</p></div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("Common-core result", str(q.get("result", "unknown")).upper())
    b.metric("Matrix executions", q.get("matrix_executions", 0))
    c.metric("Dedicated tests", q.get("dedicated_pan_oncology_tests_passed", 0))
    d.metric("Full regression tests", q.get("full_regression_tests_passed", 0))
    st.caption(f"Qualified build: {q.get('qualified_build', 'not represented')} · CI run: {q.get('workflow_run_id', 'not represented')} · date: {q.get('qualification_date', 'not represented')}")

    st.markdown('<div class="ref-section">The validation ladder</div><div class="ref-sub">A higher rung requires evidence that the lower rung cannot substitute for.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-flow">'
        '<div class="ref-node"><b>1. Architecture ready</b><small>Registered routing, schemas, deterministic gates, and fail-closed behavior exist.</small></div>'
        '<div class="ref-node"><b>2. Common-core qualified</b><small>Synthetic software qualification of shared behavior across registered programs.</small></div>'
        '<div class="ref-node"><b>3. Disease-specific qualified</b><small>Disease-specific rules and evidence packages tested against predefined software criteria.</small></div>'
        '<div class="ref-node"><b>4. Clinical validation</b><small>Independent clinical reference-standard evaluation, preferably silent/prospective.</small></div>'
        '<div class="ref-node"><b>5. Clinical release</b><small>Governance, monitoring, accountability, and institution-specific authorization.</small></div>'
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Current program status</div><div class="ref-sub">All registered oncology programs share the qualified common architecture. That does not establish disease-specific treatment correctness.</div>', unsafe_allow_html=True)
    rows = []
    for program in PROGRAMS:
        status = get_pathway_validation_status(program.program_id)
        rows.append({
            "Program": program.display_name,
            "State": status.label,
            "Common-core qualified": status.common_core_qualified,
            "Disease-specific software qualified": status.disease_specific_software_qualified,
            "Clinically validated": status.clinically_validated,
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown('<div class="ref-section">What the common-core qualification actually tested</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid">'
        '<div class="ref-card"><h3>Routing and program assignment</h3><p>Fourteen registered programs, ordinary routing, safety retention, safety-only routing, molecular and trial question routing, pediatric tie-breaking, and deterministic reassignment of incorrect program metadata.</p></div>'
        '<div class="ref-card"><h3>Integrity and missingness</h3><p>Pending diagnosis, high-severity conflicts, missing or conflicting decision-critical information, explicit stage handling, and prevention of specialist routing when blocking information is unresolved.</p></div>'
        '<div class="ref-card"><h3>Fail-closed evidence behavior</h3><p>Empty evidence channels cannot create guideline, molecular-actionability, translational-actionability, literature, trial-match, or safety claims.</p></div>'
        '</div>', unsafe_allow_html=True)
    st.info("A stage-matching defect discovered during qualification allowed Stage II to match Stage III under generic token matching. The matcher was corrected to exact canonical stage comparison, then the complete qualification gate was rerun successfully on the recorded build.")

    st.markdown('<div class="ref-section">Guardrail coverage in the production workflow</div><div class="ref-sub">These controls are enforced in code and are surfaced in the Agentic Workspace right-side inspector.</div>', unsafe_allow_html=True)
    guards = [
        ("Semantic integrity", "Pre-routing", "Blocks model/schema contradictions before downstream reasoning."),
        ("Case integrity", "Pre-routing", "Checks provenance, unresolved conflicts, and unsafe case representation."),
        ("Missing information", "Pre-routing", "Blocking gaps prevent specialist routing; nonblocking gaps remain visible."),
        ("Explicit stage prerequisite", "Guideline", "Stage-dependent guidance requires verified provenance plus clinician confirmation and exact stage match."),
        ("Guideline evidence boundary", "Guideline", "Only current, verified, authorized guidance can support formal guideline claims."),
        ("Molecular evidence boundary", "Molecular", "Gene identity or model memory cannot create actionability; records require source and human verification."),
        ("Safety evidence boundary", "Safety", "Warnings/contraindications require verified attested evidence; nonmatch is never treated as proof of safety."),
        ("Literature claim boundary", "Literature", "PubMed retrieval surfaces candidate literature but does not itself verify a clinical claim."),
        ("Trial eligibility boundary", "Trials", "A registry match is explicitly not patient eligibility."),
        ("Translational boundary", "Translational", "Mechanistic evidence cannot establish treatment efficacy or patient-level actionability."),
        ("Clinical red team", "Post-synthesis", "Searches for unsupported leaps, blocked claims, conflicts, and recommendation-changing weaknesses."),
        ("Consensus gate", "Post-red-team", "Only adjudicated, supportable outputs can reach the final brief."),
        ("Brief claim preservation", "Presentation", "The brief is a structured presentation transform and cannot create new clinical claims."),
        ("Governed follow-up chat", "Presentation", "Follow-up answers are restricted to the represented case and governed outputs; unsupported questions abstain."),
    ]
    for name, layer, purpose in guards:
        st.markdown(f'<div class="ref-row"><strong>{escape(name)}</strong><span>{escape(layer)}</span><span>{escape(purpose)}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">What this qualification does not establish</div>', unsafe_allow_html=True)
    st.markdown('<div class="ref-warning"><b>Not established:</b> disease-specific treatment correctness, completeness of biomarker rules, correctness of every staging system, patient-specific drug appropriateness, clinical-trial eligibility, patient outcomes, unrestricted real-world safety, clinical validation, regulatory authorization, or institutional approval for routine patient-care use.</div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Evidence available to reviewers</div>', unsafe_allow_html=True)
    st.markdown('<div class="ref-ok"><b>Auditable software evidence:</b> frozen qualification build, CI workflow run, common-core matrix, dedicated test count, full regression count, challenge/remediation protocols in the source project, pathway validation state, source-traced workflow audit events, and fail-closed runtime status.</div>', unsafe_allow_html=True)
    _footer()


def render_about() -> None:
    _base("about")
    st.markdown('<div class="ref-hero"><div class="fx-kicker">Scientific scope and governance</div><h1>A tumor-board instrument, not a general oncology chatbot.</h1><p>The system is designed to improve how a multidisciplinary team represents a case, commissions evidence, exposes uncertainty, challenges its own synthesis, and records an auditable decision-support brief. It does not replace multidisciplinary clinical judgment.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Four information classes remain visually and logically distinct</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-grid">'
        '<div class="ref-card"><h3>Source fact</h3><p>A patient/case assertion with represented provenance. Human confirmation is recorded separately from extraction.</p></div>'
        '<div class="ref-card"><h3>Retrieved evidence</h3><p>Guideline, PubMed, CIViC, FDA label, ClinicalTrials.gov, or translational evidence brought into a bounded specialist channel.</p></div>'
        '<div class="ref-card"><h3>Derived interpretation</h3><p>Deterministic or agent-generated synthesis whose support and limitations remain linked to its source channels.</p></div>'
        '<div class="ref-card"><h3>Human judgment</h3><p>Clinician confirmation, evidence attestation, conflict resolution, or tumor-board adjudication. It is never silently inferred from a model response.</p></div>'
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Evidence model</div>', unsafe_allow_html=True)
    evidence = [
        ("Guidance", "Current verified sources; exact stage and molecular prerequisites where required."),
        ("Molecular", "CIViC candidate retrieval plus explicit human attestation before patient-level use."),
        ("Safety", "FDA label candidate retrieval plus human attestation; label text remains distinct from patient-specific contraindication or dose."),
        ("Literature", "Bounded PubMed retrieval; article retrieval is not equivalent to critical appraisal or treatment recommendation."),
        ("Clinical trials", "ClinicalTrials.gov current match retrieval; match is not eligibility and does not recommend enrollment."),
        ("Translational", "Mechanistic/preclinical/human-translational evidence remains separate from clinical actionability."),
    ]
    for name, purpose in evidence:
        st.markdown(f'<div class="ref-row"><strong>{escape(name)}</strong><span>Bounded channel</span><span>{escape(purpose)}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Human control points</div>', unsafe_allow_html=True)
    st.markdown('<div class="ref-grid"><div class="ref-card"><h3>Case review</h3><p>Confirm that the structured representation matches the source. Unsupported facts do not become verified merely because a clinician clicks continue.</p></div><div class="ref-card"><h3>Evidence attestation</h3><p>Review candidate molecular and safety evidence before it is admitted to patient-level reasoning.</p></div><div class="ref-card"><h3>Decision adjudication</h3><p>The system produces decision support, alternatives, conditions, uncertainty, and abstention. Final patient-care decisions remain with qualified clinicians and local governance.</p></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Privacy and deployment boundary</div>', unsafe_allow_html=True)
    st.markdown('<div class="ref-warning">The public research deployment is intended for synthetic or appropriately de-identified data. Secrets are supplied through deployment secret management rather than committed files. Clinical deployment would require institution-specific privacy, security, validation, monitoring, accountability, and release controls.</div>', unsafe_allow_html=True)
    _footer()


def render_architecture() -> None:
    _base("architecture")
    st.markdown('<div class="ref-hero"><div class="fx-kicker">System architecture</div><h1>The conversation is the surface. The governed pipeline is the system.</h1><p>The Agentic Workspace does not replace the original engine. It presents the same underlying case, evidence, safety, challenge, consensus, and audit logic as a cleaner stage-by-stage conversation.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">End-to-end execution path</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ref-flow">'
        '<div class="ref-node"><b>1. Intake</b><small>load synthetic, parse text/upload, extraction v2.5, source provenance.</small></div>'
        '<div class="ref-node"><b>2. Human review</b><small>confirm the structured representation; preserve unsupported gaps.</small></div>'
        '<div class="ref-node"><b>3. Evidence</b><small>guideline + molecular + literature + trials + safety + translational channels.</small></div>'
        '<div class="ref-node"><b>4. Guarded analysis</b><small>semantic integrity, case integrity, missingness, routing, synthesis, red team, consensus.</small></div>'
        '<div class="ref-node"><b>5. Brief</b><small>final decision state, alternatives, uncertainty, source traces, audit trail, governed follow-up.</small></div>'
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Backend contract</div><div class="ref-sub">The conversational UI calls existing functions rather than maintaining a second clinical engine.</div>', unsafe_allow_html=True)
    code = '''# intake / extraction
load_synthetic()
parse_text(...) / parse_upload(...)
extract_case_v25(...)

# bounded evidence
GuidelineAgent(...).run(case)
collect_case_candidates(...)
build_approved_molecular_store(...)
build_approved_safety_store(...)
configure_workflow_runtime(...)

# guarded end-to-end analysis
run_workflow(case, raw_extraction=...)
'''
    st.code(code, language="python")

    st.markdown('<div class="ref-section">What run_workflow returns</div>', unsafe_allow_html=True)
    outputs = [
        ("case", "Canonical source-traced case representation"),
        ("routing", "Selected specialist agents and routing rationale"),
        ("specialist_outputs", "Guideline, molecular, translational, literature, trials, safety"),
        ("preliminary_synthesis", "Bounded preliminary synthesis"),
        ("red_team_findings / report", "Independent challenge layer"),
        ("consensus_report", "Adjudicated decision state"),
        ("tumor_board_brief", "Structured auditable presentation artifact"),
        ("semantic_integrity_findings", "Schema/meaning contradictions"),
        ("case_integrity_report", "Provenance/conflict safety gate"),
        ("missing_information_report", "Blocking and nonblocking information gaps"),
        ("final_decision", "Primary strategy, alternatives, conditions, uncertainties"),
        ("audit_events", "Workflow provenance and traceability"),
    ]
    for key, purpose in outputs:
        st.markdown(f'<div class="ref-row"><strong>{escape(key)}</strong><span>Workflow output</span><span>{escape(purpose)}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="ref-section">Why the right-side inspector exists</div>', unsafe_allow_html=True)
    st.markdown('<div class="ref-ok">The center stream stays clinically readable. The inspector exposes the hidden work without turning the conversation into a technical dump: pathway validation state, source tracing, evidence runtime readiness, case/missing-information gates, routed agents, red-team state, consensus state, and audit events.</div>', unsafe_allow_html=True)
    _footer()
