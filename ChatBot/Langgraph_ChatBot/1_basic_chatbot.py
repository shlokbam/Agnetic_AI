import os
import sqlite3
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_mistralai import ChatMistralAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatMistralAI(model="mistral-medium-latest", api_key=os.getenv("MISTRAL_API_KEY"))

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

# Set up SQLite database connection for persistent checkpoints
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_history.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# Prompt user for Thread ID to resume or start a conversation
print("🤖 Stateful Chatbot (SQLite Persistence)")
thread_id = input("Enter Thread ID to start or resume (default '1'): ").strip()
if not thread_id:
    thread_id = "1"

config = {"configurable": {"thread_id": thread_id}}

# Load and display conversation history if it exists
state = chatbot.get_state(config)
history = state.values.get("messages", [])
if history:
    print(f"\n✨ Found existing history for Thread ID '{thread_id}'. Resuming conversation...")
    for msg in history:
        sender = "User" if msg.type == "human" else "AI"
        print(f"[{sender}]: {msg.content}")
    print("---------------------------------------------------\n")
else:
    print(f"\n🆕 Starting new conversation thread: '{thread_id}'\n")

try:
    while True:
        user_messages = input("Type here: ")
        print(f"User: {user_messages}")
        if user_messages.strip().lower() == "exit":
            break
        
        intial_state = {'messages': [HumanMessage(content=user_messages)]}
        print("AI: ", end="", flush=True)
        for chunk, metadata in chatbot.stream(intial_state, config=config, stream_mode="messages"):
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print()
finally:
    # Close SQLite connection when script exits
    conn.close()
