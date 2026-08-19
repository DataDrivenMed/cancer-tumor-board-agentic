# Comprehensive Agentic Rebuild

This branch turns the Agentic Workspace into the primary presentation layer over the governed Tumor Board Intelligence engine.

## Product architecture

- One primary conversational workspace
- Left staged workup rail
- Center clinician conversation and progressive disclosure
- Right live workup inspector exposing provenance, evidence admission, runtime channel state, integrity gates, missing information, routing, red-team state, consensus, brief release state, and audit events
- Former Clinical Workspace route retained only as a compatibility route into the same Agentic Workspace

## Governed workflow preserved

The conversational experience calls the original workflow rather than recreating a parallel recommendation engine. The production path includes semantic-integrity checks, quality checks, Case Integrity / Data QA, Missing Information, question-aware routing, bounded specialist agents, synthesis, Clinical Red Team, consensus adjudication, structured abstention, tumor-board brief, and audit events.

## Evidence boundaries

- Guidance: verified/current source matching with exact stage and molecular prerequisites where applicable
- Molecular: CIViC candidate retrieval plus explicit human attestation before patient-level actionability analysis
- Safety: FDA label candidate retrieval plus exact-span human attestation before patient-level safety reasoning
- Literature: bounded PubMed retrieval that does not itself verify a clinical claim
- Trials: bounded ClinicalTrials.gov matching with explicit separation of trial match from trial eligibility
- Translational: mechanistic evidence kept separate from clinical actionability

## Decision output

The final brief preserves primary strategy, reasonable alternatives, conditions and prerequisites, major uncertainties, tumor-board priorities, trial opportunities, safety findings, unresolved information, provenance, source traces, audit history, decision-support strength, abstention, PDF export, and governed follow-up chat.

## Validation and qualification

The product now surfaces the baseline extraction suite, challenge validation v2, remediation validation v2.5, frozen pan-oncology common-core qualification record, acceptance criteria, known limitations, live guardrail coverage, and explicit non-claims.

The frozen common-core record reports PASS on the recorded 2026-08-16 build with 210 matrix executions, 261 dedicated pan-oncology tests, and 555 full-regression tests. That software qualification is not presented as disease-specific clinical validation or clinical release.

## Release boundary

This branch remains research decision support. It does not claim disease-specific treatment correctness, patient-specific appropriateness, clinical-trial eligibility, clinical outcome benefit, clinical validation, regulatory authorization, or institutional approval for routine patient-care use.

## Review before merge

The branch should be previewed in Streamlit Cloud with:

- Branch: `agentic-comprehensive-rebuild`
- Main file: `app/main.py`

Use the synthetic qualification case first and walk through Intake, Case Review, Evidence, Analysis, and Decision Brief. Review the right-side inspector, Validation page, Architecture page, governed chat, and PDF export before merging to `main`.
