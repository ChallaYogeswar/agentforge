# src/agents/content_optimizer.py
from typing import Any, Dict, Optional
from dataclasses import dataclass
import re
import time

from src.core.base_agent import BaseAgent, BaseAgentConfig
from src.core.llm import get_llm
from src.core.memory_manager import MemoryManager


def simple_token_count(text: str) -> int:
    if not text:
        return 0
    tokens = re.findall(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]", text)
    return len(tokens)


@dataclass
class QualityScore:
    achievements_signal: float
    metric_density: float
    tailoring_alignment: float
    json_compliance: float
    overall: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "achievements_signal": round(self.achievements_signal, 3),
            "metric_density": round(self.metric_density, 3),
            "tailoring_alignment": round(self.tailoring_alignment, 3),
            "json_compliance": round(self.json_compliance, 3),
            "overall": round(self.overall, 3),
        }


def score_resume_rewrite(input_text: str, output_json_text: str) -> QualityScore:
    """
    STAR-inspired heuristics:
    - Achievements signal: presence of action verbs and impact words
    - Metric density: count of numbers, percentages, KPIs
    - Tailoring alignment: presence of role keywords from input in output
    - JSON compliance: required fields exist and look non-empty
    """
    lower_in = input_text.lower()
    lower_out = output_json_text.lower()

    action_verbs = [
        "led", "built", "designed", "shipped", "delivered", "optimized",
        "architected", "improved", "automated", "launched", "reduced", "increased",
        "enhanced", "streamlined", "developed", "managed"
    ]
    impact_words = ["impact", "resulted", "outcome", "growth", "savings", "revenue", "efficiency"]
    verb_hits = sum(1 for v in action_verbs if v in lower_out)
    impact_hits = sum(1 for w in impact_words if w in lower_out)
    achievements_signal = min(1.0, 0.05 * verb_hits + 0.07 * impact_hits + 0.4)

    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", lower_out)
    percents = re.findall(r"\b\d+(?:\.\d+)?\s*%\b", lower_out)
    metric_density = min(1.0, 0.05 * len(numbers) + 0.1 * len(percents) + 0.3)

    # Extract potential role keywords from input (naive)
    role_keywords = set(re.findall(r"\b(data|ml|machine learning|engineer|developer|product|ai)\b", lower_in))
    alignment_hits = sum(1 for rk in role_keywords if rk in lower_out)
    tailoring_alignment = min(1.0, 0.25 * alignment_hits + 0.4)

    # JSON compliance: required keys present and not trivially empty
    required_keys = ["professional_summary", "experience", "skills", "education", "tailoring_notes"]
    key_hits = sum(1 for k in required_keys if f'"{k}"' in output_json_text)
    json_compliance = 0.2 + 0.15 * key_hits  # baseline

    overall = (achievements_signal + metric_density + tailoring_alignment + json_compliance) / 4.0
    return QualityScore(achievements_signal, metric_density, tailoring_alignment, json_compliance, overall)


class ContentRewriterAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are CareerArchitect, senior resume writer & personal branding expert at AgentForge.

User will provide:
- Their raw career details/resume text OR current resume
- Optionally: a job description/posting/link

Your job:
1. Extract achievements, skills, experience
2. Rewrite every bullet with: Action Verb + Quantifiable Metric + Impact
3. Tailor perfectly to the job description (match keywords exactly but naturally)
4. Output in clean markdown with sections: Professional Summary, Experience, Skills, Education

Output format (strict JSON):

{
  "professional_summary": "...",
  "experience": [...],
  "skills": [...],
  "education": "...",
  "tailoring_notes": "How you adapted it to the job (2-3 bullets)"
}

Make it impossible for recruiters to ignore. Use power words. Be ruthless with weak language.
"""
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id},
        )

        super().__init__(
            agent_id=f"content_rewriter_{user_id}",
            name="CareerArchitect",
            description="Expert resume writer and personal branding specialist",
            capabilities=["resume_writing", "content_optimization", "job_tailoring"],
            config=config,
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the content rewriting task with token counting and quality scoring."""
        start = time.time()
        response = self.run(task, extra_context=context)

        input_tokens = simple_token_count(task)
        output_tokens = simple_token_count(response)
        score = score_resume_rewrite(task, response)
        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "content_optimization",
                "metrics": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                    **score.to_dict(),
                },
            },
        }
