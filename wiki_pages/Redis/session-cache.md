# Redis/session-cache

# Redis Session Memory in Cognee

## Summary
Redis serves as the session memory for Cognee, providing a fast, temporary storage solution for recent conversation contexts while maintaining a durable knowledge graph for permanent data.

## Key Concepts
- **Session Management**: 
  - `cognee.remember(..., session_id="abc")`: Stores data in Redis under the specified session key.
  - `cognee.recall(..., session_id="abc")`: Retrieves data from Redis first, falling back to the permanent knowledge graph if necessary.
  
- **Two-Tier Architecture**:
  - **Redis**: Offers sub-millisecond retrieval for recent conversation contexts.
  - **Cognee Graph**: Provides durable and cross-session permanent knowledge.

- **Vector Search**: 
  - Redis supports vector search through the Query Engine (using the `redis/redis-stack` image).
  - `redisvl` provides Python bindings for Redis vector indexes, semantic caching, and session management.

## API Examples
To configure Redis as the vector store in Cognee, use the following settings:
```python
config.vector_db_provider = "redis"
config.vector_db_url = "redis://localhost:6379"
```

## Related Pages
- [Cognee Documentation](#)
- [Redis Documentation](#)
- [Redis Vector Search](#)

## Open Questions
- What are the best practices for managing session data in Redis?
- How does Redis handle data expiration for session keys?
- What are the performance implications of using Redis for large-scale applications?