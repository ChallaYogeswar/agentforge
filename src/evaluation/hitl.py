# src/evaluation/hitl.py
import json

def hitl_feedback(agent_output: str, task: str) -> str:
    print("\n" + "="*80)
    print("🧑‍⚖️ HUMAN-IN-THE-LOOP FEEDBACK REQUIRED")
    print("="*80)
    print(f"TASK: {task}\n")
    print(f"AGENT OUTPUT:\n{agent_output}\n")
    
    rating = input("Rate 1-10 (or press Enter to accept): ").strip()
    feedback = input("Feedback (or Enter to keep): ").strip()
    
    if rating or feedback:
        print("🔥 Feedback recorded. System improving...")
        # In real deployment you'd save this to improve the agent
        with open("data/memory/hitl_feedback.jsonl", "a") as f:
            f.write(json.dumps({"task": task, "output": agent_output, "rating": rating or "10", "feedback": feedback}) + "\n")
        return "Thank you human overlord. Agent will evolve."
    else:
        return "Output accepted as perfect."