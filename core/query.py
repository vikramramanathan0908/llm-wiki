import os
import numpy as np
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, WIKI_DATASET
from core.memory import remember_session, remember_permanent, recall as cognee_recall
from core.redis_memory import add_to_session, get_session_history, check_cache, store_cache

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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

async def answer_question(question: str, session_id: str) -> str:
    # Check semantic cache first
    cached = check_cache(question)
    if cached:
        add_to_session(session_id, question, cached + " *(cached)*")
        return cached + "\n\n*(⚡ Served from Redis SemanticCache)*"

    # Query Cognee knowledge graph
    try:
        context_items = await cognee_recall(question, session_id=session_id)
        if context_items:
            if isinstance(context_items, list):
                context = "\n\n".join(str(c) for c in context_items[:5])
            else:
                context = str(context_items)
            sources = "Cognee knowledge graph"
        else:
            raise ValueError("Empty recall")
    except Exception as e:
        print(f"[cognee] recall failed, falling back to disk: {e}")
        pages = load_all_wiki_pages()
        context = "\n\n---\n\n".join(f"**{n}**\n{c}" for n, c in list(pages.items())[:3])
        sources = "wiki pages (disk fallback)"

    # Include Redis session history
    session_history = get_session_history(session_id)
    history_section = f"\nRecent conversation:\n{session_history}\n" if session_history else ""

    prompt = f"""You are a wiki assistant. Answer the question using the context below.
{history_section}
Context from Cognee knowledge graph:
{context}

Question: {question}

Answer concisely, then end with:
**Sources:** {sources}"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
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

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    corrected = response.choices[0].message.content

    await remember_permanent(corrected, dataset=WIKI_DATASET)
    await remember_session(f"Applied feedback on '{wiki_page_name}': {feedback[:100]}", session_id=session_id)

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
