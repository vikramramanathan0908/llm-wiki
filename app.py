import asyncio
import uuid
import streamlit as st
from core.memory import setup_cognee
from core.query import answer_question, apply_feedback
from core.lint import run_lint, load_all_wiki_pages

st.set_page_config(
    page_title="Knowledge Wiki",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* Global reset */
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
  }

  /* ── Background ── */
  .stApp {
    background: #0a0c10;
    color: #e2e8f0;
  }

  /* ── Top bar ── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 0 2rem 0;
    border-bottom: 1px solid #1e2530;
    margin-bottom: 2rem;
  }
  .topbar-left { display: flex; align-items: center; gap: 12px; }
  .topbar-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .topbar-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f1f5f9;
    letter-spacing: -0.01em;
  }
  .topbar-subtitle {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 400;
  }
  .session-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #64748b;
    background: #111827;
    border: 1px solid #1e2530;
    border-radius: 6px;
    padding: 4px 10px;
    letter-spacing: 0.05em;
  }

  /* ── Nav tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
    border-bottom: 1px solid #1e2530;
    padding-bottom: 0;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 8px 18px;
    border-radius: 8px 8px 0 0;
    transition: color 0.15s, background 0.15s;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: #cbd5e1;
    background: #111827;
  }
  .stTabs [aria-selected="true"] {
    color: #3b82f6 !important;
    background: #111827 !important;
    border-bottom: 2px solid #3b82f6 !important;
  }
  .stTabs [data-baseweb="tab-highlight"] { display: none; }
  .stTabs [data-baseweb="tab-border"] { display: none; }

  /* ── Section headers ── */
  .section-header {
    margin-bottom: 1.5rem;
  }
  .section-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
  }
  .section-header p {
    font-size: 0.82rem;
    color: #475569;
    margin: 0;
  }

  /* ── Cards ── */
  .card {
    background: #0f1520;
    border: 1px solid #1e2530;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }
  .card-sm {
    background: #0f1520;
    border: 1px solid #1e2530;
    border-radius: 10px;
    padding: 1rem 1.25rem;
  }

  /* ── Answer box ── */
  .answer-box {
    background: #0f1520;
    border: 1px solid #1e2530;
    border-left: 3px solid #3b82f6;
    border-radius: 0 12px 12px 0;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
  }
  .answer-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-bottom: 0.75rem;
  }
  .answer-content {
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.65;
  }

  /* ── Feedback section ── */
  .feedback-header {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #64748b;
    margin: 1.5rem 0 1rem 0;
    padding-top: 1.25rem;
    border-top: 1px solid #1e2530;
  }

  /* ── Input overrides ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.875rem !important;
    font-family: 'Inter', sans-serif !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
  }
  .stTextInput label, .stTextArea label, .stSelectbox label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    letter-spacing: 0.02em;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: #1e2530 !important;
    border: 1px solid #2d3748 !important;
    color: #cbd5e1 !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.25rem !important;
    transition: all 0.15s !important;
    letter-spacing: 0.01em;
  }
  .stButton > button:hover {
    background: #263044 !important;
    border-color: #3b82f6 !important;
    color: #e2e8f0 !important;
  }
  .stButton > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
  }

  /* ── Issue cards for lint ── */
  .issue-card {
    border: 1px solid #1e2530;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    background: #0f1520;
    transition: border-color 0.15s;
  }
  .issue-card:hover { border-color: #2d3748; }
  .issue-type {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
  }
  .type-conflict    { background: rgba(239,68,68,0.15);  color: #ef4444; }
  .type-duplicate   { background: rgba(234,179,8,0.12);  color: #eab308; }
  .type-stale       { background: rgba(249,115,22,0.12); color: #f97316; }
  .type-missing_link{ background: rgba(59,130,246,0.12); color: #60a5fa; }
  .type-unsupported_claim { background: rgba(16,185,129,0.1); color: #10b981; }
  .type-error       { background: rgba(156,163,175,0.1); color: #9ca3af; }
  .type-info        { background: rgba(148,163,184,0.08); color: #94a3b8; }
  .issue-page {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
  }
  .issue-claim {
    font-size: 0.82rem;
    color: #cbd5e1;
    margin: 4px 0;
    line-height: 1.5;
  }
  .issue-rec {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #1e2530;
  }

  /* ── Wiki page viewer ── */
  .wiki-layout {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 1.5rem;
  }
  .wiki-sidebar {
    background: #0f1520;
    border: 1px solid #1e2530;
    border-radius: 10px;
    padding: 0.75rem;
  }
  .wiki-content {
    background: #0f1520;
    border: 1px solid #1e2530;
    border-radius: 10px;
    padding: 1.5rem;
  }
  .wiki-page-content {
    color: #cbd5e1;
    font-size: 0.875rem;
    line-height: 1.7;
  }
  .wiki-page-content h1, .wiki-page-content h2 { color: #f1f5f9; }
  .wiki-page-content code {
    background: #111827;
    border: 1px solid #1e2530;
    border-radius: 4px;
    padding: 1px 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #60a5fa;
  }

  /* ── Status banners ── */
  .stSuccess > div, .stInfo > div, .stWarning > div, .stError > div {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
  }

  /* ── Spinner ── */
  .stSpinner > div {
    border-color: #3b82f6 transparent transparent transparent !important;
  }

  /* ── Divider ── */
  hr { border-color: #1e2530 !important; }

  /* ── Selectbox dropdown ── */
  .stSelectbox [data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 8px !important;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: #0f1520 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
  }
  .streamlit-expanderContent {
    background: #0f1520 !important;
    border: 1px solid #1e2530 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
  }

  /* ── Success icon ── */
  .success-state {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #10b981;
  }

  /* ── Stats row ── */
  .stats-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  .stat-chip {
    background: #111827;
    border: 1px solid #1e2530;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #64748b;
  }
  .stat-chip span {
    color: #94a3b8;
    font-weight: 600;
    margin-right: 4px;
  }

  /* ── Empty state ── */
  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #475569;
  }
  .empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.4;
  }
  .empty-state h3 {
    font-size: 1rem;
    font-weight: 500;
    color: #64748b;
    margin-bottom: 6px;
  }
  .empty-state p { font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── Session init ──────────────────────────────────────────────────────────────
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

SESSION_ID = st.session_state.session_id

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">&#129504;</div>
    <div>
      <div class="topbar-title">Knowledge Wiki</div>
      <div class="topbar-subtitle">Redis session &rarr; Cognee graph</div>
    </div>
  </div>
  <div class="session-badge">session&nbsp;&nbsp;{SESSION_ID[:8]}&hellip;</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  Ask & Improve  ", "  Lint  ", "  Wiki Pages  "])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ASK & IMPROVE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="section-header">
      <h2>Ask the Wiki</h2>
      <p>Query session memory and the knowledge graph. Provide corrections to improve wiki content.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "Question",
        placeholder="How does Cognee session memory work?",
        label_visibility="collapsed",
    )

    col_btn, col_spacer = st.columns([1, 5])
    with col_btn:
        ask_clicked = st.button("Search", type="primary", use_container_width=True)

    if ask_clicked:
        if not question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching session memory and knowledge graph..."):
                answer = asyncio.run(answer_question(question, SESSION_ID))
            st.session_state.last_question = question
            st.session_state.last_answer = answer
            st.session_state.thumb_up_shown = False

    if st.session_state.last_answer:
        st.markdown(f"""
        <div class="answer-box">
          <div class="answer-label">Answer</div>
          <div class="answer-content">{st.session_state.last_answer.replace(chr(10), "<br>")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Feedback section
        st.markdown('<div class="feedback-header">Feedback</div>', unsafe_allow_html=True)

        col_correct, col_correct_spacer = st.columns([1, 5])
        with col_correct:
            if st.button("Mark correct", use_container_width=True):
                st.session_state.thumb_up_shown = True

        if st.session_state.thumb_up_shown:
            st.markdown('<div class="success-state">Answer logged to session memory.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("Submit a correction"):
            feedback = st.text_area(
                "Correction",
                placeholder="The correct behavior is...",
                height=100,
            )
            wiki_target = st.text_input(
                "Wiki page to update",
                placeholder="Cognee/session-memory",
            )
            col_apply, col_apply_spacer = st.columns([1, 4])
            with col_apply:
                apply_clicked = st.button("Apply correction", type="primary", use_container_width=True)

            if apply_clicked:
                if feedback and wiki_target:
                    with st.spinner("Distilling feedback into wiki..."):
                        corrected = asyncio.run(apply_feedback(
                            st.session_state.last_question,
                            st.session_state.last_answer,
                            feedback,
                            wiki_target,
                            SESSION_ID,
                        ))
                    st.markdown(f"""
                    <div class="success-state">
                      Wiki page <code style="color:#10b981;background:transparent">{wiki_target}</code> updated successfully.
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="answer-box">
                      <div class="answer-label">Updated page</div>
                      <div class="answer-content">{corrected.replace(chr(10), "<br>")}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Fill in both the correction and the wiki page name.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — LINT
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="section-header">
      <h2>Lint the Wiki</h2>
      <p>Detect conflicts, duplicates, stale entries, missing links, and unsupported claims across all pages.</p>
    </div>
    """, unsafe_allow_html=True)

    col_lint_btn, col_lint_spacer = st.columns([1, 5])
    with col_lint_btn:
        lint_clicked = st.button("Run audit", type="primary", use_container_width=True)

    if lint_clicked:
        with st.spinner("Auditing wiki pages..."):
            issues = asyncio.run(run_lint())
        st.session_state["lint_issues"] = issues

    if "lint_issues" in st.session_state:
        issues = st.session_state["lint_issues"]
        if not issues:
            st.markdown('<div class="success-state">No issues found. All wiki pages look clean.</div>', unsafe_allow_html=True)
        else:
            type_counts: dict = {}
            for issue in issues:
                t = issue.get("type", "unknown")
                type_counts[t] = type_counts.get(t, 0) + 1

            # Stats chips
            chips_html = '<div class="stats-row">'
            chips_html += f'<div class="stat-chip"><span>{len(issues)}</span> total issues</div>'
            for t, count in sorted(type_counts.items()):
                chips_html += f'<div class="stat-chip"><span>{count}</span> {t.replace("_", " ")}</div>'
            chips_html += '</div>'
            st.markdown(chips_html, unsafe_allow_html=True)

            type_class = {
                "conflict": "type-conflict",
                "duplicate": "type-duplicate",
                "stale": "type-stale",
                "missing_link": "type-missing_link",
                "unsupported_claim": "type-unsupported_claim",
                "error": "type-error",
                "info": "type-info",
            }

            for issue in issues:
                itype = issue.get("type", "unknown")
                cls = type_class.get(itype, "type-info")
                page_a = issue.get("page_a", "")
                page_b = issue.get("page_b", "")
                claim_a = issue.get("claim_a", "")
                claim_b = issue.get("claim_b", "")
                rec = issue.get("recommendation", "")
                msg = issue.get("message", "")

                pages_html = f'<div class="issue-page">{page_a}'
                if page_b:
                    pages_html += f' &rarr; {page_b}'
                pages_html += '</div>'

                claims_html = ""
                if claim_a:
                    claims_html += f'<div class="issue-claim"><strong style="color:#94a3b8">Claim A:</strong> {claim_a}</div>'
                if claim_b:
                    claims_html += f'<div class="issue-claim"><strong style="color:#94a3b8">Claim B:</strong> {claim_b}</div>'
                if msg:
                    claims_html += f'<div class="issue-claim">{msg}</div>'

                rec_html = f'<div class="issue-rec"><strong>Recommendation:</strong> {rec}</div>' if rec else ""

                st.markdown(f"""
                <div class="issue-card">
                  <div class="issue-type {cls}">{itype.replace("_", " ").upper()}</div>
                  {pages_html}
                  {claims_html}
                  {rec_html}
                </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — WIKI PAGES
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="section-header">
      <h2>Wiki Pages</h2>
      <p>Browse the current state of all generated and corrected wiki pages.</p>
    </div>
    """, unsafe_allow_html=True)

    pages = load_all_wiki_pages()

    if not pages:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-state-icon">&#128196;</div>
          <h3>No wiki pages yet</h3>
          <p>Run <code>.venv/bin/python ingest_all.py</code> to ingest source docs.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        page_names = sorted(pages.keys())
        groups: dict = {}
        for name in page_names:
            group = name.split("/")[0] if "/" in name else "Other"
            groups.setdefault(group, []).append(name)

        col_sidebar, col_content = st.columns([1, 3], gap="medium")

        with col_sidebar:
            st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#475569;margin-bottom:0.75rem;">Pages</div>', unsafe_allow_html=True)
            selected = st.selectbox(
                "Select page",
                page_names,
                label_visibility="collapsed",
            )

            # Group listing for context
            for group, names in sorted(groups.items()):
                st.markdown(f'<div style="font-size:0.7rem;color:#64748b;margin:0.75rem 0 0.25rem 0;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">{group}</div>', unsafe_allow_html=True)
                for name in names:
                    short = name.split("/")[-1].replace(".md", "")
                    color = "#3b82f6" if name == selected else "#475569"
                    st.markdown(f'<div style="font-size:0.78rem;color:{color};padding:2px 0;cursor:pointer;">{short}</div>', unsafe_allow_html=True)

        with col_content:
            if selected:
                parts = selected.replace(".md", "").split("/")
                breadcrumb = " / ".join(parts)
                st.markdown(f'<div style="font-size:0.72rem;color:#475569;margin-bottom:0.75rem;font-family:\'JetBrains Mono\',monospace;">{breadcrumb}</div>', unsafe_allow_html=True)
                st.markdown(pages[selected])
