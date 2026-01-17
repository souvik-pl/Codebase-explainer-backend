from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from langgraph_agent.agents import explainer_agent
from langgraph_agent.tools import all_tools

graph = StateGraph(dict)

graph.add_node("agent", explainer_agent)
graph.add_node("tools", ToolNode(all_tools))

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    lambda state: (
        "continue"
        if hasattr(state["messages"][-1], "tool_calls")
        and state["messages"][-1].tool_calls
        else "end"
    ),
    {
        "continue": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "agent")

agent = graph.compile()
