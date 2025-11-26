"""Lightweight LLM resolver with a safe local fallback.

This module tries to import the production LLM wrappers. If they are not
available in the environment (for example during quick local testing), a
small `StubLLM` is returned that implements a compatible `invoke` method.
"""

from types import SimpleNamespace
from src.utils.config import Config

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.chat_models import ChatOllama
    from langchain_core.language_models import BaseLanguageModel

    def get_llm() -> BaseLanguageModel:
        if not Config.USE_OLLAMA:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=Config.GEMINI_API_KEY,
                temperature=0.7,
                max_tokens=4096,
                streaming=True
            )
        else:
            print("Gemini key not found → falling back to local Ollama (llama3.2)")
            return ChatOllama(model=Config.OLLAMA_MODEL, temperature=0.7)
except Exception:
    # Fallback stub - returns a deterministic canned response so agents can run
    class StubLLM:
        def invoke(self, messages):
            # messages is typically a list with SystemMessage and HumanMessage
            # We'll find the last HumanMessage-like object and echo it
            last_text = None
            try:
                for m in reversed(messages):
                    if hasattr(m, "content"):
                        last_text = m.content
                        break
            except Exception:
                last_text = str(messages)

            resp = f"[stub-llm] I received: {last_text[:500]}"
            return SimpleNamespace(content=resp)

    def get_llm():
        return StubLLM()