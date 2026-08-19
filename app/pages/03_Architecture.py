from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.reference_pages import render_architecture

st.set_page_config(
    page_title="Architecture · Tumor Board Intelligence",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_architecture()
