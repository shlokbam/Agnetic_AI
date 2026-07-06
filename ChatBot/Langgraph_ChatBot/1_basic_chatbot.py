import os
import sqlite3
import requests
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_mistralai import ChatMistralAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

load_dotenv()

# Define the state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Define Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    try:
        r = requests.get(url)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

tools = [search_tool, get_stock_price, calculator]

# Initialize LLM and bind tools
llm = ChatMistralAI(model="mistral-medium-latest", api_key=os.getenv("MISTRAL_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

# Define core LLM node
def chat_node(state: ChatState):
    messages = state['messages']
    print("\n--- DEBUG: Message list sent to Mistral ---")
    for i, m in enumerate(messages):
        print(f"Message {i}: type={type(m).__name__}, content={repr(m.content)}, tool_calls={getattr(m, 'tool_calls', None)}")
    print("-------------------------------------------\n")
    response = llm_with_tools.invoke(messages)
    return {'messages': [response]}

# Set up SQLite database connection for persistent checkpoints
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_history.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

# Build ReAct StateGraph
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")

chatbot = graph.compile(checkpointer=checkpointer)

# Prompt user for Thread ID to resume or start a conversation
print("🤖 Stateful ReAct Chatbot (SQLite Persistence)")
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
        sender = "User" if msg.type == "human" else ("AI" if msg.type == "ai" else f"System ({msg.type})")
        print(f"[{sender}]: {msg.content}")
    print("---------------------------------------------------\n")
else:
    print(f"\n🆕 Starting new conversation thread: '{thread_id}'\n")

seen_tool_calls = set()

try:
    while True:
        user_messages = input("Type here: ")
        print(f"User: {user_messages}")
        if user_messages.strip().lower() == "exit":
            break
        
        intial_state = {'messages': [HumanMessage(content=user_messages)]}
        print("AI: ", end="", flush=True)
        
        seen_tool_calls.clear()
        for chunk, metadata in chatbot.stream(intial_state, config=config, stream_mode="messages"):
            # Check for tool invocation chunks
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                for tc in chunk.tool_calls:
                    tc_id = tc.get("id")
                    if tc_id and tc_id not in seen_tool_calls:
                        seen_tool_calls.add(tc_id)
                        print(f"\n🔧 [Tool Call]: Running `{tc.get('name')}` with args `{tc.get('args')}`...")
            
            # Check for tool return chunks
            if isinstance(chunk, ToolMessage):
                print(f"📥 [Tool Output]: `{chunk.content}`")
                print("AI: ", end="", flush=True)
                
            # Print standard streaming content
            if isinstance(chunk, AIMessage) and chunk.content:
                print(chunk.content, end="", flush=True)
        print()
finally:
    # Close SQLite connection when script exits
    conn.close()
