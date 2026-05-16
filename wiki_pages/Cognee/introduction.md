# Cognee/introduction

```markdown
# Cognee Documentation

## Summary
Cognee is a powerful tool designed to enhance AI memory by linking documents and creating context for LLM (Large Language Model) calls. It allows users to store, query, enrich, and delete memory, enabling more effective interactions with AI models.

## Key Concepts
- **AI Memory**: Addresses the stateless nature of LLM calls by providing a memory layer that connects documents and maintains context.
- **Core Operations**:
  - `.remember`: Store data in memory by ingesting text, files, or URLs and building a knowledge graph.
  - `.recall`: Query memory using natural language, with automatic or specified retrieval strategies.
  - `.improve`: Enrich existing memory by applying feedback-based weighting and bridging session memory into the permanent graph.
  - `.forget`: Remove specific data items or entire datasets from memory.
- **Lower-Level Operations**: Includes `Add`, `Cognify`, `Search`, and `Memify` for direct control over memory management.

## API Examples
- **Installation**: Follow the [Installation Guide](https://docs.cognee.ai/getting-started/installation) to set up your environment.
- **Quickstart**: Run your first knowledge graph example with the [Quickstart Tutorial](https://docs.cognee.ai/getting-started/quickstart).

## Related Pages
- [Getting Started](https://docs.cognee.ai/getting-started/introduction)
- [Core Concepts](https://docs.cognee.ai/getting-started/core-concepts)
- [Setup Configuration](https://docs.cognee.ai/getting-started/setup-configuration)
- [Cognee Community Adapters](https://docs.cognee.ai/guides/community-adapters)
- [Documentation Index](https://docs.cognee.ai/llms.txt)

## Open Questions
- How can users best utilize the `.improve` operation for specific use cases?
- What are the best practices for managing memory with the `.forget` operation?
- How does Cognee handle security and privacy in memory management?
```
