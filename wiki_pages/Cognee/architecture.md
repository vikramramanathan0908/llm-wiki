# Cognee/architecture

```markdown
# Cognee Architecture

## Summary
Cognee's architecture is designed to handle various aspects of memory through the integration of three complementary storage systems: a relational store, a vector store, and a graph store. This multi-store approach ensures that data is both searchable and connected, facilitating efficient retrieval and management of information.

## Key Concepts

### Why Multiple Stores
- **Relational Store**: Tracks documents, their chunks, and provenance (source and linkage of data).
- **Vector Store**: Holds embeddings for semantic similarity, enabling the identification of conceptually related text.
- **Graph Store**: Captures entities and relationships in a knowledge graph, allowing for structured navigation between concepts.

### What is Stored Where
- **Relational Store**: Document-level metadata and provenance.
- **Vector Store**: Semantic fingerprints of chunks and DataPoints.
- **Graph Store**: Higher-level structure represented as entities and relationships.

### How They Are Used
- **Permanent Memory Ingestion**: The relational store is crucial for tracking documents and their origins.
- **Recall and Retrieval**:
  - **Semantic Searches**: Utilize the vector store to find conceptually related passages.
  - **Structural Searches**: Use the graph store to explore entities and relationships via Cypher.
  - **Hybrid Searches**: Combine vector and graph searches for contextually rich results.

## API Examples
For detailed API usage, refer to the [Cognee API documentation](https://docs.cognee.ai/core-concepts/architecture).

## Related Pages
- [Getting Started](https://docs.cognee.ai/core-concepts/getting-started)
- [Core Concepts](https://docs.cognee.ai/core-concepts/overview)
- [Main Operations](https://docs.cognee.ai/core-concepts/main-operations)
- [Setup Configuration](https://docs.cognee.ai/core-concepts/setup-configuration)

## Open Questions
- How can the efficiency of data indexing be improved across the different stores?
- What are the best practices for integrating production-ready backends?
- How does the architecture scale with increasing data volume and complexity?
```