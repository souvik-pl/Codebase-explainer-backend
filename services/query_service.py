from langchain_core.messages import HumanMessage, AIMessage

from langgraph_agent.graph import agent


class QueryService:
    def ask_agent(self, query: str) -> str:
        initial_state = {
            "messages": [HumanMessage(content=query)],
        }

        final_state = agent.invoke(initial_state)
        last_message = final_state["messages"][-1]

        if isinstance(last_message, AIMessage):
            html_content = last_message.content
        else:
            html_content = str(last_message)

        return f'<div class="codebase-answer">{html_content}</div>'


query_service = QueryService()
