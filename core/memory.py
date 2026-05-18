import os
from dotenv import load_dotenv

load_dotenv()

# Set env vars BEFORE importing cognee so it picks them up at init time
_api_key = os.environ.get("OPENAI_API_KEY", "")
os.environ["LLM_API_KEY"] = _api_key
os.environ["EMBEDDING_API_KEY"] = _api_key
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "gpt-4o-mini"
os.environ["EMBEDDING_PROVIDER"] = "openai"
os.environ["EMBEDDING_MODEL"] = "text-embedding-3-large"

import cognee
from core.config import WIKI_DATASET, SOURCE_DATASET

async def setup_cognee():
    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    os.environ["LLM_API_KEY"] = key
    os.environ["EMBEDDING_API_KEY"] = key
    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4o-mini")
    cognee.config.set_llm_api_key(key)
    cognee.config.set_embedding_provider("openai")
    cognee.config.set_embedding_model("text-embedding-3-large")
    cognee.config.set_embedding_api_key(key)
    cognee.config.set_vector_db_provider("lancedb")

async def remember_session(text: str, session_id: str):
    await cognee.remember(text, session_id=session_id)

async def remember_permanent(text: str, dataset: str = WIKI_DATASET):
    await cognee.remember(text, dataset_name=dataset)

async def recall(query: str, session_id: str = None):
    if session_id:
        return await cognee.recall(query, session_id=session_id)
    return await cognee.recall(query)
