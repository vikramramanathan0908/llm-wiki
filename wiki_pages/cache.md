```markdown
# Cache

## Summary
Caching in Cognee is implemented through a combination of Elasticsearch and Redis, providing a fast, temporary storage solution for recent conversation contexts while maintaining a durable knowledge graph for permanent data.

## Key Concepts
- **Session Management**: 
  - `cognee.remember(..., session_id="abc")`: Stores data in Elasticsearch under the specified session key, acting as the hot scratchpad tier for quick access.
  - `cognee.recall(..., session_id="abc")`: Retrieves data from Elasticsearch first, falling back to the permanent knowledge graph if necessary. For permanent storage, use `cognee.remember(..., dataset_name=...)` without a session_id.

- **Two-Tier Architecture**:
  - **Elasticsearch**: Provides fast retrieval for recent conversation contexts, functioning as a hot scratchpad for session data.
  - **Cognee Graph**: Offers durable and cross-session permanent knowledge.

- **Vector Search**: 
  - Elasticsearch supports vector search capabilities, allowing for efficient querying of semantic data.
  - `redisvl` provides Python bindings for Redis vector indexes, semantic caching, and session management.

## API Examples
To configure Elasticsearch as the vector store in Cognee, use the following settings:
```python
config.vector_db_provider = "elasticsearch"
config.vector_db_url = "http://localhost:9200"
```

## Related Pages
- [Cognee Documentation](#)
- [Elasticsearch Documentation](#)
- [Elasticsearch Vector Search](#)

## Open Questions
- What are the best practices for managing session data in Elasticsearch?
- How does Elasticsearch handle data expiration for session keys?
- What are the performance implications of using Elasticsearch for large-scale applications?
```