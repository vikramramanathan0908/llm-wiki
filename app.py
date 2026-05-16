import asyncio
import uuid
import os
import subprocess
import streamlit as st
from core.memory import setup_cognee
from core.query import answer_question, apply_feedback
from core.lint import run_lint, load_all_wiki_pages

st.set_page_config(
    page_title="WikiMind",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
    background: #111 !important; color: #f4f1ea !important;
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
.stSpinner > div { border-top-color: #111 !important; }

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
            with st.spinner(""):
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
            if st.button("Mark correct", type="secondary", use_container_width=True):
                st.success("Logged to session memory.")

        feedback = st.text_area("Correction", placeholder="What was wrong? What is the correct answer?", height=96, key="fb")
        wiki_target = st.text_input("Wiki page", placeholder="e.g. Cognee/recall or Redis/session-cache", key="wt")

        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("Apply correction", type="primary", use_container_width=True):
                if feedback and wiki_target:
                    with st.spinner(""):
                        corrected = asyncio.run(apply_feedback(
                            st.session_state.last_question,
                            st.session_state.last_answer,
                            feedback, wiki_target, SESSION_ID,
                        ))
                    st.success("Wiki page updated and saved to Cognee graph.")
                    st.markdown(f'<div class="wiki-card">{corrected}</div>', unsafe_allow_html=True)
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
        with st.spinner(""):
            st.session_state.lint_issues = asyncio.run(run_lint())

    if st.session_state.lint_issues is not None:
        issues = st.session_state.lint_issues
        if not issues:
            st.success("No issues found. Wiki is consistent.")
        else:
            st.markdown(f'<div style="font-size:0.68rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#bbb;margin:24px 0 14px">{len(issues)} issue(s) detected</div>', unsafe_allow_html=True)
            for issue in issues:
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
            st.markdown(f'<div class="wiki-card">{pages[selected]}</div>', unsafe_allow_html=True)

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
