import os
import tempfile
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


def _cognee_root() -> str:
    """Writable root for Cognee DB/files (Streamlit Cloud cannot write to default paths)."""
    root = os.environ.get("COGNEE_DATA_DIR") or os.path.join(
        tempfile.gettempdir(), "wikimind-cognee"
    )
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    return root


async def setup_cognee():
    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    os.environ["LLM_API_KEY"] = key
    os.environ["EMBEDDING_API_KEY"] = key

    root = _cognee_root()
    cognee.config.system_root_directory(root)
    cognee.config.data_root_directory(os.path.join(root, "data"))

    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4o-mini")
    cognee.config.set_llm_api_key(key)
    cognee.config.set_embedding_provider("openai")
    cognee.config.set_embedding_model("text-embedding-3-large")
    cognee.config.set_embedding_api_key(key)
    cognee.config.set_vector_db_provider("lancedb")


async def remember_session(text: str, session_id: str):
    try:
        await cognee.remember(text, session_id=session_id)
    except (PermissionError, OSError) as e:
        print(f"[cognee] session remember skipped (non-fatal): {e}")


async def remember_permanent(text: str, dataset: str = WIKI_DATASET):
    try:
        await cognee.remember(text, dataset_name=dataset)
    except (PermissionError, OSError) as e:
        print(f"[cognee] permanent remember skipped (non-fatal): {e}")


async def recall(query: str, session_id: str = None):
    try:
        if session_id:
            return await cognee.recall(query, session_id=session_id)
        return await cognee.recall(query)
    except (PermissionError, OSError) as e:
        print(f"[cognee] recall skipped (non-fatal): {e}")
        return []
