"""Run this once to ingest all source_docs into the knowledge graph."""
import asyncio
import os
import uuid
from core.memory import setup_cognee
from core.ingest import ingest_doc

SOURCE_DIR = "source_docs"

async def main():
    await setup_cognee()
    session_id = str(uuid.uuid4())

    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith((".txt", ".md"))]
    print(f"Found {len(files)} docs to ingest...")

    for fname in files:
        path = os.path.join(SOURCE_DIR, fname)
        with open(path) as f:
            text = f.read()

        # Derive a wiki page name from filename e.g. cognee-remember.txt -> Cognee/remember
        base = fname.rsplit(".", 1)[0]
        parts = base.split("-", 1)
        if len(parts) == 2:
            category = parts[0].capitalize()
            name = parts[1]
            source_name = f"{category}/{name}"
        else:
            source_name = base

        print(f"  Ingesting {fname} -> {source_name} ...")
        wiki = await ingest_doc(text, source_name, session_id)
        print(f"  ✅ Done: {source_name}")

    print("\nAll docs ingested. Run the app with: ./run.sh")

if __name__ == "__main__":
    asyncio.run(main())
