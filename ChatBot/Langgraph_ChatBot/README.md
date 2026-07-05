# 🤖 LangGraph Basic Chatbot & Streamlit Web App

This directory contains a stateful chatbot built with **LangGraph** and **LangChain (Mistral AI)**, including both a CLI version and a premium **Streamlit** web application with a live-rendering workflow graph.

## 📂 Directory Contents

- **[1_basic_chatbot.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/1_basic_chatbot.py)**: The core terminal-based stateful chatbot script. It uses `MemorySaver` to persist conversation history and allows interactive messaging in the CLI.
- **[app.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/Langgraph_ChatBot/app.py)**: A premium web application built with Streamlit. It provides a visual chat canvas and tracks/highlights the active graph execution state (`START` -> `chat_node` -> `END`) live on screen during inference.

---

## 🚀 How to Run

### 1. Install Dependencies
Make sure you have active environment settings and dependencies installed:
```bash
pip install -r requirements.txt
```

### 2. Run the CLI Chatbot
To run the terminal-based interactive chatbot:
```bash
python 1_basic_chatbot.py
```

### 3. Run the Streamlit Web Application
To run the interactive web interface with the live graph visualizer:
```bash
streamlit run app.py
```
> [!WARNING]
> Do NOT run `python app.py` directly. Streamlit applications require the Streamlit runtime context to function and must be started using the `streamlit run` command. Calling `python app.py` directly will raise session state errors and thread warnings.
Once launched, open your web browser and navigate to `http://localhost:8501`.
