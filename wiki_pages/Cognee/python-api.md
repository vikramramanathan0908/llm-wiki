# Cognee/python-api

```markdown
# Cognee Python API Documentation

## Summary
The Cognee Python API provides a comprehensive interface for managing memory and data through a set of core and legacy operations. It allows users to store, query, enrich, and delete memory efficiently, facilitating the development of applications that leverage structured knowledge graphs.

## Key Concepts
- **Core Operations**: These are the primary functions for managing memory:
  - `remember()`: Store data as permanent or session memory.
  - `recall()`: Query memory with auto-routing and session-aware retrieval.
  - `improve()`: Enrich existing graph memory.
  - `forget()`: Remove specific data items or all memory for the current user.

- **Legacy Operations**: Lower-level operations for more granular control:
  - `add()`: Ingest various data types into the knowledge base.
  - `cognify()`: Transform raw data into a structured knowledge graph.
  - `search()`: Query the knowledge graph using multiple modes.
  - `memify()`: Enrich knowledge graphs with custom tasks.

- **Data Management**: Functions for handling datasets:
  - `datasets`: Manage datasets (list, create, delete).
  - `update()`: Update existing data items.
  - `prune`: Clean up data and resources.
  - `run_startup_migrations()`: Apply database schema migrations.

- **Session Management**: Manage conversation history and feedback:
  - Use `session_id` and `get_session()` to inspect stored history.
  - Feedback system for Q&A entries.

- **Configuration & Utilities**: Configure various settings and execute custom pipelines.

## API Examples
```python
import cognee

# Example v1.0 workflow
await cognee.remember("Your data here")
results = await cognee.recall("Your query")
```

## Related Pages
- [Cognee Cloud Documentation](https://docs.cognee.ai/cognee-cloud)
- [Integrations](https://docs.cognee.ai/integrations)
- [HTTP API Documentation](https://docs.cognee.ai/http-api)
- [Complete Documentation Index](https://docs.cognee.ai/llms.txt)

## Open Questions
- What are the best practices for using the `improve()` function effectively?
- How can the feedback system be optimized for better user interaction?
- Are there performance benchmarks available for the various search modes?
```