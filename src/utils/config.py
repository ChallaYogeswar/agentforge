import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # fallback

    # You can switch to Ollama anytime by leaving GEMINI_API_KEY empty
    USE_OLLAMA = GEMINI_API_KEY is None or GEMINI_API_KEY.strip() == ""

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DB_PATH = "data/memory/vector_store"
    SQLITE_DB_PATH = "data/memory/sessions.db"