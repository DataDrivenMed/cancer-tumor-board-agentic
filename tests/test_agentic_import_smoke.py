def test_agentic_import_graph_resolves():
    """The deployed agentic entry point must have a closed local import graph."""
    import app.agentic_home  # noqa: F401
    import app.agentic_core  # noqa: F401
    import app.agentic_layout  # noqa: F401
    import app.agentic_stages_case  # noqa: F401
    import app.agentic_stages_output  # noqa: F401
    import app.chat_ui  # noqa: F401
    import services.explicit_stage_extraction  # noqa: F401
    import services.evidence_commissioning  # noqa: F401
    import services.runtime_agents  # noqa: F401
    import services.governed_chat  # noqa: F401
    import services.tumor_board_pdf  # noqa: F401
    import orchestration.workflow  # noqa: F401


def test_synthetic_case_can_be_loaded():
    from app.agentic_core import load_synthetic

    case = load_synthetic()
    assert case.case_id
    assert case.diagnosis is not None
