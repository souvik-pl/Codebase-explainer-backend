from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from langgraph_agent.prompts import SYSTEM_PROMPT
from langgraph_agent.tools import all_tools
from utils.contants import LLM_MODEL

load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(model=LLM_MODEL)


def explainer_agent(state: dict) -> dict:
    messages = state["messages"]

    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    llm_with_tools = llm.bind_tools(all_tools)

    response = llm_with_tools.invoke(messages)

    if response is None:
        raise ValueError("Agent didn't return a valid response")

    return {
        "messages": messages + [response],
        "iteration_count": state.get("iteration_count", 0),
    }


def tools_node(state: dict) -> dict:
    tool_node = ToolNode(all_tools)
    tool_result = tool_node.invoke(state)

    # Preserve original messages and add tool results
    original_messages = state["messages"]
    tool_messages = tool_result["messages"]

    iteration_count = state.get("iteration_count", 0) + 1

    return {
        "messages": original_messages + tool_messages,
        "iteration_count": iteration_count,
    }
