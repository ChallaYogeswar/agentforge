# src/core/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage
import operator

from src.agents.prompt_optimizer import PromptOptimizerAgent
from src.agents.content_optimizer import ContentRewriterAgent
from src.agents.email_prioritizer import EmailPrioritizerAgent
from src.core.mcp_interface import tools

# ---- Agent State Definition ----
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.additem]
    next_agent: str

# ---- Initialize Agents ----
prompt_agent = PromptOptimizerAgent()
rewriter_agent = ContentRewriterAgent()
email_agent = EmailPrioritizerAgent()

# Bind tools to rewriter agent (he needs them most)
if hasattr(rewriter_agent, "llm"):
    rewriter_agent.llm = rewriter_agent.llm.bind_tools(tools)

# ---- Supervisor Node ----
def supervisor_node(state: AgentState) -> str:
    """Route to the correct agent based on last message content."""
    last_message = state["messages"][-1].content.lower()

    if any(keyword in last_message for keyword in ["resume", "cv", "job"]):
        return "ContentRewriterAgent"
    elif any(keyword in last_message for keyword in ["email", "inbox", "mail"]):
        return "EmailPrioritizerAgent"
    else:
        return "PromptOptimizerAgent"

# ---- Graph Construction ----
graph = StateGraph(AgentState)

# Supervisor node: decides routing
graph.add_node("supervisor", lambda state: {"next_agent": supervisor_node(state)})

# Prompt Optimizer
graph.add_node(
    "PromptOptimizerAgent",
    lambda state: {
        "messages": [
            HumanMessage(content=prompt_agent.run(state["messages"][-1].content))
        ]
    },
)

# Content Rewriter
graph.add_node(
    "ContentRewriterAgent",
    lambda state: {
        "messages": [
            HumanMessage(content=rewriter_agent.run(state["messages"][-1].content))
        ]
    },
)

# Email Prioritizer
graph.add_node(
    "EmailPrioritizerAgent",
    lambda state: {
        "messages": [
            HumanMessage(content=email_agent.run(state["messages"][-1].content))
        ]
    },
)

# ---- Entry Point & Routing ----
graph.set_entry_point("supervisor")

# Conditional edges from supervisor to agents
graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],  # use supervisor_node result
    {
        "PromptOptimizerAgent": "PromptOptimizerAgent",
        "ContentRewriterAgent": "ContentRewriterAgent",
        "EmailPrioritizerAgent": "EmailPrioritizerAgent",
    },
)

# End edges
graph.add_edge("PromptOptimizerAgent", END)
graph.add_edge("ContentRewriterAgent", END)
graph.add_edge("EmailPrioritizerAgent", END)

# ---- Compile App ----
app = graph.compile()

# ---- Integration Helper ----
def run_agent_pipeline(user_input: str):
    """Unified entry point for main system integration."""
    initial_state: AgentState = {"messages": [HumanMessage(content=user_input)], "next_agent": ""}
    result_state = app.invoke(initial_state)
    return result_state["messages"][-1].content
