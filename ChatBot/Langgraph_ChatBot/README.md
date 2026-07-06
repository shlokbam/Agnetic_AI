# 🤖 LangGraph Basic Chatbot & Streamlit Web App

This directory contains a stateful chatbot built with **LangGraph** and **LangChain (Mistral AI)**, including both a CLI version and a premium **Streamlit** web application with a live-rendering workflow graph.

---

## 📂 Directory Contents

- **[1_basic_chatbot.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/1_basic_chatbot.py)**: The terminal-based ReAct chatbot script. It uses `SqliteSaver` to persist conversation history and dynamically prints tool calls and inputs to stdout.
- **[app.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/app.py)**: A premium web application built with Streamlit. It provides a visual chat canvas, session control widgets (saving, resuming, and deleting individual threads from the database), and tracks/highlights the active graph execution state (`START` -> `chat` -> `tools` -> `END`) live on screen.
- **[tool.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/tool.py)**: Validation script to test tool operations.
- **[requirements.txt](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/requirements.txt)**: Localized requirements for the chatbot.

---

## 🛠️ Key Features

### 1. ReAct Tool Loop Execution
The chatbot is bound to three tools:
- **DuckDuckGo Search**: Fetches real-time web context.
- **Calculator**: Performs exact basic arithmetic calculations (`add`, `sub`, `mul`, `div`).
- **Stock Price**: Fetches live stock quotes using Alpha Vantage (automatically fallback from NSE `.NS` to BSE `.BO` if quotes are empty).

If the model generates a tool call, the LangGraph workflow dynamically routes the state to the `tools` node, executes the tool, and routes back to `chat` for final summarization.

### 2. Thread-Safe Persistent Memory
The chatbot maintains history across sessions using SQLite checkpointing (`SqliteSaver.from_conn_string`). You can enter a custom session name or delete individual threads dynamically.

### 3. Live Tracing & Visual Progress Indicators
The Streamlit app displays:
- **Active Node status**: Glowing indicators in the sidebar tracing the active execution state (`START`, `chat`, `tools`, `END`).
- **Tool Invocations**: Blue status containers detailing the tool name and arguments.
- **Tool Outputs**: Green status containers displaying the returned results.

---

## 🚀 How to Run

### 1. Environment Activation
To prevent runtime errors, ensure that you have your virtual environment active:
```bash
source .venv/bin/activate
```

### 2. Run the Streamlit Web Application
Run the Streamlit application using the environment executable to avoid system python package mismatches:
```bash
.venv/bin/streamlit run ChatBot/Langgraph_ChatBot/app.py
```
> [!WARNING]
> Do NOT run `streamlit run app.py` globally if it resolves to a python environment other than `.venv`. Running Streamlit globally with outdated langchain-core/langchain-mistralai versions (e.g. 0.3.x) will cause duplicate tool call ID bugs.

Once launched, navigate to `http://localhost:8501`.

### 3. Run the CLI Chatbot
```bash
python ChatBot/Langgraph_ChatBot/1_basic_chatbot.py
```
