#!/bin/bash
# Run the Health Claim Checker app.
# First run creates .venv and installs deps; subsequent runs reuse them.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "[setup] Creating .venv (first run only)..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    echo "[setup] Done. Starting app..."
else
    source .venv/bin/activate
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "[hint] ANTHROPIC_API_KEY not set in env — you can also paste it in the UI."
fi

exec streamlit run app.py
