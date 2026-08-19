# Validation framework

This agentic presentation preserves the governed qualification structure from the source Tumor Board Intelligence repository.

## Frozen common-core qualification

The source repository records a PASS for the pan-oncology common core on 2026-08-16: 14 registered tumor-board programs, 15 scenarios per program, 210 matrix executions, 261 dedicated pan-oncology tests, and 555 full-regression tests. The recorded qualification build is `b62217a3bc65321193195d782a593e093139d406` and the recorded GitHub Actions run is `31964312857`.

This establishes software qualification of the shared architecture only. It does not establish disease-specific treatment correctness, trial eligibility, patient-specific appropriateness, clinical outcome benefit, regulatory authorization, clinical validation, or institutional approval for routine patient care.

## Baseline extraction qualification

The baseline suite contains Q01 through Q10 and tests straightforward extraction, missing-information detection, contradiction preservation, pending-result non-inference, treatment chronology, molecular over-interpretation, stage conflict, longitudinal treatment and transplant extraction, historical distractor contamination, and intentional abstention for an insufficient case.

## Challenge validation v2

The v2 challenge protocol contains 10 targeted cases and 10 unseen cases. Six frozen cases are repeated three times to test stochastic stability. Failure modes include treatment-history omission, current-versus-historical diagnosis contamination, planned-versus-administered therapy, medication temporality, chronology, stage-conflict preservation, pending molecular non-inference, sparse-case missingness, and safe abstention for unknown primary.

Acceptance policy:
- Green: 100% strict pass across a stream, 100% exact provenance, zero prohibited assertions, zero unsupported provenance assertions.
- Amber: at least 95% strict pass, exact provenance remains 100%, zero prohibited or unsupported assertions, and no repeated-subset case fails more than once.
- Red: below 95%, any provenance failure, any prohibited or unsupported assertion, or recurrent failure of the same repeated-subset case.

The protocol and challenge cases are retained in this repository. The product UI does not present a challenge-stream execution as passed unless a frozen executed study result is available.

## Remediation validation v2.5

The v2.5 remediation suite contains 12 frozen cases, Y01 through Y12. Six cases are repeated three times, for 30 planned executions. It targets uncertainty preservation, diagnostic and molecular missingness ontology, planned-treatment separation, treatment chronology, duplicate-prone treatment completeness, historical malignancy contamination, stage-conflict separation, metastatic-state canonicalization, and safe sparse-case behavior.

Green requires 30/30 strict passes, 100% exact provenance, zero prohibited assertions, zero unsupported provenance assertions, zero semantic-integrity errors, no duplicate treatment episodes, consistent missing-information ontology, and every repeated case passing 3/3.

## Release boundary

Software qualification, disease-specific validation, prospective clinical validation, and governed clinical release are separate states. The current product remains research decision support. Clinical release is not established.
