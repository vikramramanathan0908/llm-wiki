import os
import numpy as np  # noqa: F401 — used inside semantic_search_disk
from openai import AsyncOpenAI
from core.config import WIKI_DATASET
from core.memory import remember_session, remember_permanent, recall as cognee_recall
from core.redis_memory import add_to_session, get_session_history, check_cache, store_cache, clear_cache

_openai_client: AsyncOpenAI | None = None


def _openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        key = (os.environ.get("OPENAI_API_KEY") or "").strip()
        if not key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set (check Streamlit Secrets or a local .env file)."
            )
        _openai_client = AsyncOpenAI(api_key=key)
    return _openai_client

WIKI_PAGE_DIR = "wiki_pages"

def load_all_wiki_pages() -> dict:
    pages = {}
    for root, _, files in os.walk(WIKI_PAGE_DIR):
        for fname in files:
            if fname.endswith(".md"):
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, WIKI_PAGE_DIR)
                with open(full) as f:
                    pages[rel] = f.read()
    return pages

async def embed(text: str) -> list:
    resp = await _openai().embeddings.create(model="text-embedding-3-small", input=text[:8000])
    return resp.data[0].embedding

async def semantic_search_disk(question: str, top_k: int = 3) -> list[tuple[str, str]]:
    """Find most relevant wiki pages from disk using embeddings."""
    import numpy as np
    pages = load_all_wiki_pages()
    if not pages:
        return []
    q_vec = await embed(question)
    scores = []
    for name, content in pages.items():
        p_vec = await embed(content[:4000])
        sim = float(np.dot(q_vec, p_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(p_vec) + 1e-9))
        scores.append((sim, name, content))
    scores.sort(reverse=True)
    return [(n, c) for _, n, c in scores[:top_k]]

async def answer_question(question: str, session_id: str) -> str:
    # Check semantic cache first
    cached = check_cache(question)
    if cached:
        add_to_session(session_id, question, cached + " *(cached)*")
        return cached + "\n\n*(⚡ Served from Redis SemanticCache)*"

    # Always search disk wiki pages (always current after corrections)
    disk_results = await semantic_search_disk(question)
    if disk_results:
        context = "\n\n---\n\n".join(f"**{n}**\n{c}" for n, c in disk_results)
        sources = ", ".join(f"`{n}`" for n, _ in disk_results)
        context_header = "Context from on-disk wiki pages (retrieved by similarity; may be only loosely related):"
    else:
        # Fallback to Cognee graph
        try:
            context_items = await cognee_recall(question, session_id=session_id)
            context = "\n\n".join(str(c) for c in context_items[:5]) if context_items else "No context found."
            sources = "Cognee knowledge graph"
        except Exception as e:
            context = "No context found."
            sources = "none"
        context_header = "Context from Cognee knowledge graph recall:"

    # Include Redis session history
    session_history = get_session_history(session_id)
    history_section = f"\nRecent conversation:\n{session_history}\n" if session_history else ""

    prompt = f"""You are a careful wiki assistant. You ONLY assert facts that are clearly stated in or directly entailed by the context below.

Rules:
- If the context does not mention a version number, release, product feature, or vendor backend, do NOT invent one. Say the wiki does not contain that information.
- Do not treat "Sources" filenames as proof that a claim is true; only use what is actually written in the context excerpts.
- If the question assumes something false or unsupported (e.g. a backend that is not in the docs), say so briefly.
- If you cannot answer from context, give a 1–2 sentence refusal and suggest what kind of doc would be needed.

{history_section}
{context_header}
{context}

Question: {question}

Answer concisely. Then end with a line:
**Sources:** {sources}"""

    response = await _openai().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    answer = response.choices[0].message.content

    add_to_session(session_id, question, answer)
    await remember_session(f"Q: {question}\nA: {answer}", session_id=session_id)
    store_cache(question, answer)
    return answer

async def apply_feedback(
    question: str,
    original_answer: str,
    feedback: str,
    wiki_page_name: str,
    session_id: str,
) -> str:
    pages = load_all_wiki_pages()
    original_content = ""
    for name, content in pages.items():
        if wiki_page_name.lower() in name.lower():
            original_content = content
            break

    prompt = f"""You are a wiki editor. Produce a corrected wiki page based on the feedback.

Original wiki page: {wiki_page_name}
Current content:
{original_content}

User question: {question}
Agent answer: {original_answer}
User feedback: {feedback}

Output the full corrected wiki page in markdown."""

    response = await _openai().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    corrected = response.choices[0].message.content

    await remember_permanent(corrected, dataset=WIKI_DATASET)
    await remember_session(f"Applied feedback on '{wiki_page_name}': {feedback[:100]}", session_id=session_id)
    clear_cache()  # invalidate cache so next question gets fresh answer from updated graph

    parts = wiki_page_name.split("/")
    if len(parts) == 2:
        folder = os.path.join(WIKI_PAGE_DIR, parts[0])
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, f"{parts[1]}.md")
    else:
        filepath = os.path.join(WIKI_PAGE_DIR, f"{wiki_page_name}.md")

    with open(filepath, "w") as f:
        f.write(corrected)

    return corrected
