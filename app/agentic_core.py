from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

from agents.extraction_v25 import extract_case_v25
from schemas.case import CancerTumorBoardCase
from services.document_parser import parse_text, parse_upload
from services.evidence_commissioning import (
    build_approved_molecular_store,
    build_approved_safety_store,
    collect_case_candidates,
)
from services.eln_aml_guidance import public_eln_aml_store
from services.runtime_agents import configure_workflow_runtime
from orchestration.workflow import run_workflow

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGES = ("intake", "review", "evidence", "analysis", "brief")
STAGE_LABELS = {
    "intake": "Case intake",
    "review": "Case review",
    "evidence": "Evidence",
    "analysis": "Analysis",
    "brief": "Decision brief",
}


def val(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def txt(value: Any, default: str = "Not represented") -> str:
    if value is None:
        return default
    if hasattr(value, "value"):
        value = value.value
    text = str(value).strip()
    return text or default


def human(value: Any) -> str:
    return txt(value).replace("_", " ").strip().title()


def secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value).strip()
    except Exception:
        pass
    value = os.getenv(name, "").strip()
    return value or None


def source_ok(item: Any) -> bool:
    return any(bool(val(p, "source_verified", False)) for p in (val(item, "provenance", []) or []))


def source_refs(item: Any) -> list[str]:
    refs: list[str] = []
    for p in (val(item, "provenance", []) or []):
        document_id = val(p, "document_id")
        if document_id:
            refs.append(str(document_id))
        refs.extend(str(x) for x in (val(p, "source_segment_ids", []) or []) if x)
    return list(dict.fromkeys(refs))


def confirm_case_representation(case: CancerTumorBoardCase) -> CancerTumorBoardCase:
    """Record clinician confirmation only for facts already carrying verified provenance."""
    confirmed = case.model_copy(deep=True)
    facts = [confirmed.diagnosis, confirmed.disease_state, confirmed.stage, confirmed.performance_status]
    facts += list(confirmed.pathology) + list(confirmed.imaging) + list(confirmed.labs)
    facts += list(confirmed.comorbidities) + list(confirmed.toxicities)
    facts += list(confirmed.transplant_cellular_therapy) + list(confirmed.current_medications)
    for item in [x for x in facts if x is not None]:
        if source_ok(item):
            item.human_verified = True
    for item in confirmed.molecular_findings:
        if source_ok(item):
            item.human_verified = True
    for item in confirmed.treatments:
        if source_ok(item):
            item.human_verified = True
    return confirmed


def load_synthetic() -> CancerTumorBoardCase:
    payload = json.loads((PROJECT_ROOT / "synthetic_cases" / "syn_aml_001.json").read_text(encoding="utf-8"))
    return CancerTumorBoardCase.model_validate(payload)


def initialize_state() -> None:
    defaults = {
        "ag_stage": "intake",
        "ag_case": None,
        "ag_raw_extraction": None,
        "ag_extraction_package": None,
        "ag_review_confirmed": False,
        "ag_guideline_store": None,
        "ag_guideline_report": None,
        "ag_evidence_candidates": None,
        "ag_evidence_error": None,
        "ag_molecular_store": None,
        "ag_safety_store": None,
        "ag_runtime_status": None,
        "ag_result": None,
        "ag_evidence_confirmed": False,
        "ag_evidence_summary": {
            "molecular_candidates": 0,
            "molecular_attested": 0,
            "safety_candidates": 0,
            "safety_attested": 0,
        },
        "ag_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_workup() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("ag_"):
            del st.session_state[key]
    st.rerun()


def goto(stage: str) -> None:
    if stage not in STAGES:
        raise ValueError(stage)
    st.session_state.ag_stage = stage
    st.rerun()


def extract_text_case(narrative: str, case_id: str = "AGENTIC-EXTRACTED-001"):
    token = secret("MODEL_AUTH_TOKEN") or secret("HF_TOKEN")
    if not token:
        raise RuntimeError("MODEL_AUTH_TOKEN or HF_TOKEN is required for model-based extraction.")
    document = parse_text(narrative)
    return extract_case_v25(
        document=document,
        api_key=token,
        model=secret("EXTRACTION_MODEL") or "openai/gpt-oss-120b:fireworks-ai",
        case_id=case_id,
    )


def extract_upload_case(upload, case_id: str = "AGENTIC-UPLOAD-001"):
    token = secret("MODEL_AUTH_TOKEN") or secret("HF_TOKEN")
    if not token:
        raise RuntimeError("MODEL_AUTH_TOKEN or HF_TOKEN is required for model-based extraction.")
    document = parse_upload(upload)
    return extract_case_v25(
        document=document,
        api_key=token,
        model=secret("EXTRACTION_MODEL") or "openai/gpt-oss-120b:fireworks-ai",
        case_id=case_id,
    )


def ensure_evidence_candidates() -> None:
    if st.session_state.ag_evidence_candidates is not None or st.session_state.ag_evidence_error:
        return
    case = st.session_state.ag_case
    guideline_store = st.session_state.ag_guideline_store or public_eln_aml_store()
    st.session_state.ag_guideline_store = guideline_store
    try:
        candidates = collect_case_candidates(
            case,
            guideline_store,
            civic_api_key=secret("CIVIC_API_KEY"),
            openfda_api_key=secret("OPENFDA_API_KEY"),
        )
        st.session_state.ag_evidence_candidates = candidates
        st.session_state.ag_evidence_summary = {
            "molecular_candidates": len(val(candidates, "molecular_records", []) or []),
            "molecular_attested": 0,
            "safety_candidates": len(val(candidates, "safety_records", []) or []),
            "safety_attested": 0,
        }
    except Exception as exc:
        st.session_state.ag_evidence_error = f"{type(exc).__name__}: {exc}"


def commission_evidence(molecular_records, molecular_ids: set[str], safety_records, safety_indices: set[int]) -> None:
    st.session_state.ag_molecular_store = build_approved_molecular_store(molecular_records, molecular_ids)
    st.session_state.ag_safety_store = build_approved_safety_store(safety_records, safety_indices)
    st.session_state.ag_evidence_summary = {
        "molecular_candidates": len(molecular_records),
        "molecular_attested": len(molecular_ids),
        "safety_candidates": len(safety_records),
        "safety_attested": len(safety_indices),
    }
    st.session_state.ag_evidence_confirmed = True
    st.session_state.ag_result = None


def run_guarded_workflow() -> dict[str, Any]:
    if st.session_state.ag_result is not None:
        return st.session_state.ag_result
    guideline_store = st.session_state.ag_guideline_store or public_eln_aml_store()
    runtime = configure_workflow_runtime(
        guideline_store_override=guideline_store,
        molecular_store_override=st.session_state.ag_molecular_store,
        safety_store_override=st.session_state.ag_safety_store,
    )
    st.session_state.ag_runtime_status = runtime
    result = run_workflow(
        st.session_state.ag_case,
        raw_extraction=st.session_state.ag_raw_extraction,
    )
    st.session_state.ag_result = result
    return result
