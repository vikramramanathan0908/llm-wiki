import asyncio
import uuid
import streamlit as st
from core.memory import setup_cognee
from core.query import answer_question, apply_feedback
from core.lint import run_lint, load_all_wiki_pages

st.set_page_config(page_title="LLM Knowledge Wiki", page_icon="🧠", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "cognee_ready" not in st.session_state:
    asyncio.run(setup_cognee())
    st.session_state.cognee_ready = True

SESSION_ID = st.session_state.session_id

st.title("🧠 LLM Knowledge Wiki")
st.caption(f"Session: `{SESSION_ID[:8]}...` · Redis (session) → Cognee graph (permanent)")

tab1, tab2, tab3 = st.tabs(["💬 Ask + Improve", "🔍 Lint", "📚 Wiki Pages"])

# ── TAB 1: ASK + IMPROVE ───────────────────────────────────────────────────────
with tab1:
    st.header("Ask the Wiki")
    st.markdown("Query session memory + knowledge graph. Give feedback to improve the wiki.")

    question = st.text_input("Your question", placeholder="How does Cognee session memory work?")

    if st.button("🔎 Ask", type="primary"):
        if not question:
            st.warning("Enter a question.")
        else:
            with st.spinner("Recalling from session + graph..."):
                answer = asyncio.run(answer_question(question, SESSION_ID))
            st.session_state.last_question = question
            st.session_state.last_answer = answer

    if st.session_state.last_answer:
        st.markdown("**Answer:**")
        st.markdown(st.session_state.last_answer)

        st.divider()
        st.markdown("**Was this answer correct?**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Correct"):
                st.success("Great! Answer logged to session memory.")
        with col2:
            feedback = st.text_area("👎 Correction / feedback", placeholder="Actually, the correct behavior is...")
            wiki_target = st.text_input("Which wiki page to update?", placeholder="Cognee/session-memory")
            if st.button("✏️ Apply Correction"):
                if feedback and wiki_target:
                    with st.spinner("Distilling feedback into wiki..."):
                        corrected = asyncio.run(apply_feedback(
                            st.session_state.last_question,
                            st.session_state.last_answer,
                            feedback,
                            wiki_target,
                            SESSION_ID,
                        ))
                    st.success(f"✅ Wiki page `{wiki_target}` updated!")
                    st.markdown("**Updated wiki page:**")
                    st.markdown(corrected)
                else:
                    st.warning("Fill in both feedback and wiki page name.")

# ── TAB 2: LINT ────────────────────────────────────────────────────────────────
with tab2:
    st.header("Lint the Wiki")
    st.markdown("Detect conflicts, duplicates, stale entries, and unsupported claims.")

    if st.button("🔬 Run Lint", type="primary"):
        with st.spinner("Auditing wiki pages..."):
            issues = asyncio.run(run_lint())

        if not issues:
            st.success("✅ No issues found!")
        else:
            st.warning(f"Found {len(issues)} issue(s):")
            for i, issue in enumerate(issues):
                issue_type = issue.get("type", "unknown")
                color = {
                    "conflict": "🔴",
                    "duplicate": "🟡",
                    "stale": "🟠",
                    "missing_link": "🔵",
                    "unsupported_claim": "🟣",
                    "error": "⚫",
                    "info": "⚪",
                }.get(issue_type, "⚪")

                with st.expander(f"{color} [{issue_type.upper()}] {issue.get('page_a', '')}"):
                    if issue.get("page_b"):
                        st.write(f"**vs.** `{issue['page_b']}`")
                    if issue.get("claim_a"):
                        st.write(f"**Claim A:** {issue['claim_a']}")
                    if issue.get("claim_b"):
                        st.write(f"**Claim B:** {issue['claim_b']}")
                    if issue.get("recommendation"):
                        st.info(f"**Recommendation:** {issue['recommendation']}")
                    if issue.get("message"):
                        st.write(issue["message"])

# ── TAB 3: WIKI PAGES ──────────────────────────────────────────────────────────
with tab3:
    st.header("Current Wiki Pages")
    pages = load_all_wiki_pages()
    if not pages:
        st.info("No wiki pages yet. Run: .venv/bin/python ingest_all.py")
    else:
        selected = st.selectbox("Select a page", list(pages.keys()))
        if selected:
            st.markdown(f"**{selected}**")
            st.markdown(pages[selected])
