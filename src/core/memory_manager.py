"""Memory manager with an optional ChromaDB-backed store.

If `chromadb` and `sentence-transformers` are available they will be used
for semantic storage; otherwise the module falls back to SQLite-only with a
tiny in-memory collection for semantic operations so the app remains
functional for local testing.
"""

import sqlite3
import json
from datetime import datetime
from src.utils.config import Config

try:
    from chromadb import PersistentClient
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    _HAVE_CHROMA = True
except Exception:
    _HAVE_CHROMA = False


class _InMemoryCollection:
    def __init__(self):
        self._docs = []

    def add(self, documents, metadatas=None, ids=None):
        for i, doc in enumerate(documents):
            self._docs.append({
                "id": ids[i] if ids else str(len(self._docs)),
                "document": doc,
                "metadata": (metadatas[i] if metadatas else {})
            })

    def query(self, query_texts=None, n_results=5, include=None):
        # Very naive: return most recent documents
        docs = [d["document"] for d in self._docs][-n_results:][::-1]
        return {"documents": [docs], "metadatas": [[d["metadata"] for d in self._docs][-n_results:][::-1]]}


class MemoryManager:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

        # SQLite for session & long-term memory
        self.conn = sqlite3.connect(Config.SQLITE_DB_PATH, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()

        # ChromaDB for semantic long-term memory (optional)
        if _HAVE_CHROMA:
            try:
                self.chroma = PersistentClient(path=Config.VECTOR_DB_PATH)
                self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name=Config.EMBEDDING_MODEL)
                self.collection = self.chroma.get_or_create_collection(
                    name="long_term_memory",
                    embedding_function=self.embedding_fn
                )
            except Exception:
                # Something failed during chroma setup; fall back
                self.collection = _InMemoryCollection()
        else:
            self.collection = _InMemoryCollection()

    def add_exchange(self, role: str, content: str):
        self.conn.execute(
            "INSERT INTO conversations (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (self.user_id, role, content, datetime.now().isoformat())
        )
        self.conn.commit()

        # Also store in vector DB (or in-memory fallback)
        try:
            self.collection.add(
                documents=[content],
                metadatas=[{"role": role, "user_id": self.user_id, "timestamp": datetime.now().isoformat()}],
                ids=[f"{self.user_id}_{datetime.now().timestamp()}"]
            )
        except Exception:
            # swallow errors for environments without chroma
            pass

    def get_recent_context(self, limit: int = 8) -> str:
        cursor = self.conn.execute(
            "SELECT role, content FROM conversations WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (self.user_id, limit)
        )
        rows = cursor.fetchall()[::-1]  # reverse to chronological
        return "\n".join([f"{role.capitalize()}: {content}" for role, content in rows])

    def semantic_search(self, query: str, n_results: int = 5):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas"]
            )
            return results["documents"][0] if results.get("documents") else []
        except Exception:
            return []