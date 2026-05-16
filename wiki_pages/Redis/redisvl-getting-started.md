# Redis/redisvl-getting-started

```markdown
# Getting Started with RedisVL

## Summary
RedisVL is a Python library with an integrated CLI designed for building AI applications using Redis. This guide provides an overview of the core workflow, including defining an index schema, preparing a sample dataset, creating a search index, loading data, and executing vector searches.

## Key Concepts

### Prerequisites
Before starting, ensure you have:
- Installed RedisVL: `pip install redisvl`
- A running Redis instance (Redis 8+ or Redis Cloud)

### What You'll Learn
By the end of this guide, you will be able to:
- Create index schemas using Python dictionaries or YAML files
- Build and manage `SearchIndex` objects
- Use the `rvl` CLI for index management
- Load data and execute vector similarity searches
- Fetch individual records and list all keys in an index
- Delete specific records by key or document ID
- Update index schemas as your application evolves

### Defining an IndexSchema
The `IndexSchema` maintains crucial index configuration and field definitions to enable search with Redis. It can be constructed from a Python dictionary or YAML file.

#### Example Schema Creation
**YAML Definition:**
```yaml
version: '0.1.0'
index:
  name: user_simple
  prefix: user_simple_docs
fields:
  - name: user
    type: tag
  - name: credit_score
    type: tag
  - name: job
    type: text
  - name: age
    type: numeric
  - name: user_embedding
    type: vector
    attrs:
      algorithm: flat
      dims: 3
      distance_metric: cosine
      datatype: float32
```

**Python Dictionary:**
```python
schema = {
    "index": {
        "name": "user_simple",
        "prefix": "user_simple_docs",
    },
    "fields": [
        {"name": "user", "type": "tag"},
        {"name": "credit_score", "type": "tag"},
        {"name": "job", "type": "text"},
        {"name": "age", "type": "numeric"},
        {
            "name": "user_embedding",
            "type": "vector",
            "attrs": {
                "dims": 3,
                "distance_metric": "cosine",
                "algorithm": "flat",
                "datatype": "float32"
            }
        }
    ]
}
```

## API Examples

### Sample Dataset Preparation
Create a mock dataset with user information:
```python
import numpy as np
data = [
    {
        'user': 'john',
        'age': 1,
        'job': 'engineer',
        'credit_score': 'high',
        'user_embedding': np.array([0.1, 0.1, 0.5], dtype=np.float32).tobytes()
    },
    {
        'user': 'mary',
        'age': 2,
        'job': 'doctor',
        'credit_score': 'low',
        'user_embedding': np.array([0.1, 0.1, 0.5], dtype=np.float32).tobytes()
    },
    {
        'user': 'joe',
        'age': 3,
        'job': 'dentist',
        'credit_score': 'medium',
        'user_embedding': np.array([0.9, 0.9, 0.1], dtype=np.float32).tobytes()
    }
]
```

### Creating a SearchIndex
To create a `SearchIndex`, connect to Redis:
```python
from redisvl.index import SearchIndex
from redis import Redis

client = Redis.from_url("redis://localhost:6379")
index = SearchIndex.from_dict(schema, redis_client=client, validate_on_load=True)
index.create(overwrite=True)
```

### Load Data to SearchIndex
Load the sample dataset into Redis:
```python
keys = index.load(data)
print(keys)
```

### Fetch and Manage Records
Fetch a record by ID:
```python
record = index.fetch("john")
print(record)
```

List all keys in the index:
```python
from redisvl.query import FilterQuery
from redisvl.query.filter import FilterExpression

query = FilterQuery(filter_expression=FilterExpression("*"), return_fields=["user", "age", "job"])
for batch in index.paginate(query, page_size=10):
    for doc in batch:
        print(f"Key: {doc['id']}, User: {doc['user']}")
```

### Deleting Records
Delete specific records:
```python
full_key = index.key("john")
deleted_count = index.drop_keys(full_key)
print(f"Deleted {deleted_count} record(s) by key")
```

### Creating VectorQuery Objects
Create a vector query object:
```python
from redisvl.query import VectorQuery

query = VectorQuery(vector=[0.1, 0.1, 0.5], vector_field_name="user_embedding", return_fields=["user", "age", "job", "credit_score", "vector_distance"], num_results=3)
results = index.query(query)
```

### Using an Asynchronous Redis Client
For asynchronous operations:
```python
from redisvl.index import AsyncSearchIndex
from redis.asyncio import Redis

client = Redis.from_url("redis://localhost:6379")
index = AsyncSearchIndex.from_dict(schema, redis_client=client)
results = await index.query(query)
```

### Updating a Schema
Update the index schema:
```python
index.schema.remove_field("job")
index.schema.remove_field("user_embedding")
index.schema.add_fields([
    {"name": "job", "type": "tag"},
    {
        "name": "user_embedding",
        "type": "vector",
        "attrs": {
            "dims": 3,
            "distance_metric": "cosine",
            "algorithm": "hnsw",
            "datatype": "float32"
        }
    }
])
await index.create(overwrite=True, drop=False)
```

## Related Pages
- [Query and Filter Data](https://redis.io/docs/latest/develop/ai/redisvl/user_guide/query_filter/)
- [Create Embeddings with Vectorizers](https://redis.io/docs/latest/develop/ai/redisvl/user_guide/embeddings/)
- [Choose a Storage Type](https://redis.io/docs/latest/develop/ai/redisvl/user_guide/storage_type/)

## Open Questions
- What are the best practices for managing large datasets in RedisVL?
- How can RedisVL be integrated with other AI frameworks?
- What are the performance implications of different vector indexing algorithms?
```
