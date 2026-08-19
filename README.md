# Cancer Tumor Board Intelligence - Agentic Workspace

Agentic interface for the cancer tumor board intelligence system.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` using `.env.example` as the template.

3. Run the app:

```bash
streamlit run app/main.py
```

## Deployment

Target Streamlit Cloud application:

https://cancer-tumor-board-agentic.streamlit.app/

## Structure

- `app/` - Streamlit frontend, pages, UI, and styling
- `agents/` - Clinical agent implementations
- `services/` - Business logic and integrations
- `schemas/` - Data models and contracts
- `orchestration/` - Workflow state machine
- `synthetic_cases/` - Demo case data

## Environment Variables

See `.env.example` for required environment variables.

## Production Notes

- Add secrets through Streamlit Cloud secrets management.
- Never commit `.env` files containing real credentials.
- `.streamlit/secrets.toml` is intentionally excluded from migration.
- The original repository is not modified by this migration script.
