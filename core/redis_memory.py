"""Redis-backed session memory and semantic cache using redisvl."""
import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

try:
    _client = redis.from_url(REDIS_URL, decode_responses=True)
    _client.ping()
    REDIS_AVAILABLE = True
    print("[redis] Connected to Redis Stack ✅")
except Exception as e:
    _client = None
    REDIS_AVAILABLE = False
    print(f"[redis] Not available (non-fatal): {e}")

_session_stores: dict = {}
_semantic_cache = None

def get_semantic_cache():
    global _semantic_cache
    if _semantic_cache is None and REDIS_AVAILABLE:
        try:
            from redisvl.extensions.cache.llm import SemanticCache
            from redisvl.utils.vectorize import OpenAITextVectorizer
            vectorizer = OpenAITextVectorizer(
                model="text-embedding-3-small",
                api_config={"api_key": OPENAI_API_KEY},
            )
            _semantic_cache = SemanticCache(
                name="wiki-llm-cache",
                redis_url=REDIS_URL,
                vectorizer=vectorizer,
                distance_threshold=0.12,
            )
            print("[redisvl] SemanticCache initialized ✅")
        except Exception as e:
            print(f"[redisvl] SemanticCache init failed (non-fatal): {e}")
    return _semantic_cache

def check_cache(question: str) -> str | None:
    """Return cached answer if semantically similar question was asked before."""
    try:
        cache = get_semantic_cache()
        if cache is None:
            return None
        results = cache.check(prompt=question)
        if results:
            print(f"[redisvl] Cache HIT ✅")
            return results[0].get("response")
    except Exception as e:
        print(f"[redisvl] cache check failed (non-fatal): {e}")
    return None

def store_cache(question: str, answer: str):
    """Store a question-answer pair in the semantic cache."""
    try:
        cache = get_semantic_cache()
        if cache is None:
            return
        cache.store(prompt=question, response=answer)
        print(f"[redisvl] Cache stored ✅")
    except Exception as e:
        print(f"[redisvl] cache store failed (non-fatal): {e}")

def get_session_store(session_id: str):
    from redisvl.extensions.message_history import MessageHistory
    if session_id not in _session_stores:
        _session_stores[session_id] = MessageHistory(
            name=f"wiki-session-{session_id[:8]}",
            redis_url=REDIS_URL,
        )
    return _session_stores[session_id]

def add_to_session(session_id: str, question: str, answer: str):
    if not REDIS_AVAILABLE:
        return
    try:
        store = get_session_store(session_id)
        store.add_messages([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
        print(f"[redisvl] Session turn saved ✅")
    except Exception as e:
        print(f"[redisvl] session write failed (non-fatal): {e}")

def get_session_history(session_id: str) -> str:
    if not REDIS_AVAILABLE:
        return ""
    try:
        store = get_session_store(session_id)
        messages = store.get_recent(top_k=6)
        return "\n".join(f"{str(m['role']).split('.')[-1]}: {m['content']}" for m in messages)
    except Exception as e:
        print(f"[redisvl] session read failed (non-fatal): {e}")
        return ""

def get_session_count(session_id: str) -> int:
    if not REDIS_AVAILABLE:
        return 0
    try:
        store = get_session_store(session_id)
        return len(store.get_recent(top_k=100))
    except:
        return 0
