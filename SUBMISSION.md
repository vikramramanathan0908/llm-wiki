# WikiMind — Hackathon Submission

## 1. Project Writeup

### Core Idea

WikiMind is an AI-powered knowledge wiki that gets smarter with every question asked.

Instead of retrieving from raw documents at query time (like standard RAG), WikiMind incrementally builds and maintains a **persistent, structured wiki** — exactly as Karpathy described. Every document ingested becomes a structured wiki page. Every question and correction permanently improves the knowledge base.

The system is built on a **two-tier memory architecture**:

```
User question
      │
      ▼
┌─────────────────────────────┐
│  Redis Stack — HOT MEMORY   │  ← SemanticCache + MessageHistory (redisvl)
│  Sub-50ms cache hits        │     Fast, ephemeral, per-session
└──────────────┬──────────────┘
               │ on cache miss
               ▼
┌─────────────────────────────┐
│  Cognee — PERMANENT MEMORY  │  ← Knowledge graph (NetworkX + LanceDB)
│  Entities, relationships,   │     Durable, cross-session, structured
│  embeddings from 17 docs    │
└─────────────────────────────┘
```

**Redis = hot scratchpad** (fast, ephemeral)
**Cognee graph = the wiki** (permanent, structured, queryable)

---

### Self-Improvement Loop

The core loop that makes the wiki smarter:

```
1. INGEST
   Raw docs → LLM generates structured wiki page (Summary, Key Concepts, API Examples)
   → Stored permanently in Cognee knowledge graph
   → Ingestion event logged to Redis session memory

2. QUERY
   Question → redisvl SemanticCache check (cache hit = instant, no LLM call)
   → On miss: Cognee graph recall (semantic search over entities + triplets)
   → Redis MessageHistory adds session context
   → GPT-4o-mini generates grounded answer
   → Answer stored in SemanticCache + MessageHistory

3. SELF-IMPROVE
   User gives feedback/correction on answer
   → GPT-4o-mini rewrites the wiki page incorporating the correction
   → Corrected page saved to disk + Cognee graph permanently
   → SemanticCache updated so next similar question gets the corrected answer
   → Wiki improves — forever

4. LINT
   All wiki pages audited for:
   • Conflicts (contradictory claims between pages)
   • Duplicates (same concept in multiple pages)
   • Stale content (outdated API references)
   • Missing links (pages that should reference each other)
   • Unsupported claims (facts with no source)
   → Issues surfaced with recommendations, applied in one click
```

---

### Redis Usage (for Redis Prize)

| Feature | API | Purpose |
|---------|-----|---------|
| **SemanticCache** | `redisvl.extensions.cache.llm.SemanticCache` | Caches LLM answers by semantic similarity. Similar questions skip the LLM entirely — sub-50ms responses |
| **MessageHistory** | `redisvl.extensions.message_history.MessageHistory` | Per-session conversation history stored in Redis. Included as context in every answer for coherent multi-turn conversations |
| **Redis Stack** | RediSearch module | Powers vector similarity search for SemanticCache |

---

## 2. Codebase Structure

```
llm-wiki/
├── app.py                    ← Streamlit UI (Ask, Audit, Wiki, Knowledge Graph tabs)
├── ingest_all.py             ← One-shot ingestion pipeline
├── fetch_docs.py             ← Scrapes Cognee + Redis official docs
├── generate_graph.py         ← Builds interactive knowledge graph visualization
│
├── core/
│   ├── config.py             ← Environment config
│   ├── memory.py             ← Cognee remember/recall wrappers
│   ├── redis_memory.py       ← redisvl SemanticCache + MessageHistory
│   ├── ingest.py             ← Doc ingestion + wiki page generation
│   ├── query.py              ← Question answering + feedback application
│   └── lint.py               ← Wiki audit (5 check types)
│
├── skills/
│   ├── ingest-doc/SKILL.md   ← Wiki writer skill
│   ├── answer-question/SKILL.md  ← Q&A skill
│   ├── distill-feedback/SKILL.md ← Wiki editor skill
│   └── lint-wiki/SKILL.md    ← Wiki auditor skill
│
├── wiki_pages/
│   ├── Cognee/               ← 9 generated Cognee wiki pages
│   └── Redis/                ← 8 generated Redis wiki pages
│
├── source_docs/              ← 17 scraped official docs
├── graph.html                ← Interactive knowledge graph
└── ARCHITECTURE.md           ← Full technical architecture
```

---

## 3. Evaluation Evidence — Before & After Self-Improvement

### Test Question
> "How does Redis fit into Cognee session memory?"

---

### BEFORE (first answer, before any feedback)

**Answer:**
> Redis fits into Cognee session memory by acting as a hot session scratchpad, where it temporarily stores data for quick retrieval during user sessions. It allows for efficient management of recent conversation contexts through specific session keys, enhancing data retrieval speed and overall performance. Functions like `cognee.remember()` and `cognee.recall()` facilitate the storage and retrieval...

**Issues with this answer:**
- Does not explain the API distinction (`session_id` vs `dataset_name`)
- Does not mention the two-tier architecture explicitly
- Missing: what makes session memory ephemeral vs permanent

---

### FEEDBACK APPLIED

```
User correction: "The answer should explicitly mention that Redis acts as the hot
scratchpad tier, and that cognee.remember(..., session_id=...) routes to Redis
while permanent graph storage uses cognee.remember(..., dataset_name=...)
without session_id."
```

**Wiki page rewritten.** Corrected `Redis/session-cache.md`:

```markdown
# Redis/session-cache

## Summary
Redis serves as the session memory for Cognee, providing a fast, temporary
storage solution for recent conversation contexts while maintaining a durable
knowledge graph for permanent data.

## Key Concepts
- **Session Management**:
  - `cognee.remember(..., session_id="abc")`: Stores data in Redis under the
    specified session key — acting as the hot scratchpad tier (ephemeral)
  - `cognee.remember(..., dataset_name="llm_wiki")`: Stores permanently in
    the Cognee knowledge graph (durable, cross-session)
  - `cognee.recall(..., session_id="abc")`: Searches Redis session first,
    falls through to the permanent graph on miss

- **Two-Tier Architecture**:
  - Redis = hot, fast, ephemeral (sub-millisecond reads)
  - Cognee graph = permanent, structured, cross-session

- **redisvl Integration**:
  - SemanticCache: caches LLM answers by semantic similarity
  - MessageHistory: per-session conversation turns stored in Redis
```

---

### AFTER (second ask, same question — from cache)

**Answer served from:** `Redis SemanticCache` — **0 LLM calls, <50ms**

The corrected answer now correctly explains:
- The `session_id` routing to Redis vs `dataset_name` to the permanent graph
- The two-tier memory architecture
- The ephemeral vs permanent distinction

**The wiki learned.** The correction is now permanent in the Cognee graph and cached in Redis for instant future retrieval.

---

### Lint Evidence

Running the wiki audit detected **6 real issues** across the 17 pages including:

- **Conflicts** between pages on whether session memory is always ephemeral
- **Missing links** between `Cognee/recall.md` and `Redis/session-cache.md`
- **Unsupported claims** in pages referencing specific version behaviors

Each issue includes a recommendation and can be applied in one click from the UI.

---

### Key Metrics

| Metric | Value |
|--------|-------|
| Documents ingested | 17 |
| Wiki pages generated | 17 |
| Knowledge graph nodes | 17+ entities |
| Cache hit latency | <50ms |
| LLM calls on cache hit | 0 |
| Lint issues detected | 6 |
| Self-improvement cycles | Live demo |
