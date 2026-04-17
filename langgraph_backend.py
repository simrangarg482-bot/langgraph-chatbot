from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    streaming=True
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

result = chatbot.invoke(
    {"messages": [HumanMessage(content="Hello")]},
    config=config
)

print("AI:", result["messages"][-1].content)

result = chatbot.invoke(
    {"messages": [HumanMessage(content="What did I just say?")]},
    config=config
)

print("AI:", result["messages"][-1].content) 