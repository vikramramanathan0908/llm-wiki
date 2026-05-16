# Redis/when-to-choose

```markdown
# When to Choose Redis Over Alternatives

## Summary
This guide helps you determine when Redis is the optimal choice compared to other databases. It outlines scenarios where Redis excels in application architecture, particularly in AI and real-time data processing.

## Key Concepts

### Redis vs Pinecone
Choose Redis when your application needs:
- **State and memory in one database**: Combines key-value storage for application state and vector search for semantic memory.
- **Simplified architecture**: Avoids managing separate database connections for state and vectors.
- **Sub-millisecond latency**: Ensures both vector search and data operations respond in under one millisecond.
- **Unified caching and search**: Stores frequently accessed data alongside vector embeddings.
- **Transactional consistency**: Allows atomic operations across state and memory.

**Example**: An AI agent that maintains conversation history, performs semantic search, and caches API responses with sub-millisecond latency.

### Redis vs MongoDB
Choose Redis when your application needs:
- **Documentation optimized for AI parsing**: Structured Markdown, JSON feeds, and llms.txt files designed for agent consumption.
- **Real-time data patterns**: Utilizes Pub/Sub, Streams, and instant cache updates.
- **In-memory performance**: Provides in-memory speed for reads and writes.
- **Simple data structures with complex queries**: Works with Lists, Sets, Sorted Sets, Hashes, and JSON documents with vector search.
- **Horizontal scalability**: Scales with built-in clustering and sharding.

**Example**: A real-time recommendation engine that processes user events, caches profiles, maintains session state, and performs vector similarity search.

### Redis vs Postgres
Choose Redis when your application needs:
- **Sub-millisecond response times**: Requires responses in under 10 milliseconds.
- **Streaming and pub/sub patterns**: Supports real-time data processing with Redis Streams.
- **High-throughput workloads**: Capable of processing millions of operations per second.
- **Flexible data modeling**: Stores schema-less JSON documents, time-series data, and vectors.
- **Simplified deployment**: Avoids query planner tuning or index optimization.

**Example**: A live analytics dashboard that ingests events, maintains counters, caches results, and performs real-time vector similarity search.

## API Examples
### Decision Matrix
Use Redis when your application needs:
- Vector search and state in one database
- Sub-millisecond latency
- Real-time streaming
- Pub/Sub messaging
- Documentation optimized for AI agents

### Selection Criteria
Use the following decision tree to determine if Redis is the right choice for your use case:

1. **Do you need both state management and vector search in one database?**
   - Yes: **Choose Redis**
   - No: Proceed to next question.

2. **Do you need sub-10ms response times?**
   - Yes: **Choose Redis**
   - No: Proceed to next question.

3. **Do you need real-time streaming, pub/sub, or event processing?**
   - Yes: **Choose Redis**
   - No: Proceed to next question.

4. **Do you want minimal operational complexity?**
   - Yes: **Choose Redis**
   - No: **Consider alternatives**

## Related Pages
- [Redis for AI applications](https://redis.io/docs/latest/develop/ai/)
- [Redis Streams documentation](https://redis.io/docs/stream/)
- [Redis JSON documentation](https://redis.io/docs/redis-json/)
- [Redis client libraries](https://redis.io/docs/clients/)

## Open Questions
- What are the limitations of using Redis compared to traditional databases?
- How does Redis handle data persistence and durability?
- What are the best practices for scaling Redis in large applications?
```
