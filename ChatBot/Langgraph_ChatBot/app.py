import os
import time
import uuid
import sqlite3
import requests
import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Define the state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Fetch existing thread IDs from SQLite database
def get_existing_threads():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_history.db")
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return sorted(threads)
    except Exception:
        return []

# Delete a specific thread and its checkpoints/writes from the database
def delete_thread_from_db(thread_id: str):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_history.db")
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_chatbot(model_name: str, checkpointer):
    # Initialize Tools
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
    
    # Initialize the LLM and bind tools
    llm = ChatMistralAI(model=model_name, api_key=os.getenv("MISTRAL_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the core node
    def chat_node(state: ChatState):
        messages = state['messages']
        response = llm_with_tools.invoke(messages)
        return {'messages': [response]}
        
    # Build the state graph
    builder = StateGraph(ChatState)
    builder.add_node('chat', chat_node)
    builder.add_node('tools', ToolNode(tools))
    
    builder.add_edge(START, 'chat')
    builder.add_conditional_edges('chat', tools_condition)
    builder.add_edge('tools', 'chat')
    
    # Compile the graph
    return builder.compile(checkpointer=checkpointer)

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Dynamic active node indicator styling */
    .status-card {
        padding: 1.2rem;
        border-radius: 12px;
        background-color: #1e293b;
        border: 1px solid #334155;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .status-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    .status-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    .dot-pending { background-color: #64748b; }
    .dot-running { background-color: #3b82f6; box-shadow: 0 0 8px #3b82f6; animation: pulse 1.5s infinite; }
    .dot-success { background-color: #10b981; }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Check if running in a virtual environment
import sys
in_venv = (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
if not in_venv:
    st.warning("⚠️ **Warning**: You are running Streamlit outside the virtual environment (`.venv`). This uses outdated system packages (e.g. langchain-core 0.3.x) which cause duplicate tool-calling bugs. Please stop this server and run: `.venv/bin/streamlit run ChatBot/Langgraph_ChatBot/app.py` instead.")

# --- Session State Initialization ---
if "active_node" not in st.session_state:
    st.session_state.active_node = None
if "selected_session" not in st.session_state:
    st.session_state.selected_session = "🆕 Create New Session"
if "new_session_name" not in st.session_state:
    st.session_state.new_session_name = f"session-{uuid.uuid4().hex[:4]}"

# --- Sidebar Title ---
st.sidebar.title("🤖 Chat Controls")

# Hardcoded Model Selection
selected_model = "mistral-medium-latest"

# Compile chatbot graph based on model selection
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_history.db")
with SqliteSaver.from_conn_string(db_path) as checkpointer:
    chatbot = get_chatbot(selected_model, checkpointer)

    # --- Sidebar Saved Sessions ---
    st.sidebar.subheader("📁 Saved Sessions")

    # Fetch unique thread IDs from SQLite db to populate scrollbar list
    existing_threads = get_existing_threads()

    # Scrollable container for sessions list (inside sidebar, height set to 300)
    with st.sidebar.container(height=300):
        # "Create New Session" Option
        is_new_active = (st.session_state.selected_session == "🆕 Create New Session")
        if st.button("➕ New Session", use_container_width=True, type="primary" if is_new_active else "secondary"):
            st.session_state.selected_session = "🆕 Create New Session"
            # Generate a new unique ID so the user starts with a completely fresh, empty chat
            st.session_state.new_session_name = f"session-{uuid.uuid4().hex[:4]}"
            st.session_state.active_node = None
            st.rerun()
            
        st.markdown("<div style='margin: 8px 0; border-top: 1px dashed #475569;'></div>", unsafe_allow_html=True)
        
        # List all saved sessions with a side delete button
        for session in existing_threads:
            is_active = (st.session_state.selected_session == session)
            
            # Grid columns inside sidebar for thread buttons and delete button
            row_col1, row_col2 = st.columns([4, 1.2])
            with row_col1:
                btn_label = f"💬 {session}"
                if is_active:
                    btn_label = f"👉 {session}"
                if st.button(btn_label, key=f"session_btn_{session}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state.selected_session = session
                    st.session_state.active_node = None
                    st.rerun()
            with row_col2:
                if st.button("🗑️", key=f"del_{session}", use_container_width=True, help=f"Delete thread {session}"):
                    delete_thread_from_db(session)
                    if st.session_state.selected_session == session:
                        st.session_state.selected_session = "🆕 Create New Session"
                        st.session_state.new_session_name = f"session-{uuid.uuid4().hex[:4]}"
                        st.session_state.active_node = None
                    st.rerun()
                
    if st.session_state.selected_session == "🆕 Create New Session":
        base_thread_id = st.sidebar.text_input("Enter Session ID", value=st.session_state.new_session_name)
        current_thread_id = base_thread_id
    else:
        current_thread_id = st.session_state.selected_session
        st.sidebar.info(f"Resuming: `{current_thread_id}`")

    # --- Live Workflow Execution Render Helper ---
    st.sidebar.subheader("⚙️ Workflow Execution")
    status_card_placeholder = st.sidebar.empty()

    def render_workflow_status(active_node=None):
        start_class = "dot-running" if active_node == "START" else ("dot-success" if active_node in ["chat", "tools", "END"] else "dot-pending")
        chat_class = "dot-running" if active_node == "chat" else ("dot-success" if active_node in ["tools", "END"] else "dot-pending")
        tools_class = "dot-running" if active_node == "tools" else ("dot-success" if active_node == "END" else "dot-pending")
        end_class = "dot-success" if active_node == "END" else "dot-pending"
        
        status_card_placeholder.markdown(f"""
        <div class="status-card">
            <h5 style="margin-top:0;margin-bottom:0.8rem;color:#94a3b8;">Active Node Status</h5>
            <div class="status-item">
                <span class="status-dot {start_class}"></span>
                <span><b>START</b></span>
            </div>
            <div style="height: 15px; border-left: 2px dashed #475569; margin-left: 5px; margin-bottom: 5px;"></div>
            <div class="status-item">
                <span class="status-dot {chat_class}"></span>
                <span><b>chat</b> (LLM Query)</span>
            </div>
            <div style="height: 15px; border-left: 2px dashed #475569; margin-left: 5px; margin-bottom: 5px;"></div>
            <div class="status-item">
                <span class="status-dot {tools_class}"></span>
                <span><b>tools</b> (Tool Node execution)</span>
            </div>
            <div style="height: 15px; border-left: 2px dashed #475569; margin-left: 5px; margin-bottom: 5px;"></div>
            <div class="status-item">
                <span class="status-dot {end_class}"></span>
                <span><b>END</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_workflow_status(st.session_state.active_node)

    # --- Main Layout ---
    config = {"configurable": {"thread_id": current_thread_id}}

    st.subheader("💬 Chat Window")

    # Retrieve existing state and history from the checkpointer
    state = chatbot.get_state(config)
    messages = state.values.get("messages", [])

    # Render all historical messages
    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, ToolMessage):
            st.success(f"✅ **Tool Output**: `{msg.content}`")
        elif isinstance(msg, AIMessage):
            # Render any tool calls that are stored in the historical AIMessage
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    st.info(f"🔧 **Tool Call**: Running `{tc['name']}` with arguments `{tc['args']}`...")
            # Render the text content if it exists
            if msg.content:
                with st.chat_message("assistant"):
                    st.write(msg.content)

    # --- Message Input & Processing ---
    if prompt := st.chat_input("Ask a question..."):
        # Append & Display user's new message
        with st.chat_message("user"):
            st.write(prompt)
            
        # Setup placeholder for dynamic LLM response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

        # Step 1: START running
        st.session_state.active_node = "START"
        render_workflow_status("START")
        time.sleep(0.3)  # Small visual delay

        # Step 2: chat running
        st.session_state.active_node = "chat"
        render_workflow_status("chat")
        response_placeholder.markdown("*Thinking...*")

        # Invoke chatbot graph execution with messages stream mode
        input_messages = {"messages": [HumanMessage(content=prompt)]}
        
        # We execute and capture the response chunks in real-time
        try:
            displayed_text = ""
            seen_tool_calls = set()
            
            # stream_mode="messages" streams token chunks from the Chat model
            for chunk, metadata in chatbot.stream(input_messages, config=config, stream_mode="messages"):
                # Dynamically update the active node in the workflow visualizer
                node = metadata.get("langgraph_node")
                if node and st.session_state.active_node != node:
                    st.session_state.active_node = node
                    render_workflow_status(node)
                
                # Check for tool invocation chunks
                if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                    for tc in chunk.tool_calls:
                        tc_id = tc.get("id")
                        if tc_id and tc_id not in seen_tool_calls:
                            seen_tool_calls.add(tc_id)
                            tool_name = tc.get("name")
                            tool_args = tc.get("args")
                            st.info(f"🔧 **Tool Call**: Running `{tool_name}` with arguments `{tool_args}`...")
                
                # Check for tool return chunks
                if isinstance(chunk, ToolMessage):
                    st.success(f"✅ **Tool Output**: `{chunk.content}`")
                    # Reset response placeholder for next text chunks
                    with st.chat_message("assistant"):
                        response_placeholder = st.empty()
                    displayed_text = ""
                    
                # Print standard streaming content
                if isinstance(chunk, AIMessage) and chunk.content:
                    displayed_text += chunk.content
                    # Update response
                    response_placeholder.markdown(displayed_text + "▌")
            
            # Step 3: END reached
            st.session_state.active_node = "END"
            render_workflow_status("END")
            if displayed_text:
                response_placeholder.markdown(displayed_text)
            
        except Exception as e:
            st.session_state.active_node = None
            render_workflow_status(None)
            response_placeholder.error(f"Error during graph execution: {e}")
