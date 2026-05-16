```markdown
# Cognee/remember

## Cognee remember() API

### Summary
The `cognee.remember()` function is designed to ingest data into Cognee's memory system. It allows for the storage of data either temporarily in session memory or permanently in the knowledge graph, depending on the parameters provided.

### Key Concepts
- **Session Memory**: If a `session_id` is provided, data is stored in a Redis-backed session cache, which is ephemeral and specific to a conversation. This storage tier is completely separate from permanent storage.
- **Permanent Storage**: If only a `dataset_name` is specified, the data is permanently stored in the Cognee knowledge graph, which utilizes NetworkX and LanceDB. This ensures that the data persists across sessions and is accessible later.
- **Data Types**: The function can accept various types of data, including text, file paths, URLs, or `SkillRunEntry`.

### API Examples
```python
# Permanent wiki fact
await cognee.remember("Cognee uses LanceDB as its default vector store.", dataset_name="llm_wiki")

# Session memory (ephemeral, stored in Redis)
await cognee.remember("User is asking about session memory.", session_id="session_123")
```

### Related Pages
- [Cognee API Overview](#)
- [Cognee Knowledge Graph](#)
- [Session Management in Cognee](#)

### Open Questions
- What are the limitations on data size for `cognee.remember()`?
- How does the knowledge graph handle data conflicts or duplicates?
- What are the best practices for managing session IDs?

### User Question
**What is the difference between `cognee.remember` with `session_id` vs `dataset_name`?**

### Agent Answer
The difference between `cognee.remember` with `session_id` and `dataset_name` is that using `session_id` stores data temporarily in the Redis session cache, which is specific to the current user session and allows for quick retrieval. In contrast, using `dataset_name` stores data permanently in the Cognee knowledge graph, ensuring it persists across sessions and is accessible later.

**Sources:** Cognee knowledge graph
```