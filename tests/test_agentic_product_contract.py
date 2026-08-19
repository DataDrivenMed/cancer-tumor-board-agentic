from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AGENTIC_FILES = (
    ROOT / "app" / "main.py",
    ROOT / "app" / "agentic_home.py",
    ROOT / "app" / "agentic_core.py",
    ROOT / "app" / "agentic_layout.py",
    ROOT / "app" / "agentic_stages_case.py",
    ROOT / "app" / "agentic_stages_output.py",
    ROOT / "app" / "reference_pages.py",
)

REQUIRED_RUNTIME_FILES = (
    ROOT / "orchestration" / "workflow.py",
    ROOT / "services" / "evidence_commissioning.py",
    ROOT / "services" / "runtime_agents.py",
    ROOT / "services" / "governed_chat.py",
    ROOT / "services" / "tumor_board_pdf.py",
    ROOT / "agents" / "clinical_red_team.py",
    ROOT / "agents" / "consensus.py",
    ROOT / "agents" / "case_integrity.py",
    ROOT / "agents" / "missing_information.py",
    ROOT / "qualification" / "challenge_cases_v2.py",
    ROOT / "qualification" / "challenge_protocol_v2.py",
    ROOT / "qualification" / "remediation_cases_v25.py",
    ROOT / "qualification" / "remediation_protocol_v25.py",
)


def test_agentic_python_sources_compile() -> None:
    for path in AGENTIC_FILES:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")


def test_required_governed_runtime_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_RUNTIME_FILES if not path.exists()]
    assert not missing, f"Missing governed runtime files: {missing}"


def test_streamlit_entry_point_is_stable_renderer() -> None:
    source = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "render_agentic_home()" in source
    assert "st.switch_page" not in source


def test_agentic_ui_has_no_invalid_app_prefixed_page_links() -> None:
    for path in AGENTIC_FILES:
        source = path.read_text(encoding="utf-8")
        assert '"app/pages/' not in source
        assert "'app/pages/" not in source


def test_no_competing_classic_workspace_navigation() -> None:
    source = (ROOT / "app" / "reference_pages.py").read_text(encoding="utf-8")
    assert "Classic Workspace" not in source


def test_legacy_workspace_route_is_only_a_compatibility_surface() -> None:
    source = (ROOT / "app" / "pages" / "00_Clinical_Workspace.py").read_text(encoding="utf-8")
    assert "render_agentic_home()" in source
    assert "run_workflow(" not in source
