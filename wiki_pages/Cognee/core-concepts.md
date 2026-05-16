# Cognee/core-concepts

```markdown
# Cognee Documentation

## Summary
Cognee is an open-source platform designed to transform raw data into intelligent, searchable memory by combining vector search with graph databases. Its architecture supports both semantic search and structural reasoning, allowing users to manage and retrieve data effectively.

## Key Concepts

### Architecture
Cognee utilizes three complementary storage systems:
- **Relational Store**: Tracks documents, chunks, and provenance.
- **Vector Store**: Holds embeddings for semantic similarity.
- **Graph Store**: Captures entities and relationships in a knowledge graph.

### Building Blocks
The system is built from three fundamental components:
- **DataPoints**: Structured data units that serve as graph nodes.
- **Tasks**: Individual processing units for data transformation.
- **Pipelines**: Orchestrations of Tasks into coordinated workflows.

### Main Operations
Cognee provides four primary operations:
- **Remember**: Store new memory as permanent or session-based.
- **Recall**: Query stored memory with session-aware retrieval.
- **Improve**: Enrich existing memory and bridge session memory to permanent storage.
- **Forget**: Remove memory at various scopes.

### Further Concepts
Advanced features include:
- **Node Sets**: Tagging and organization system for knowledge base content.
- **Agent Memory Decorator**: Attaches memory retrieval to async agent functions.
- **Ontologies**: Connects data to established knowledge structures.
- **Loaders**: Normalize various file formats into text.
- **Chunkers**: Split documents for processing and embedding.

## API Examples
For detailed API usage and examples, refer to the [Cognee API Documentation](https://docs.cognee.ai/core-concepts/overview).

## Related Pages
- [Installation Guide](https://docs.cognee.ai/core-concepts/installation)
- [Quickstart](https://docs.cognee.ai/core-concepts/quickstart)
- [Cognee Community Adapters](https://docs.cognee.ai/core-concepts/community-adapters)
- [Contributing to Cognee](https://github.com/Cognee/core-concepts)

## Open Questions
- How can users effectively manage large knowledge bases with Node Sets?
- What are the best practices for integrating external ontologies in specific domains?
- How does the performance of different storage backends compare in production environments?
```
