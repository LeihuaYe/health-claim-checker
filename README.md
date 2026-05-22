# 🔬 Health Claim Checker

A Streamlit web app that evaluates viral health claims against the
evidence — peer-reviewed source quality, study design, statistical
power, replication, and media distortion — and returns a 0–100
credibility score with reasoning.

Powered by Claude Opus 4.7 with extended thinking and server-side web
search, so the model actually fetches and reads primary sources rather
than relying solely on its training data.

## What it does

Paste a viral health claim ("Cold showers boost testosterone by 200%")
or an article URL. The app:

1. Searches the web for the primary source / study being referenced
2. Evaluates the claim across **6 dimensions**:
   - Source quality (peer-reviewed? what tier?)
   - Study design (RCT? observational? n-of-1?)
   - Sample size (adequately powered?)
   - Effect size (statistically AND practically significant?)
   - Replication (consistent with broader literature?)
   - Media distortion (headline match the actual finding?)
3. Returns a credibility score, plain-English bottom line, and a
   confidence rating on its own assessment

## Run locally

```bash
git clone https://github.com/LeihuaYe/health-claim-checker.git
cd health-claim-checker
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
./run.sh    # or: streamlit run app.py
```

Opens at `http://localhost:10000`.

You can also paste your API key directly in the UI if you don't want to
set the env var.

## Deploy to Render

1. Fork this repo
2. Create a new Web Service on [render.com](https://render.com),
   connecting your fork
3. Render auto-detects `render.yaml` — accept defaults
4. In the service's **Environment** tab, add:
   - Key: `ANTHROPIC_API_KEY`
   - Value: your Anthropic API key (get one at
     [console.anthropic.com](https://console.anthropic.com))
5. Deploy

Free tier works for low-volume personal use. Each claim analysis uses
~1 model call + up to 5 web searches.

## Cost / usage caps

The app enforces a 20-claim-per-session cap to protect against runaway
spend on a public deploy. Each claim ≈ a few cents on Opus 4.7 plus
web search fees. Refresh the page to start a new session.

## How it works under the hood

- **Model:** `claude-opus-4-7` with adaptive extended thinking — the
  model decides how much reasoning to do per claim
- **Tool:** Server-side `web_search` (max 5 uses per claim) so the
  model can fetch primary sources rather than guessing from training
  data
- **Prompt caching:** The static system prompt is cached with 5-min
  TTL — repeat analyses in the same session pay ~90% less on system
  tokens
- **Output extraction:** Takes the *last* text block in the response
  (post-search reasoning) so the verdict reflects what the model
  concluded after consulting sources

Single-file app — all logic in `app.py` (~150 lines).

## Limitations

- The model can be wrong. The score is one expert opinion (statistically
  weighted across training + retrieved sources), not ground truth.
- Web search results depend on what's indexed. Recent claims or
  paywalled studies may not surface.
- Adaptive thinking + 5 web searches per claim takes 10-30 seconds.
  Patience.
- This is **not medical advice**. Use it to evaluate health *claims*,
  not to make personal health decisions.

## License

MIT — use it, fork it, learn from it.
