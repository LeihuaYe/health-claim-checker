#!/bin/bash
# Run the Health Claim Checker app
cd "$(dirname "$0")"
source .venv/bin/activate
streamlit run app.py
