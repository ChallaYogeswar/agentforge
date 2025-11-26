# src/core/intent_router.py
from src.core.llm import get_llm
from sentence_transformers import SentenceTransformer, util
import numpy as np
import logging


class IntentRouter:
    def __init__(self):
        self.llm = get_llm()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # Prefer structlog when available, but fall back to stdlib logging
        try:
            import structlog

            self.log = structlog.get_logger()
        except Exception:
            self.log = logging.getLogger("agentforge.intent_router")

        self.routes = {
            "optimize prompt": "PromptOptimizerAgent",
            "improve prompt": "PromptOptimizerAgent",
            "better prompt": "PromptOptimizerAgent",
            "rewrite prompt": "PromptOptimizerAgent",

            "resume": "ContentRewriterAgent",
            "cv": "ContentRewriterAgent",
            "linkedin": "ContentRewriterAgent",
            "job description": "ContentRewriterAgent",
            "tailor resume": "ContentRewriterAgent",

            "email": "EmailPrioritizerAgent",
            "inbox": "EmailPrioritizerAgent",
            "prioritize": "EmailPrioritizerAgent",
            "urgent": "EmailPrioritizerAgent",
        }

        self.route_embeddings = self.encoder.encode(list(self.routes.keys()), convert_to_tensor=True)

    def route(self, user_input: str) -> str:
        # First try semantic search
        input_emb = self.encoder.encode(user_input, convert_to_tensor=True)
        scores = util.cos_sim(input_emb, self.route_embeddings)[0]

        if scores.max() > 0.45:  # confident match
            best_idx = int(np.argmax(scores))
            keys = list(self.routes.keys())
            target = self.routes[keys[best_idx]]
            try:
                self.log.info("intent.routing", method="semantic", confidence=float(scores.max()), target=target)
            except Exception:
                # logging backends may have different APIs
                try:
                    self.log.info(f"intent.routing semantic target={target} confidence={float(scores.max())}")
                except Exception:
                    pass
            return target

        # Fallback to LLM
        prompt = f"""
Given this user request, which agent should handle it?

Options:
- PromptOptimizerAgent
- ContentRewriterAgent
- EmailPrioritizerAgent

User: {user_input}

Respond with ONLY the agent name.
"""
        # Some LLM wrappers accept a string; others expect messages. We'll pass
        # the prompt as-is and let the LLM implementation handle it.
        try:
            response = self.llm.invoke(prompt).content.strip()
        except Exception:
            # If invoke fails (different signature), fall back to str()
            try:
                response = str(self.llm.invoke(prompt)).strip()
            except Exception:
                response = "PromptOptimizerAgent"

        try:
            self.log.info("intent.routing", method="llm_fallback", target=response)
        except Exception:
            try:
                self.log.info(f"intent.routing llm_fallback target={response}")
            except Exception:
                pass

        return response