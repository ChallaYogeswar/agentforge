# src/evaluation/llm_judge.py
from src.core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

llm = get_llm()

JUDGE_PROMPT = """
You are the Official Judge of the Google Agents Intensive Capstone 2025.
Rate the following agent output on a scale of 1–10 across 5 criteria. Be extremely harsh — only perfection gets 10.

Task Description:
{task}

Agent Output:
{output}

Rate strictly:

1. Correctness & Accuracy      : /10
2. Structure & Clarity        : /10
3. Creativity & Polish         : /10
4. Adherence to Instructions  : /10
5. Overall Impact              : /10

Total Score: /50

Give a one-sentence justification. If score < 45, explain exactly what to fix.
Respond in JSON only.
"""

def judge_output(task: str, output: str) -> dict:
    response = llm.invoke([
        SystemMessage(content=JUDGE_PROMPT.format(task=task, output=output))
    ]).content
    
    # Clean common markdown
    response = response.strip().strip("```json").strip("```")
    import json
    try:
        return json.loads(response)
    except:
        return {"raw": response, "error": "Judge failed to return valid JSON"}