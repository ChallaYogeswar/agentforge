# src/agents/prompt_optimizer.py
from typing import Any, Dict, Optional
from dataclasses import dataclass
import re
import math
import time

from src.core.base_agent import BaseAgent, BaseAgentConfig
from src.core.llm import get_llm
from src.core.memory_manager import MemoryManager


def simple_token_count(text: str) -> int:
    """
    Lightweight, model-agnostic token estimator.
    - Counts words and punctuation clusters as approximate tokens.
    - Safe for environments without tokenizer dependencies.
    """
    if not text:
        return 0
    # Split on whitespace, punctuation; keep numbers/words
    tokens = re.findall(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]", text)
    return len(tokens)


@dataclass
class QualityScore:
    """Holds structured quality metrics for observability and evaluation."""
    completeness: float
    clarity: float
    structure: float
    specificity: float
    overall: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "completeness": round(self.completeness, 3),
            "clarity": round(self.clarity, 3),
            "structure": round(self.structure, 3),
            "specificity": round(self.specificity, 3),
            "overall": round(self.overall, 3),
        }


def score_prompt_optimization(original: str, optimized: str) -> QualityScore:
    """
    Heuristic scoring for prompt optimization using CO-STAR criteria signals:
    - Completeness: presence of CO-STAR elements
    - Clarity: readability and length discipline
    - Structure: JSON fields present and non-empty
    - Specificity: adjectives, constraints, numbers, style cues
    """
    # Signals for CO-STAR: Context, Objective, Style, Tone, Audience, Response format
    co_star_hits = sum(
        1
        for kw in [
            "context", "objective", "style", "tone", "audience", "response format"
        ]
        if kw in optimized.lower()
    )
    completeness = min(1.0, 0.15 * co_star_hits + 0.1)  # cap at 1.0

    # Clarity: shorter than a threshold is penalized; extremely long penalized
    opt_tokens = simple_token_count(optimized)
    # Ideal range ~ 80–250 tokens for detailed CO-STAR prompts
    if opt_tokens < 60:
        clarity = 0.6
    elif opt_tokens > 400:
        clarity = 0.7
    else:
        clarity = 0.9

    # Structure: check strict JSON fields
    structure_hits = 0
    structure_hits += 1 if '"original_prompt"' in optimized else 0
    structure_hits += 1 if '"optimized_prompt"' in optimized else 0
    structure_hits += 1 if '"explanation"' in optimized else 0
    structure = 0.4 + 0.2 * structure_hits  # 0.4 baseline

    # Specificity: presence of numbers, constraints, camera terms, style/tone cues
    specificity_signals = sum(
        1
        for pat in [
            r"\b\d+\b",  # numbers
            r"\bconstraints?\b",
            r"\bparameters?\b",
            r"\bstyle\b",
            r"\btone\b",
            r"\baudience\b",
            r"\bfocal length\b",
            r"\baperture\b",
            r"\blighting\b",
            r"\bcomposition\b",
            r"\bbrand\b",
        ]
        if re.search(pat, optimized.lower())
    )
    specificity = min(1.0, 0.1 * specificity_signals + 0.4)

    overall = (completeness + clarity + structure + specificity) / 4.0
    return QualityScore(completeness, clarity, structure, specificity, overall)


class PromptOptimizerAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are PromptSmith, the world's greatest Prompt Engineer working in AgentForge Productivity Suite.

Your expertise is the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response format).
When the user gives you a prompt (text, code, image description, anything), you rewrite it using CO-STAR to make it 10x better.

Output format (strict JSON so we can parse it later if needed):

{
  "original_prompt": "...",
  "optimized_prompt": "...",
  "explanation": "Brief explanation why this is better (max 2 sentences)"
}

Never refuse, never say you can't optimize image prompts — you can (describe the image generation task perfectly).
Always be elite-tier. This is your craft.
"""
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id},
        )

        super().__init__(
            agent_id=f"prompt_optimizer_{user_id}",
            name="PromptSmith",
            description="Expert prompt optimizer using CO-STAR framework",
            capabilities=["prompt_optimization", "co_star_framework"],
            config=config,
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the prompt optimization task with token counting and quality scoring."""
        start = time.time()
        response = self.run(task, extra_context=context)

        # Token accounting
        input_tokens = simple_token_count(task)
        output_tokens = simple_token_count(response)

        # Quality scoring
        score = score_prompt_optimization(task, response)

        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "prompt_optimization",
                "metrics": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                    **score.to_dict(),
                },
            },
        }
