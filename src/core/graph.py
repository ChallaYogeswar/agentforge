# src/core/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import AgentState
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage
import operator

from src.agents.prompt_optimizer import PromptOptimizerAgent
from src.agents.content_optimizer import ContentRewriterAgent
from src.agents.email_prioritizer import EmailPrioritizerAgent
from src.core.mcp_interface import tools, tool_map

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.additem]
    next_agent: str

# Initialize agents with tools
prompt_agent = PromptOptimizerAgent()
rewriter_agent = ContentRewriterAgent()
email_agent = EmailPrioritizerAgent()

# Give tools to rewriter (he needs them most)
rewriter_agent.llm = rewriter_agent.llm.bind_tools(tools)

def supervisor_node(state):
    last_message = state["messages"][-1].content
    # Simple but powerful routing logic
    if "resume" in last_message.lower() or "cv" in last_message.lower() or "job" in last_message.lower():
        return "ContentRewriterAgent"
    elif "email" in last_message.lower() or "inbox" in last_message.lower():
        return "EmailPrioritizerAgent"
    else:
        return "PromptOptimizerAgent"

graph = StateGraph(AgentState)

graph.add_node("PromptOptimizerAgent", lambda state: {"messages": [HumanMessage(content=prompt_agent.run(state["messages"][-1].content))]})
graph.add_node("ContentRewriterAgent", lambda state: {"messages": [HumanMessage(content=rewriter_agent.run(state["messages"][-1].content))]})
graph.add_node("EmailPrioritizerAgent", lambda state: {"messages": [HumanMessage(content=email_agent.run(state["messages"][-1].content))]})

graph.set_entry_point("supervisor")
graph.add_conditional_edges("supervisor", supervisor_node)
graph.add_edge("PromptOptimizerAgent", END)
graph.add_edge("ContentRewriterAgent", END)
graph.add_edge("EmailPrioritizerAgent", END)

app = graph.compile()