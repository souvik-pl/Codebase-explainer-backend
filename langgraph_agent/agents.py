from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

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

    return {"messages": [response]}
