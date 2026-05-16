# Cognee/vector-stores

# Vector Stores Documentation

## Summary
Vector stores in Cognee hold embeddings for semantic similarity search, enabling the discovery of conceptually related content based on meaning rather than exact text matches. This documentation outlines the supported providers, configuration settings, and setup guides for various vector store options.

## Key Concepts
- **Vector Stores**: Databases that store embeddings for semantic searches.
- **Supported Providers**: Multiple vector store options are available, including:
  - **LanceDB**: File-based vector store (default).
  - **PGVector**: Postgres-backed storage with pgvector extension.
  - **Qdrant**: High-performance vector database.
  - **Redis**: Fast vector similarity search via Redis Search module.
  - **ChromaDB**: HTTP server-based vector database.
  - **FalkorDB**: Hybrid graph and vector database.
  - **Neptune Analytics**: Amazon Neptune hybrid solution.
  
- **Configuration**: Environment variables must be set in the `.env` file, including:
  - `VECTOR_DB_PROVIDER`: The chosen vector store provider.
  - `VECTOR_DB_URL`: Database URL or connection string.
  - `VECTOR_DB_KEY`: Authentication key (if required).
  - `VECTOR_DB_PORT`: Database port (if applicable).

## API Examples
### LanceDB Configuration
```bash
VECTOR_DB_PROVIDER="lancedb"
# Optional: VECTOR_DB_URL=/absolute/or/relative/path/to/cognee.lancedb
```

### PGVector Configuration
```bash
VECTOR_DB_PROVIDER="pgvector"
# Ensure Postgres connection details are set
pip install "cognee[postgres]"
```

### Qdrant Configuration
```bash
VECTOR_DB_PROVIDER="qdrant"
VECTOR_DB_URL="http://localhost:6333"
pip install cognee-community-vector-adapter-qdrant
```

### Redis Configuration
```bash
VECTOR_DB_PROVIDER="redis"
VECTOR_DB_URL="redis://localhost:6379"
pip install cognee-community-vector-adapter-redis
```

### ChromaDB Configuration
```bash
VECTOR_DB_PROVIDER="chromadb"
VECTOR_DB_URL="http://localhost:3002"
VECTOR_DB_KEY="<your_token>"
pip install "cognee[chromadb]"
```

## Related Pages
- [Setup Configuration Overview](https://docs.cognee.ai/setup-configuration)
- [Cognee Documentation Home](https://docs.cognee.ai)
- [Community Adapters](https://docs.cognee.ai/community-adapters)

## Open Questions
- What are the performance benchmarks for each vector store provider?
- How does the choice of vector store impact the overall system architecture?
- Are there specific use cases where one vector store is preferred over others?