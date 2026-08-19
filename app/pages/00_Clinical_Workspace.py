from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agentic_home import render_agentic_home

st.set_page_config(
    page_title="Tumor Board Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Compatibility route only. The former separate Clinical Workspace has been
# absorbed into the governed conversational experience so there is one primary
# product surface and one underlying workflow.
render_agentic_home()
