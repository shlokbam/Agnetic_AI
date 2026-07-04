import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_mistralai import ChatMistralAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatMistralAI(model="mistral-medium-latest", api_key=os.getenv("MISTRAL_API_KEY"))

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

checkpointer = MemorySaver()

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

intial_state = {'messages': [HumanMessage(content="What is the square root of 16?")]}

result = chatbot.invoke(intial_state, config=config)
print(f"AI: {result['messages'][-1].content}")

while True:
    user_messages = input("Type here: ")
    print(f"User: {user_messages}")
    if user_messages.strip().lower() == "exit":
        break
    
    intial_state = {'messages': [HumanMessage(content=user_messages)]}
    result = chatbot.invoke(intial_state, config=config)
    print(f"AI: {result['messages'][-1].content}")
