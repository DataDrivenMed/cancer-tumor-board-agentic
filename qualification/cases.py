from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoldCase:
    case_id: str
    title: str
    target_failure_mode: str
    narrative: str
    expected_diagnosis: str | None
    expected_disease_state: str | None
    expected_ecog: str | None
    expected_diagnosis_status: str | None = None
    expected_molecular_genes: tuple[str, ...] = ()
    expected_treatments: tuple[str, ...] = ()
    expected_missing_fields: tuple[str, ...] = ()
    expected_conflict_fields: tuple[str, ...] = ()
    prohibited_confirmed_values: tuple[str, ...] = ()
    require_no_molecular_findings: bool = False
    require_no_treatments: bool = False
    strict_core_gate: bool = False
    allow_null_diagnosis_if_uncertain: bool = False
    notes: str = ""


# The canonical baseline qualification set remains in the original repository.
# This dataclass is the contract consumed by the challenge/remediation suites.
CASES: tuple[GoldCase, ...] = ()


def get_case(case_id: str) -> GoldCase:
    for case in CASES:
        if case.case_id == case_id:
            return case
    raise KeyError(case_id)
