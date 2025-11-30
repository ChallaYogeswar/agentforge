# src/agents/email_prioritizer.py
from typing import Any, Dict, Optional, List
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
    triage_accuracy_signal: float
    urgency_consistency: float
    category_precision: float
    json_validity: float
    overall: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "triage_accuracy_signal": round(self.triage_accuracy_signal, 3),
            "urgency_consistency": round(self.urgency_consistency, 3),
            "category_precision": round(self.category_precision, 3),
            "json_validity": round(self.json_validity, 3),
            "overall": round(self.overall, 3),
        }


def score_email_prioritization(input_text: str, output_json_text: str) -> QualityScore:
    """
    Heuristics for email triage:
    - triage_accuracy_signal: detection of sender/subject/urgency fields
    - urgency_consistency: presence and plausible range (1–10)
    - category_precision: presence of known categories
    - json_validity: array structure with objects and prioritized action list mention
    """
    lo = output_json_text.lower()

    triage_fields = sum(1 for k in ["sender", "subject", "urgency_score", "category", "recommended_action"] if f'"{k}"' in output_json_text)
    triage_accuracy_signal = min(1.0, 0.15 * triage_fields + 0.4)

    # Urgency values plausibility
    urgencies = [int(x) for x in re.findall(r'"urgency_score"\s*:\s*(\d+)', output_json_text)]
    if not urgencies:
        urgency_consistency = 0.5
    else:
        valid = [u for u in urgencies if 1 <= u <= 10]
        urgency_consistency = 0.5 + 0.05 * len(valid)
        urgency_consistency = min(1.0, urgency_consistency)

    known_cats = ["sales", "hr", "finance", "spam", "newsletter", "support", "legal", "product"]
    cat_hits = sum(1 for c in known_cats if f'"{c}"' in lo)
    category_precision = min(1.0, 0.1 * cat_hits + 0.4)

    json_array_signal = 1 if re.search(r"^\s*\[", output_json_text) else 0
    action_list_signal = 1 if "do these first" in lo or "prioritized action list" in lo else 0
    json_validity = 0.4 + 0.3 * json_array_signal + 0.2 * action_list_signal

    overall = (triage_accuracy_signal + urgency_consistency + category_precision + json_validity) / 4.0
    return QualityScore(triage_accuracy_signal, urgency_consistency, category_precision, json_validity, overall)


class EmailPrioritizerAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are InboxCommander, elite email triage specialist in AgentForge.

User will paste one or multiple emails (separated by --- or numbered).

For each email you analyze:
- Sender importance
- Urgency (deadline, action required, opportunity cost)
- Topic category
- Required response time

Output strict JSON array of objects:

[
  {
    "email_id": 1,
    "sender": "...",
    "subject": "...",
    "urgency_score": 1-10,
    "category": "Sales/HR/Finance/Spam/Newsletter/etc",
    "recommended_action": "Reply within 1h / Delegate / Archive / Reply EOD",
    "one_line_summary": "...",
    "suggested_reply_draft": "Optional short draft if urgency >= 8"
  }
]

Then at the end, give a prioritized action list: "Do these first: #3, #1, #5"

Be cold-blooded. Most emails are trash.
"""
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id},
        )

        super().__init__(
            agent_id=f"email_prioritizer_{user_id}",
            name="InboxCommander",
            description="Elite email triage and prioritization specialist",
            capabilities=["email_prioritization", "urgency_analysis", "inbox_management"],
            config=config,
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the email prioritization task with token counting and quality scoring."""
        start = time.time()
        response = self.run(task, extra_context=context)

        input_tokens = simple_token_count(task)
        output_tokens = simple_token_count(response)
        score = score_email_prioritization(task, response)
        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "email_prioritization",
                "metrics": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                    **score.to_dict(),
                },
            },
        }
