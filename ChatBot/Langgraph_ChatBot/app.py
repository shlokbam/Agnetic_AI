import os
import time
import uuid
import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI

# Load environment variables
load_dotenv()

# Define the state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Cache the compilation of the LangGraph workflow to prevent re-compilation on every rerun
@st.cache_resource
def get_chatbot(model_name: str):
    # Initialize the memory checkpointer
    checkpointer = MemorySaver()
    
    # Initialize the LLM
    llm = ChatMistralAI(model=model_name, api_key=os.getenv("MISTRAL_API_KEY"))
    
    # Define the core node
    def chat_node(state: ChatState):
        messages = state['messages']
        response = llm.invoke(messages)
        return {'messages': [response]}
        
    # Build the state graph
    builder = StateGraph(ChatState)
    builder.add_node('chat_node', chat_node)
    builder.add_edge(START, 'chat_node')
    builder.add_edge('chat_node', END)
    
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

# App Title & Subtitle
st.title("🤖 Stateful LangGraph Chatbot")
st.markdown("A premium conversational interface demonstrating state preservation and live graph execution tracing.")

# --- Session State Initialization ---
if "active_node" not in st.session_state:
    st.session_state.active_node = None
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ Configuration")

# Model Selection
model_options = ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"]
selected_model = st.sidebar.selectbox("Mistral Model Selection", options=model_options, index=1)

# Compile chatbot graph based on model selection
chatbot = get_chatbot(selected_model)

# Session / Thread Management
st.sidebar.subheader("💬 Session Management")
base_thread_id = st.sidebar.text_input("Thread ID (Conversational Persistence)", value="thread-default")
current_thread_id = f"{base_thread_id}_{st.session_state.reset_counter}"

# Clear current thread session button
if st.sidebar.button("Clear Chat Session", use_container_width=True):
    st.session_state.reset_counter += 1
    st.session_state.active_node = None
    st.rerun()

# --- Live Workflow Execution Render Helper ---
st.sidebar.subheader("⚙️ Workflow Execution")
status_card_placeholder = st.sidebar.empty()

def render_workflow_status(active_node=None):
    start_class = "dot-running" if active_node == "START" else ("dot-success" if active_node in ["chat_node", "END"] else "dot-pending")
    node_class = "dot-running" if active_node == "chat_node" else ("dot-success" if active_node == "END" else "dot-pending")
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
            <span class="status-dot {node_class}"></span>
            <span><b>chat_node</b> (LLM Query)</span>
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
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# --- Message Input & Processing ---
if prompt := st.chat_input("Ask a question..."):
    # Append & Display user's new message
    with st.chat_message("user"):
        st.write(prompt)
        
    # Setup placeholder for dynamic LLM response and status updates
    with st.chat_message("assistant"):
        response_placeholder = st.empty()

    # Step 1: START running
    st.session_state.active_node = "START"
    render_workflow_status("START")
    time.sleep(0.3)  # Small visual delay

    # Step 2: chat_node running
    st.session_state.active_node = "chat_node"
    render_workflow_status("chat_node")
    response_placeholder.markdown("*Thinking...*")

    # Invoke chatbot graph execution
    input_messages = {"messages": [HumanMessage(content=prompt)]}
    
    # We execute and capture the response
    try:
        result = chatbot.invoke(input_messages, config=config)
        response_text = result["messages"][-1].content
        
        # Step 3: END reached
        st.session_state.active_node = "END"
        render_workflow_status("END")
        
        # Typing/streaming animation for the response
        displayed_text = ""
        for char in response_text:
            displayed_text += char
            response_placeholder.markdown(displayed_text + "▌")
            time.sleep(0.005)
        response_placeholder.markdown(displayed_text)
        
    except Exception as e:
        st.session_state.active_node = None
        render_workflow_status(None)
        response_placeholder.error(f"Error during graph execution: {e}")
