import uuid
import os
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY, WIKI_DATASET, SOURCE_DATASET
from core.memory import remember_permanent, remember_session

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

WIKI_PAGE_DIR = "wiki_pages"

async def generate_wiki_page(text: str, source_name: str) -> str:
    prompt = f"""You are a wiki writer. Given the following document, produce a structured markdown wiki page.

Source: {source_name}

Document:
{text}

Output a markdown wiki page with these sections:
## Summary
## Key Concepts
## API Examples
## Related Pages
## Open Questions

Be concise and factual."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content

async def ingest_doc(text: str, source_name: str, session_id: str) -> str:
    """Ingest a document: store raw + generate wiki page + write to graph."""
    # 1. Store raw source permanently
    await remember_permanent(text, dataset=SOURCE_DATASET)

    # 2. Generate wiki page via LLM
    wiki_page = await generate_wiki_page(text, source_name)

    # 3. Store wiki page permanently in graph
    wiki_content = f"# {source_name}\n\n{wiki_page}"
    await remember_permanent(wiki_content, dataset=WIKI_DATASET)

    # 4. Save wiki page to disk
    safe_name = source_name.replace("/", "_").replace(" ", "-")
    parts = source_name.split("/")
    if len(parts) == 2:
        folder = os.path.join(WIKI_PAGE_DIR, parts[0])
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, f"{parts[1]}.md")
    else:
        os.makedirs(WIKI_PAGE_DIR, exist_ok=True)
        filepath = os.path.join(WIKI_PAGE_DIR, f"{safe_name}.md")

    with open(filepath, "w") as f:
        f.write(wiki_content)

    # 5. Log ingestion event to session memory
    await remember_session(
        f"Ingested '{source_name}'; wiki page created at {filepath}.",
        session_id=session_id,
    )

    return wiki_content
