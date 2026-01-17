from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph_agent.agents import explainer_agent, tools_node


def should_continue(state: dict) -> str:
    messages = state["messages"]
    iteration_count = state.get("iteration_count", 0)

    if iteration_count >= 10:
        raise ValueError("Could not find relevant answer")

    # Check if the last message has tool calls
    if hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
        return "continue"

    return "end"


graph = StateGraph(dict)

graph.add_node("agent", explainer_agent)
graph.add_node("tools", tools_node)

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "agent")

graph.set_entry_point("agent")

agent = graph.compile()
