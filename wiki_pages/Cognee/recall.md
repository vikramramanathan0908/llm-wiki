# Cognee/recall

# Cognee Recall API

## Summary
The `cognee.recall()` API function is designed to retrieve relevant information from Cognee's memory. It allows users to query either a session-specific cache or a permanent knowledge graph, depending on whether a session ID is provided.

## Key Concepts
- **Session ID**: If provided, the API first searches the Redis session cache for relevant information. If not, it queries the permanent knowledge graph.
- **Permanent Knowledge Graph**: A comprehensive database that stores information for retrieval when no session context is available.
- **Semantic Similarity**: Results returned by the recall function are ranked based on how semantically similar they are to the query.
- **Memory Chunks**: The API returns a list of relevant memory chunks along with their source metadata, which can be used for generating grounded and cited answers.

## API Examples
```python
# Query with session context
results = await cognee.recall("how does session memory work?", session_id="session_123")

# Query permanent graph only
results = await cognee.recall("what is cognee?")
```

## Related Pages
- [Cognee API Overview](#)
- [Session Management in Cognee](#)
- [Understanding Semantic Similarity](#)

## Open Questions
- What are the limitations of the memory retrieval process?
- How does Cognee handle ambiguous queries?
- What is the maximum size of the memory chunks returned?