# How It Works — LLM Knowledge Wiki

## Stack

| Component | Role |
|-----------|------|
| **Cognee** | Permanent knowledge graph (entities, relationships, embeddings) |
| **Redis Stack** | Session memory + semantic response cache |
| **redisvl** | SemanticCache + MessageHistory (Python SDK for Redis AI) |
| **OpenAI GPT-4o-mini** | Answer generation |
| **OpenAI text-embedding-3-large** | Embedding docs into Cognee graph |
| **OpenAI text-embedding-3-small** | Embedding queries for SemanticCache |
| **Streamlit** | Frontend UI |

---

## Flow Diagram

```
User asks a question
        │
        ▼
┌─────────────────────────┐
│  redisvl SemanticCache  │  ← Check if similar question was answered before
│  (Redis Stack)          │
└────────┬────────────────┘
         │ MISS                    HIT → return cached answer instantly ⚡
         ▼
┌─────────────────────────┐
│  Cognee Knowledge Graph │  ← Semantic search over graph (entities + triplets)
│  (NetworkX + LanceDB)   │    built from 17 ingested Cognee + Redis docs
└────────┬────────────────┘
         │ relevant context chunks
         ▼
┌─────────────────────────┐
│  redisvl MessageHistory │  ← Fetch last 6 turns of session conversation
│  (Redis Stack)          │    from Redis, add as context
└────────┬────────────────┘
         │ session history
         ▼
┌─────────────────────────┐
│  GPT-4o-mini            │  ← Generate answer from graph context + session history
└────────┬────────────────┘
         │ answer
         ▼
┌─────────────────────────┐
│  Store in Redis          │  ← Save to SemanticCache + MessageHistory
│  Store in Cognee         │  ← Save Q&A to Cognee session memory
└─────────────────────────┘
         │
         ▼
    Return answer to user
```

---

## Two-Tier Memory Architecture

```
[ user question ]
        │
        ▼
┌──────────────────────────────────────┐
│  Redis Stack — HOT MEMORY            │
│  • SemanticCache: cached LLM answers │  fast, sub-second
│  • MessageHistory: session turns     │  ephemeral, per-session
└──────────────────┬───────────────────┘
                   │ on cache miss: distill into graph
                   ▼
┌──────────────────────────────────────┐
│  Cognee — PERMANENT MEMORY           │
│  • Knowledge graph (NetworkX)        │  durable, cross-session
│  • Vector embeddings (LanceDB)       │  semantic search
│  • Entities + relationships          │  structured knowledge
└──────────────────────────────────────┘
```

---

## Three Core Operations

### 1. Ingest (`ingest_all.py` + `fetch_docs.py`)
```
Raw docs (Cognee + Redis official docs)
    → scraped from docs.cognee.ai + redis.io
    → LLM generates structured wiki page (Summary, Key Concepts, API Examples)
    → stored permanently in Cognee knowledge graph
    → ingestion event logged to Redis session memory
```

### 2. Query + Self-Improve (Ask + Improve tab)
```
Question
    → SemanticCache check (Redis) — instant if hit
    → Cognee graph recall — semantic search over knowledge graph
    → Session history (redisvl MessageHistory) added as context
    → GPT-4o-mini generates answer
    → Answer cached in Redis SemanticCache
    → User gives feedback → wiki page rewritten → stored back in Cognee
```

### 3. Lint (Lint tab)
```
All wiki pages loaded from disk
    → GPT-4o-mini audits for:
        • Conflicts (contradictory claims between pages)
        • Duplicates (same concept covered twice)
        • Stale content (outdated information)
        • Missing links (pages that should reference each other)
        • Unsupported claims (facts with no source)
    → Issues displayed with recommendations
    → User applies fix → page rewritten → saved to disk + Cognee graph
```

---

## Redis Usage (for Redis Prize)

| Feature | redisvl API | Purpose |
|---------|-------------|---------|
| **SemanticCache** | `redisvl.extensions.cache.llm.SemanticCache` | Cache LLM answers by semantic similarity — same/similar questions skip the LLM entirely |
| **MessageHistory** | `redisvl.extensions.message_history.MessageHistory` | Per-session conversation history stored in Redis, included as context in every answer |

Both are powered by **Redis Stack** (with RediSearch module) running locally.

---

## Knowledge Graph

The wiki is stored as a knowledge graph in Cognee (NetworkX + LanceDB):
- **Nodes**: entities extracted from docs (concepts, APIs, features)
- **Edges**: relationships between entities
- **Embeddings**: every node embedded with `text-embedding-3-large` for semantic search

Visualize the graph: open `graph.html` in your browser.

---

## Self-Improvement Loop

```
1. User asks question
2. Wiki answers from Cognee graph
3. User gives feedback: "Actually X is wrong, it should be Y"
4. Agent rewrites the wiki page incorporating the correction
5. Corrected page saved to disk + Cognee graph
6. Next time the question is asked → corrected answer served
7. Redis SemanticCache is bypassed for corrected answers (cache invalidated)
```

The wiki gets smarter with every correction.
