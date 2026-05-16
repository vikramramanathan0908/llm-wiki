# Cognee/api-reference

```markdown
# Cognee API Reference

## Summary
The Cognee API provides a comprehensive set of endpoints for building, managing, and querying memory using Cognee’s powerful platform. It supports various operations such as data ingestion, knowledge processing, and semantic search, allowing users to effectively manage their knowledge graphs.

## Key Concepts

### Getting Started
- **Cognee Cloud**: A managed cloud platform for production use with automatic scaling and enterprise features.
- **Local Docker Setup**: A self-hosted option for development and testing using Docker.

### API Base URLs
- **Production (Cognee Cloud)**: `https://api.cognee.ai`
- **Local Development**: `http://localhost:8000`

### Authentication
- **Cognee Cloud**: Requires an API key in the header (`X-Api-Key: YOUR-API-KEY`).
- **Local Docker**: Optional authentication; can be disabled for local development.

### Core API Endpoints
- **Data Ingestion**: `POST /api/v1/add`
- **Knowledge Processing**: `POST /api/v1/cognify`
- **Semantic Search**: `POST /api/v1/search`
- **Data Management**: `DELETE /api/v1/datasets`

### API Features
- Multiple search types (e.g., GRAPH_COMPLETION, RAG_COMPLETION).
- Support for various input formats (text, structured data, code, URLs).
- Granular control over data deletion.

## API Examples
### Python Example
```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"  # or https://api.cognee.ai for Cognee Cloud
API_KEY = "your-api-key"  # only for Cognee Cloud
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY  # only for Cognee Cloud
}

# 1. Add data
add_response = requests.post(
    f"{BASE_URL}/api/v1/add",
    json={"data": "AI is transforming how we work and live."},
    headers=headers
)

# 2. Process into knowledge graph
cognify_response = requests.post(
    f"{BASE_URL}/api/v1/cognify",
    json={"datasets": ["main_dataset"]},
    headers=headers
)

# 3. Search the knowledge graph
search_response = requests.post(
    f"{BASE_URL}/api/v1/search",
    json={"query": "What is AI?", "search_type": "GRAPH_COMPLETION"},
    headers=headers
)

print(search_response.json())
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/add" \
-H "Content-Type: application/json" \
-H "X-Api-Key: your-api-key" \
-d '{"data": "AI is transforming how we work and live."}'
```

## Related Pages
- [Getting Started](https://docs.cognee.ai/api-reference/introduction)
- [Cognee Cloud Documentation](https://docs.cognee.ai/cognee-cloud)
- [Interactive API Explorer](https://api.cognee.ai/docs)

## Open Questions
- What are the best practices for managing API keys and authentication?
- How can we optimize the performance of the API for large datasets?
- What additional features are planned for future releases of the API?
```