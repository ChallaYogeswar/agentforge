# src/core/base_agent.py
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.core.llm import get_llm
from src.core.observability import trace_agent_call
from src.core.memory_manager import MemoryManager
from typing import List, Dict, Any

class BaseAgent:
    def __init__(self, name: str, role_instructions: str, user_id: str = "default_user"):
        self.name = name
        self.role_instructions = role_instructions
        self.llm = get_llm()
        self.memory = MemoryManager(user_id)
        
        # Agent Identity (Pillar 1 satisfied)
        self.system_prompt = f"""You are {name}, a specialized AI agent part of AgentForge Productivity Suite.
{role_instructions}

Rules:
- Always stay in character.
- Never reveal you are an AI or break the fourth wall.
- Be helpful, concise, and professional.
- If you need another agent, say exactly: "ROUTING TO: [AgentName]" on a new line.
"""

    def run(self, user_input: str) -> str:
        # Retrieve recent context
        context = self.memory.get_recent_context()

        messages = [SystemMessage(content=self.system_prompt)]
        if context:
            messages.append(SystemMessage(content="Previous conversation:\n" + context))
        messages.append(HumanMessage(content=user_input))

        response = self.llm.invoke(messages).content

        # Log everything beautifully
        trace_agent_call(self.name, user_input, response)

        # Save to memory
        self.memory.add_exchange("human", user_input)
        self.memory.add_exchange("assistant", response)

        return response