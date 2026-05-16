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