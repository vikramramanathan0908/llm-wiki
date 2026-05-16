# Cognee/quickstart

# Cognee Quickstart Documentation

## Summary
Cognee is a platform designed to transform documents into AI memory, creating a structured and queryable representation of content for AI systems. This documentation provides a quickstart guide to help users install and run their first example with Cognee, utilizing its core functionalities for storing and retrieving information.

## Key Concepts
- **Memory Operations**: 
  - `.remember`: Stores data in memory, performing ingestion, chunking, entity extraction, graph building, and enrichment.
  - `.recall`: Retrieves data from memory using optimal retrieval strategies.

- **Asynchronous Programming**: 
  - Cognee employs asynchronous code extensively, using `async` and `await` to handle I/O operations without blocking program execution.

- **Knowledge Graph**: 
  - Cognee builds a fully queryable knowledge graph that enriches and organizes stored information for efficient retrieval.

## API Examples
### Basic Usage Example
```python
import cognee
import asyncio

async def main():
    # Create a clean slate for cognee -- reset data and system state
    await cognee.forget(everything=True)
    
    # Store content in memory
    text = "Cognee turns documents into AI memory."
    await cognee.remember(text)
    
    # Retrieve from memory
    results = await cognee.recall(query_text="What does Cognee do?")
    
    # Print results
    for result in results:
        print(result.text)

if __name__ == '__main__':
    asyncio.run(main())
```
### Example Output
```
Cognee converts (transforms) documents into AI memory — a structured, queryable representation of document content for AI systems.
```

## Related Pages
- [Getting Started](https://docs.cognee.ai/getting-started/quickstart)
- [Cognee Core Concepts](https://docs.cognee.ai/core-concepts)
- [Cognee Community Adapters](https://docs.cognee.ai/community-adapters)
- [Async Programming Guide](https://docs.cognee.ai/async-guide)

## Open Questions
- How can existing memory be enriched further?
- What are the best practices for managing permissions and security in Cognee?
- How does Cognee integrate with various LLM providers and output backends?