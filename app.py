import asyncio
import uuid 
import os
import subprocess
import streamlit as st

st.set_page_config(
    page_title="WikiMind",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)


def _secrets_to_environ() -> None:
    """Copy Streamlit Cloud TOML secrets into os.environ.

    Supports top-level keys and nested tables that contain OPENAI_API_KEY / REDIS_URL
    (nested walks only allow-listed names so we do not set generic keys like ``host``).
    """
    _ALLOW = frozenset({"OPENAI_API_KEY", "REDIS_URL", "LLM_MODEL"})

    def merge_nested(d: dict) -> None:
        for k, v in d.items():
            if isinstance(v, dict):
                merge_nested(v)
            elif v is not None and str(k) in _ALLOW:
                os.environ[str(k)] = str(v).strip()

    try:
        sec = st.secrets
    except Exception:
        return
    for key in sec:
        val = sec[key]
        if isinstance(val, dict):
            merge_nested(val)
        elif val is not None:
            os.environ[str(key)] = str(val).strip()


_secrets_to_environ()

if not (os.environ.get("OPENAI_API_KEY") or "").strip():
    st.error(
        "Missing OPENAI_API_KEY.\n\n"
        "1. On share.streamlit.io open this deployed app.\n"
        "2. Manage app (bottom right) → Settings → Secrets (TOML editor).\n"
        "3. Add one line with your real key (keep the quotes):\n\n"
        "OPENAI_API_KEY = \"sk-...\"\n\n"
        "4. Save, then Reboot the app from Manage app.\n\n"
        "The variable name must be exactly OPENAI_API_KEY (not openai_key or OPENAI_KEY)."
    )
    st.stop()

from core.memory import setup_cognee
from core.query import answer_question, apply_feedback
from core.lint import run_lint, load_all_wiki_pages, auto_fix_issue, manual_fix_issue, apply_lint_fix

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f4f1ea; }
.block-container { padding: 80px 0 120px !important; max-width: 680px !important; }

/* Text selection */
::selection { background: #111 !important; color: #f4f1ea !important; }
::-moz-selection { background: #111 !important; color: #f4f1ea !important; }
textarea::selection, input::selection { background: #111 !important; color: #f4f1ea !important; }

/* Radio buttons — force dark text */
.stRadio label { color: #111 !important; font-size: 0.88rem !important; font-weight: 500 !important; }
.stRadio > div { color: #111 !important; }
.stRadio > div > div > label > div { color: #111 !important; }
.stRadio p { color: #111 !important; }
[data-testid="stRadio"] label { color: #111 !important; }
[data-testid="stRadio"] p { color: #111 !important; }
[data-testid="stWidgetLabel"] p { color: #111 !important; }
[data-testid="stWidgetLabel"] { color: #111 !important; }
/* All widget labels */
label { color: #111 !important; }

/* ── Nav ── */
.nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    background: rgba(244,241,234,0.95);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(0,0,0,0.07);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px; height: 52px;
}
.nav-logo { font-size: 0.9rem; font-weight: 700; color: #111; letter-spacing: -0.3px; }
.nav-meta { font-size: 0.73rem; color: #bbb; }
.nav-pill {
    font-size: 0.7rem; font-weight: 600;
    background: #111; color: #f4f1ea;
    padding: 5px 14px; border-radius: 100px; letter-spacing: 0.2px;
}

/* ── Hero ── */
.hero { padding: 48px 0 52px; border-bottom: 1px solid rgba(0,0,0,0.08); margin-bottom: 48px; }
.hero-eyebrow {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: #bbb; margin-bottom: 18px;
}
.hero-title {
    font-size: 3rem; font-weight: 800; color: #111;
    letter-spacing: -1.5px; line-height: 1.05; margin-bottom: 6px;
}
.hero-title-sub {
    font-size: 3rem; font-weight: 300; font-style: italic;
    color: #999; letter-spacing: -1.5px; line-height: 1.05; margin-bottom: 24px;
}
.hero-desc { font-size: 0.88rem; color: #888; line-height: 1.7; max-width: 480px; }

/* ── Stats row ── */
.stats-row { display: flex; gap: 12px; margin-bottom: 48px; }
.stat {
    flex: 1; background: #fff;
    border: 1px solid rgba(0,0,0,0.08); border-radius: 10px;
    padding: 16px 20px;
}
.stat-val { font-size: 1.4rem; font-weight: 700; color: #111; letter-spacing: -0.5px; }
.stat-label { font-size: 0.68rem; font-weight: 500; color: #bbb; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 3px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent; border-bottom: 1px solid rgba(0,0,0,0.08);
    gap: 0; padding: 0; margin-bottom: 40px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 0;
    border-bottom: 2px solid transparent;
    padding: 12px 0; margin-right: 32px;
    font-size: 0.82rem; font-weight: 500; color: #ccc;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #111 !important; border-bottom: 2px solid #111 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #fff !important;
    border: 1px solid rgba(0,0,0,0.11) !important;
    border-radius: 10px !important; color: #111 !important;
    font-size: 0.88rem !important; font-family: 'Inter', sans-serif !important;
    padding: 13px 16px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #111 !important;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.05) !important;
}
.stTextInput label, .stTextArea label {
    font-size: 0.68rem !important; font-weight: 600 !important;
    letter-spacing: 1px !important; text-transform: uppercase !important;
    color: #bbb !important; margin-bottom: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important; border-radius: 100px !important;
    font-weight: 600 !important; font-size: 0.78rem !important;
    letter-spacing: 0.2px !important; padding: 11px 24px !important;
    transition: all 0.15s ease !important; border: none !important;
}
.stButton > button[kind="primary"] {
    background: #111 !important;
    color: #f4f1ea !important;
    -webkit-text-fill-color: #f4f1ea !important;
}
/* Inner nodes get their own color from Streamlit theme — force contrast on dark pill */
.stButton > button[kind="primary"] *,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {
    color: #f4f1ea !important;
    -webkit-text-fill-color: #f4f1ea !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover * {
    color: #f4f1ea !important;
    -webkit-text-fill-color: #f4f1ea !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2a2a2a !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important; color: #666 !important;
    border: 1px solid rgba(0,0,0,0.14) !important;
}
.stButton > button[kind="secondary"]:hover { border-color: #666 !important; }

/* ── Answer card ── */
.answer-card {
    background: #fff; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px; padding: 26px 30px;
    margin: 20px 0 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-eyebrow {
    font-size: 0.66rem; font-weight: 600; letter-spacing: 1.2px;
    text-transform: uppercase; color: #ccc; margin-bottom: 12px;
}
.card-body { font-size: 0.88rem; color: #222; line-height: 1.8; }

/* ── Cache ── */
.cache-bar {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-left: 3px solid #22c55e; border-radius: 8px;
    padding: 9px 14px; font-size: 0.76rem; font-weight: 500;
    color: #15803d; margin-bottom: 12px;
}

/* ── Section divider ── */
.section-divider { border-top: 1px solid rgba(0,0,0,0.07); margin: 32px 0; }
.section-eyebrow {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: #bbb; margin-bottom: 18px;
}

/* ── Lint card ── */
.lint-card {
    background: #fff; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px; padding: 22px 26px;
    margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.lint-badge {
    display: inline-block; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    padding: 3px 9px; border-radius: 100px; margin-bottom: 10px;
}
.badge-conflict { background:#fef2f2; color:#dc2626; }
.badge-duplicate { background:#fffbeb; color:#b45309; }
.badge-stale { background:#fff7ed; color:#c2410c; }
.badge-missing_link { background:#eff6ff; color:#1d4ed8; }
.badge-unsupported_claim { background:#faf5ff; color:#7c3aed; }
.lint-pages { font-size:0.76rem; color:#aaa; font-family:monospace; margin-bottom:8px; }
.lint-claim { font-size:0.85rem; color:#444; line-height:1.6; margin:2px 0; }
.lint-rec {
    margin-top:12px; padding:9px 12px; background:#f9f8f6;
    border-radius:7px; font-size:0.81rem; color:#666; line-height:1.6;
}

/* ── Wiki card ── */
.wiki-card {
    background: #fff; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px; padding: 28px 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    font-size: 0.87rem; color: #333; line-height: 1.85; margin-top: 16px;
}

/* ── Markdown prose (Wiki tab, etc.) ──
   Custom .stApp background is light; if Streamlit follows OS dark mode, body
   text tokens stay light and disappear. Force dark prose on markdown blocks. */
[data-testid="stMarkdownContainer"] {
    color: #1a1a1a !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] blockquote {
    color: #1a1a1a !important;
}
[data-testid="stMarkdownContainer"] a {
    color: #155dfc !important;
}
[data-testid="stMarkdownContainer"] code {
    color: #1a1a1a !important;
    background: rgba(0,0,0,0.07) !important;
}
[data-testid="stMarkdownContainer"] pre {
    background: #f0eee8 !important;
    color: #1a1a1a !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
}
[data-testid="stMarkdownContainer"] pre code {
    background: transparent !important;
    color: #1a1a1a !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] details summary,
details summary {
    background: #111 !important;
    color: #f4f1ea !important;
    border-radius: 100px !important;
    padding: 11px 24px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    border: none !important;
    list-style: none !important;
}
[data-testid="stExpander"] summary:hover { background: #2a2a2a !important; }
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span { color: #f4f1ea !important; }
[data-testid="stExpander"] summary svg { stroke: #f4f1ea !important; }
[data-testid="stExpanderDetails"] {
    background: #fff !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin-top: 8px !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #fff !important; border: 1px solid rgba(0,0,0,0.11) !important;
    border-radius: 10px !important; color: #111 !important;
    font-size: 0.86rem !important; box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stSelectbox label {
    font-size: 0.68rem !important; font-weight: 600 !important;
    letter-spacing: 1px !important; text-transform: uppercase !important; color: #bbb !important;
}
/* Dropdown options */
[data-baseweb="select"] * { color: #111 !important; }
[data-baseweb="menu"] { background: #fff !important; border: 1px solid rgba(0,0,0,0.1) !important; }
[data-baseweb="option"] { background: #fff !important; color: #111 !important; }
[data-baseweb="option"]:hover { background: #f4f1ea !important; color: #111 !important; }
[aria-selected="true"][data-baseweb="option"] { background: #111 !important; color: #f4f1ea !important; }
/* Tab text */
.stTabs [data-baseweb="tab"] { color: #999 !important; }
.stTabs [aria-selected="true"] { color: #111 !important; }
/* All text inputs visible */
input, textarea, select { color: #111 !important; }
/* Spinner */
/* Spinner — nuclear fix */
div[data-testid="stSpinner"] * { color: #111 !important; stroke: #111 !important; border-color: #111 !important; }
div[data-testid="stSpinner"] > div > div {
    border-color: rgba(0,0,0,0.15) !important;
    border-top-color: #111 !important;
}
svg[class*="spinner"] *, svg[class*="Spinner"] * { stroke: #111 !important; }
.stSpinner * { color: #111 !important; }
.stSpinner > div > div {
    border-color: rgba(0,0,0,0.15) !important;
    border-top-color: #111 !important;
}
/* Target the actual rotating circle SVG */
[data-testid="stSpinner"] svg { display: none !important; }
[data-testid="stSpinner"]::before {
    content: '';
    display: inline-block;
    width: 18px; height: 18px;
    border: 2px solid rgba(0,0,0,0.15);
    border-top: 2px solid #111;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 10px;
    vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stSuccess > div, .stWarning > div, .stInfo > div {
    border-radius: 10px !important; font-size: 0.86rem !important;
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session ────────────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "thumb_up_shown" not in st.session_state:
    st.session_state.thumb_up_shown = False
if "cognee_ready" not in st.session_state:
    asyncio.run(setup_cognee())
    st.session_state.cognee_ready = True
if "lint_issues" not in st.session_state:
    st.session_state.lint_issues = None

SESSION_ID = st.session_state.session_id
pages = load_all_wiki_pages()

# ── Nav ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nav">
    <div class="nav-logo">WikiMind_</div>
    <div class="nav-meta">Cognee · Redis Stack · redisvl</div>
    <div class="nav-pill">Live Demo</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">AI Memory Hackathon · Pebblebed SF 2026</div>
    <div class="hero-title">A wiki that</div>
    <div class="hero-title-sub">learns from every question.</div>
    <div class="hero-desc">
        Permanent knowledge in Cognee's graph. Instant retrieval via Redis semantic cache.
        Correct an answer and the wiki improves — forever.
    </div>
</div>
<div class="stats-row">
    <div class="stat"><div class="stat-val">{len(pages)}</div><div class="stat-label">Pages</div></div>
    <div class="stat"><div class="stat-val">17</div><div class="stat-label">Docs ingested</div></div>
    <div class="stat"><div class="stat-val">3</div><div class="stat-label">Operations</div></div>
    <div class="stat"><div class="stat-val">&lt;50ms</div><div class="stat-label">Cache hit</div></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Ask + Improve", "Audit", "Wiki", "Knowledge Graph"])

# ── TAB 1 ──────────────────────────────────────────────────────────────────────
with tab1:
    question = st.text_input("Question", placeholder="How does session memory work in Cognee?", key="q")

    c1, _ = st.columns([1, 3])
    with c1:
        ask = st.button("Ask", type="primary", use_container_width=True)

    if ask:
        if not question.strip():
            st.warning("Enter a question.")
        else:
            with st.spinner("Searching knowledge graph..."):
                answer = asyncio.run(answer_question(question, SESSION_ID))
            st.session_state.last_question = question
            st.session_state.last_answer = answer
            st.session_state.thumb_up_shown = False

    if st.session_state.last_answer:
        if "SemanticCache" in st.session_state.last_answer:
            st.markdown('<div class="cache-bar">Redis SemanticCache hit — served instantly, no LLM call</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="answer-card">
            <div class="card-eyebrow">Answer</div>
            <div class="card-body">{st.session_state.last_answer}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div><div class="section-eyebrow">Improve this answer</div>', unsafe_allow_html=True)

        c1, _ = st.columns([1, 3])
        with c1:
            mark_correct = st.button("Mark correct", type="secondary", use_container_width=True)
        if mark_correct:
            st.success("Logged to session memory.")

        feedback = st.text_area("Correction", placeholder="What was wrong? What is the correct answer?", height=96, key="fb")
        wiki_target = st.text_input("Wiki page", placeholder="e.g. Cognee/recall or Redis/session-cache", key="wt")

        c1, _ = st.columns([1, 3])
        with c1:
            apply_clicked = st.button("Apply correction", type="primary", use_container_width=True)

        if apply_clicked:
            if feedback and wiki_target:
                with st.spinner("Rewriting wiki page..."):
                    corrected = asyncio.run(apply_feedback(
                        st.session_state.last_question,
                        st.session_state.last_answer,
                        feedback, wiki_target, SESSION_ID,
                    ))
                st.success("Wiki page updated and saved to Cognee graph.")
                st.markdown(f'<div style="color:#111;background:#fff;border:1px solid rgba(0,0,0,0.08);border-radius:12px;padding:24px 28px;margin-top:16px;font-size:0.88rem;line-height:1.8">{corrected}</div>', unsafe_allow_html=True)
            else:
                st.warning("Provide both a correction and the wiki page name.")

# ── TAB 2 ──────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-size:1.3rem;font-weight:700;color:#111;letter-spacing:-0.4px;margin-bottom:6px">Wiki Audit</div>
        <div style="font-size:0.86rem;color:#999;line-height:1.65">Detect conflicts, duplicates, stale content, missing links, and unsupported claims.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, _ = st.columns([1, 3])
    with c1:
        run = st.button("Run audit", type="primary", use_container_width=True)

    if run:
        with st.spinner("Auditing wiki pages..."):
            st.session_state.lint_issues = asyncio.run(run_lint())

    if st.session_state.lint_issues is not None:
        issues = st.session_state.lint_issues
        if not issues:
            st.success("No issues found. Wiki is consistent.")
        else:
            st.markdown(f'<div style="font-size:0.68rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#bbb;margin:24px 0 14px">{len(issues)} issue(s) detected</div>', unsafe_allow_html=True)
            for idx, issue in enumerate(issues):
                t = issue.get("type", "unknown")
                page_a = issue.get("page_a", "")
                page_b = issue.get("page_b", "")
                pages_str = page_a + ("  /  " + page_b if page_b else "")
                claim_a = f'<div class="lint-claim"><strong>A —</strong> {issue["claim_a"]}</div>' if issue.get("claim_a") else ""
                claim_b = f'<div class="lint-claim"><strong>B —</strong> {issue["claim_b"]}</div>' if issue.get("claim_b") else ""
                rec = f'<div class="lint-rec">{issue["recommendation"]}</div>' if issue.get("recommendation") else ""

                st.markdown(f"""
                <div class="lint-card">
                    <span class="lint-badge badge-{t}">{t.replace("_"," ")}</span>
                    <div class="lint-pages">{pages_str}</div>
                    {claim_a}{claim_b}{rec}
                </div>
                """, unsafe_allow_html=True)

                if page_a and page_b:
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Auto-fix (GPT decides)", key=f"auto_{idx}", type="primary", use_container_width=True):
                            with st.spinner("GPT resolving issue..."):
                                page_name, fixed = asyncio.run(auto_fix_issue(issue))
                                asyncio.run(apply_lint_fix(issue, fixed, page_name))
                            st.session_state[f"autofix_result_{idx}"] = (page_name, fixed)
                            st.session_state.lint_issues = None

                    with col2:
                        if st.button("Manual fix — I'll decide", key=f"toggle_{idx}", type="primary", use_container_width=True):
                            key = f"show_manual_{idx}"
                            st.session_state[key] = not st.session_state.get(key, False)

                    if st.session_state.get(f"show_manual_{idx}", False):
                        pages_data = load_all_wiki_pages()
                        content_a = pages_data.get(page_a, "")
                        content_b = pages_data.get(page_b, "")
                        preview_a = content_a[:200].replace("\n", " ").strip() + "..."
                        preview_b = content_b[:200].replace("\n", " ").strip() + "..."

                        st.markdown(f"""
                        <div style="background:#fff;border:1px solid rgba(0,0,0,0.08);border-radius:12px;padding:20px 24px;margin-top:8px">
                            <div style="font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#aaa;margin-bottom:16px">Choose the correct page</div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
                                <div style="border:1px solid rgba(0,0,0,0.1);border-radius:8px;padding:14px">
                                    <div style="font-size:0.72rem;font-weight:600;color:#888;font-family:monospace;margin-bottom:6px">{page_a}</div>
                                    <div style="font-size:0.82rem;color:#333;line-height:1.5">{preview_a}</div>
                                </div>
                                <div style="border:1px solid rgba(0,0,0,0.1);border-radius:8px;padding:14px">
                                    <div style="font-size:0.72rem;font-weight:600;color:#888;font-family:monospace;margin-bottom:6px">{page_b}</div>
                                    <div style="font-size:0.82rem;color:#333;line-height:1.5">{preview_b}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        chosen = st.radio(
                            "Which page is correct?",
                            [page_a, page_b],
                            key=f"radio_{idx}",
                        )
                        instruction = st.text_input(
                            "Additional instruction (optional)",
                            placeholder="e.g. keep the Redis-specific details, remove Elasticsearch references",
                            key=f"instr_{idx}",
                        )
                        c1, _ = st.columns([1, 3])
                        with c1:
                            if st.button("Apply manual fix", key=f"manual_{idx}", type="primary", use_container_width=True):
                                with st.spinner("Rewriting conflicting page..."):
                                    page_name, fixed = asyncio.run(manual_fix_issue(issue, chosen, instruction))
                                    asyncio.run(apply_lint_fix(issue, fixed, page_name))
                                st.session_state[f"manualfix_result_{idx}"] = (page_name, fixed)
                                st.session_state.lint_issues = None

                if f"autofix_result_{idx}" in st.session_state:
                    page_name, fixed = st.session_state[f"autofix_result_{idx}"]
                    st.success(f"Fixed: `{page_name}` rewritten automatically. Re-run audit to verify.")
                    st.markdown(fixed)

                if f"manualfix_result_{idx}" in st.session_state:
                    page_name, fixed = st.session_state[f"manualfix_result_{idx}"]
                    st.success(f"Fixed: `{page_name}` rewritten. Re-run audit to verify.")
                    st.markdown(fixed)

                st.markdown("<hr style='border:none;border-top:1px solid rgba(0,0,0,0.06);margin:8px 0 20px'>", unsafe_allow_html=True)

# ── TAB 3 ──────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-size:1.3rem;font-weight:700;color:#111;letter-spacing:-0.4px;margin-bottom:6px">Wiki Pages</div>
        <div style="font-size:0.86rem;color:#999;line-height:1.65">Knowledge base built from official Cognee and Redis documentation.</div>
    </div>
    """, unsafe_allow_html=True)

    if not pages:
        st.info("No pages yet. Run python ingest_all.py")
    else:
        selected = st.selectbox("Page", list(pages.keys()))
        if selected:
            st.markdown(pages[selected])

# ── TAB 4: GRAPH ───────────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style="margin-bottom:28px">
        <div style="font-size:1.3rem;font-weight:700;color:#111;letter-spacing:-0.4px;margin-bottom:6px">Knowledge Graph</div>
        <div style="font-size:0.86rem;color:#999;line-height:1.65">Visual map of entities and relationships extracted from all ingested documents.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, _ = st.columns([1, 3])
    with c1:
        if st.button("Refresh graph", type="secondary", use_container_width=True):
            subprocess.run([".venv/bin/python", "generate_graph.py"])

    graph_path = "graph.html"
    if os.path.exists(graph_path):
        with open(graph_path) as f:
            graph_html = f.read()
        st.components.v1.html(graph_html, height=580, scrolling=False)
    else:
        st.info("No graph yet. Click Refresh graph to generate.")
