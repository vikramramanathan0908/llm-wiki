"""Run this to apply a correction and demonstrate self-improvement."""
import asyncio
from core.memory import setup_cognee
from core.query import answer_question, apply_feedback

QUESTION = "How does redisvl SemanticCache work?"

ORIGINAL_ANSWER = """The SemanticCache in RedisVL works by caching responses from large language models (LLMs) based on the semantic meaning of the queries. This approach reduces latency and costs by allowing frequently accessed responses to be retrieved quickly without needing to recompute them. It leverages the understanding of context and meaning to ensure that the cached responses are relevant to the user's queries."""

CORRECTION = """The SemanticCache in redisvl works by storing LLM prompt-response pairs as vector embeddings in Redis Stack. When a new query arrives, it is embedded and compared against cached embeddings using cosine similarity. If a semantically similar query exists within the configured distance_threshold (e.g. 0.12), the cached response is returned instantly — no LLM call is made. This reduces latency from ~13 seconds to under 200ms and eliminates API costs for repeated or similar questions. The vectorizer (e.g. OpenAI text-embedding-3-small) converts prompts into vectors. The cache is invalidated explicitly via cache.clear() when a wiki correction is applied, ensuring stale answers never persist after self-improvement."""

WIKI_PAGE = "Redis/redisvl-concepts"
SESSION = "correction-demo"

async def main():
    await setup_cognee()

    print("=" * 60)
    print("BEFORE CORRECTION")
    print("=" * 60)
    before = await answer_question(QUESTION, SESSION)
    print(before)

    print()
    print("=" * 60)
    print("APPLYING CORRECTION...")
    print("=" * 60)
    corrected = await apply_feedback(QUESTION, ORIGINAL_ANSWER, CORRECTION, WIKI_PAGE, SESSION)
    print(f"Wiki page '{WIKI_PAGE}' rewritten.")
    print(f"Cache cleared.")
    print()
    print("New wiki page (preview):")
    print(corrected[:600])

    print()
    print("=" * 60)
    print("AFTER CORRECTION (same question)")
    print("=" * 60)
    after = await answer_question(QUESTION, SESSION)
    print(after)

asyncio.run(main())
