"""Scrape Cognee and Redis docs and save to source_docs/."""
import asyncio
import os
import httpx
from bs4 import BeautifulSoup

OUTPUT_DIR = "source_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PAGES = [
    # Cognee docs
    ("cognee-introduction", "https://docs.cognee.ai/getting-started/introduction"),
    ("cognee-quickstart", "https://docs.cognee.ai/getting-started/quickstart"),
    ("cognee-core-concepts", "https://docs.cognee.ai/core-concepts/overview"),
    ("cognee-architecture", "https://docs.cognee.ai/core-concepts/architecture"),
    ("cognee-vector-stores", "https://docs.cognee.ai/setup-configuration/vector-stores"),
    ("cognee-python-api", "https://docs.cognee.ai/python-api"),
    ("cognee-api-reference", "https://docs.cognee.ai/api-reference/introduction"),
    # Redis / redisvl docs
    ("redis-redisvl-intro", "https://redis.io/docs/latest/develop/ai/redisvl/"),
    ("redis-redisvl-install", "https://redis.io/docs/latest/develop/ai/redisvl/install/"),
    ("redis-redisvl-concepts", "https://redis.io/docs/latest/develop/ai/redisvl/concepts/"),
    ("redis-redisvl-getting-started", "https://redis.io/docs/latest/develop/ai/redisvl/user_guide/getting_started/"),
    ("redis-redisvl-use-cases", "https://redis.io/docs/latest/develop/ai/redisvl/user_guide/use_cases/"),
    ("redis-redisvl-how-to", "https://redis.io/docs/latest/develop/ai/redisvl/user_guide/how_to_guides/"),
    ("redis-when-to-choose", "https://redis.io/docs/latest/develop/ai/when-to-choose-redis/"),
]

async def fetch_page(client: httpx.AsyncClient, name: str, url: str) -> None:
    try:
        resp = await client.get(url, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove nav, footer, scripts, styles
        for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()

        # Try to get main content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(class_=lambda c: c and "content" in c.lower())
            or soup.body
        )

        text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)

        # Clean up excessive blank lines
        lines = [l for l in text.splitlines() if l.strip()]
        clean = "\n".join(lines)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.txt")
        with open(out_path, "w") as f:
            f.write(f"Source: {url}\n\n{clean}")

        print(f"  ✅ {name} ({len(clean)} chars)")
    except Exception as e:
        print(f"  ⚠️  {name} failed: {e}")

async def main():
    print(f"Fetching {len(PAGES)} pages into {OUTPUT_DIR}/...\n")
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        tasks = [fetch_page(client, name, url) for name, url in PAGES]
        await asyncio.gather(*tasks)
    print(f"\nDone. Run: .venv/bin/python ingest_all.py")

if __name__ == "__main__":
    asyncio.run(main())
