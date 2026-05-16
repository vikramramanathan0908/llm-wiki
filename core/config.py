import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

WIKI_DATASET = "llm_wiki"
SOURCE_DATASET = "source_docs"
