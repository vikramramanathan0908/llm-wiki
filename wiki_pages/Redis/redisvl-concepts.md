```markdown
# Redis/redisvl-concepts

# RedisVL Concepts

## Summary
RedisVL provides foundational knowledge for building AI applications using Redis. The concepts outlined are language-agnostic and applicable across all RedisVL implementations, focusing on architecture, search and indexing, field attributes, query types, utilities, MCP integration, and extensions.

## Key Concepts

### 🏗️ Architecture
RedisVL components connect through schemas, indexes, queries, and extensions, forming a cohesive structure for AI applications.

### 🔍 Search & Indexing
This section covers schemas, fields, documents, storage types, and various query patterns essential for effective data retrieval.

### 🏷️ Field Attributes
Field attributes can be configured for various options such as sortable, no_index, index_missing, and more, allowing for tailored data handling.

### 🔎 Query Types
RedisVL supports multiple query options, including vector, filter, text, hybrid, and multi-vector queries, enabling flexible data access methods.

### 🔧 Utilities
Utilities include vectorizers for generating embeddings and rerankers for optimizing search results, enhancing the performance of AI applications.

### 🧠 MCP
RedisVL provides a stable tool contract that exposes existing Redis indexes to MCP clients, facilitating seamless integration.

### 🧩 Extensions
Pre-built patterns available in RedisVL include caching, message history, and semantic routing, which can be leveraged to enhance application functionality.

### 📦 SemanticCache
The SemanticCache in RedisVL works by storing large language model (LLM) prompt-response pairs as vector embeddings in Redis Stack. When a new query arrives, it is embedded and compared against cached embeddings using cosine similarity. If a semantically similar query exists within the configured `distance_threshold` (e.g., 0.12), the cached response is returned instantly—no LLM call is made. This approach reduces latency from approximately 13 seconds to under 200 milliseconds and eliminates API costs for repeated or similar questions. The vectorizer (e.g., OpenAI text-embedding-3-small) converts prompts into vectors. The cache can be invalidated explicitly via `cache.clear()` when a wiki correction is applied, ensuring that stale answers do not persist after self-improvement.

## API Examples
*Examples of API usage will be provided in the official RedisVL documentation.*

## Related Pages
- [Redis Documentation](https://redis.io/docs/)
- [RedisAI](https://redis.io/docs/ai/)
- [Redis Data Structures](https://redis.io/docs/data-types/)

## Open Questions
- What are the best practices for optimizing query performance in RedisVL?
- How can RedisVL be integrated with other AI frameworks?
- What are the limitations of current RedisVL implementations?
```