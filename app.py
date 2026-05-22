import streamlit as st
import anthropic
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health Claim Checker",
    page_icon="🔬",
    layout="centered",
)

st.title("🔬 Health Claim Checker")
st.caption("Paste any viral health claim or article URL. Get an evidence-based credibility score.")

# ── API key ───────────────────────────────────────────────────────────────────
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com",
    )
    if not api_key:
        st.info("Enter your Anthropic API key to get started.")
        st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ── Input ─────────────────────────────────────────────────────────────────────
claim = st.text_area(
    "Health claim or article URL",
    placeholder='e.g. "Cold showers boost testosterone by 200%" or paste a URL',
    height=100,
)

# Per-session usage cap. Each analysis can fire up to 5 web_search
# calls + 1 model call, so unconstrained use on a public deploy could
# add up fast. 20 claims/session is generous for honest use without
# letting a single browser tab drain the budget.
MAX_CLAIMS_PER_SESSION = 20
claims_used = len(st.session_state.get("history", []))
budget_left = MAX_CLAIMS_PER_SESSION - claims_used
st.caption(f"Session budget: {budget_left}/{MAX_CLAIMS_PER_SESSION} claims remaining")

analyze = st.button(
    "Analyze Claim",
    type="primary",
    disabled=not claim.strip() or budget_left <= 0,
)
if budget_left <= 0:
    st.warning(
        f"Session cap of {MAX_CLAIMS_PER_SESSION} claims reached. "
        "Refresh the page to start a new session."
    )

# ── Analysis ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a rigorous evidence-based health scientist with expertise in
epidemiology, statistics, and causal inference. Your job is to evaluate viral health claims
using the same standards you would apply to academic peer review.

You must be honest, precise, and calibrated — neither dismissive nor credulous.
Always distinguish between statistical significance and practical significance."""

ANALYSIS_PROMPT = """Evaluate this health claim: {claim}

Search for the original source/study if needed. Then analyze it across these 6 dimensions:

1. SOURCE QUALITY — Is this peer-reviewed? What journal tier? Preprint? Blog? Press release?
2. STUDY DESIGN — RCT, observational, animal study, n-of-1, meta-analysis? Rate the design quality.
3. SAMPLE SIZE — Was it adequately powered to detect the claimed effect size?
4. EFFECT SIZE — Is the effect statistically AND practically significant? Report actual numbers.
5. REPLICATION — Is this consistent with the broader literature or an outlier?
6. MEDIA DISTORTION — Does the headline/claim accurately represent what the study actually found?

Output format (strictly follow this):

## Credibility Score: [X/100]
**[One-line verdict: Likely True / Partially True / Misleading / Likely False / Unverified]**

---

### 1. Source Quality
[2-3 sentences]

### 2. Study Design
[2-3 sentences]

### 3. Sample Size
[2-3 sentences]

### 4. Effect Size
[2-3 sentences with actual numbers if available]

### 5. Replication
[2-3 sentences]

### 6. Media Distortion
[2-3 sentences comparing claim to actual evidence]

---

### Bottom Line
[2-3 sentences plain-English verdict for a general audience]

### Confidence in This Assessment
[Low / Medium / High] — [one sentence explaining why]
"""

if analyze and claim.strip():
    with st.spinner("Analyzing claim... searching literature..."):
        try:
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=2000,
                thinking={"type": "adaptive"},
                # System prompt is static across all queries — cache it so
                # subsequent claims in the same session hit the prompt
                # cache (5-min TTL). Cuts input cost on the system block
                # by ~90%.
                system=[{
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }],
                # Server-side web search lets the model actually verify
                # claims against primary sources (the prompt explicitly
                # tells it to "search for the original source/study if
                # needed" — before this tool was wired up that instruction
                # was dead weight).
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5,
                }],
                messages=[
                    {"role": "user", "content": ANALYSIS_PROMPT.format(claim=claim.strip())}
                ],
            )

            # Extract final text — skip thinking, tool_use, web_search_tool_result
            # blocks. Take the LAST text block (post-search reasoning) so the
            # answer reflects what the model said after consulting sources.
            result_text = ""
            for block in response.content:
                if block.type == "text":
                    result_text = block.text

            st.markdown("---")
            st.markdown(result_text)

            # Save to history
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "claim": claim.strip(),
                "result": result_text,
            })

        except anthropic.AuthenticationError:
            st.error("Invalid API key. Check your key at console.anthropic.com.")
        except anthropic.RateLimitError:
            st.error("Rate limit hit. Wait a moment and try again.")
        except Exception as e:
            st.error(f"Error: {e}")

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.get("history"):
    with st.expander(f"📋 Session history ({len(st.session_state.history)} claims)"):
        for i, item in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"**{i}. {item['claim'][:80]}{'...' if len(item['claim']) > 80 else ''}**")
            st.markdown(item["result"][:300] + "...")
            st.divider()
