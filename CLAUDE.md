# Health Claim Checker — Claude Code Context

## Project
Streamlit web app that uses the Claude API to analyze health claims across 6 dimensions:
source quality, study design, sample size, effect size, replication, and media distortion.
Returns a credibility score (0–100) and evidence-based verdict.

## Run
```bash
./run.sh
# or: streamlit run app.py
```
Runs on port 10000 (configured in `.streamlit/config.toml`).

## Architecture
- Single file: `app.py` — all logic, UI, and API calls
- Model: `claude-opus-4-7` with adaptive extended thinking
- Server-side web search tool (`web_search_20250305`, max 5 uses per claim)
  so the model can actually verify claims against primary sources
- Prompt caching on the static system block (5-min TTL) — repeat claims
  within a session hit ~90% input-cost discount on the system tokens
- SDK: `anthropic` (see `requirements.txt`)

## Deployment
- Git remote: `https://github.com/LeihuaYe/health-claim-checker.git`
- **Render** — `render.yaml` is committed at repo root.
  Connect repo on Render dashboard, set `ANTHROPIC_API_KEY` secret,
  deploy. Port pulled from Render's `$PORT` env var.
- Port 10000 in `.streamlit/config.toml` is the local-dev default;
  Render overrides via the start command in `render.yaml`.
