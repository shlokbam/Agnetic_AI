# 🤖 Agentic_AI

A hands-on codebase for learning, practicing, and building stateful Agentic AI workflows using LangChain and LangGraph. As I progress, this repository will serve as a workspace for folders, scripts, notebooks, and prototype agents.

---

## 📂 Repository Structure

- `Sequential Workflows/` - Practice with sequential node execution, basic state flows, and deterministic graphs.
  - [`app.py`](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Sequential%20Workflows/app.py) - A simple state-based BMI calculator graph.
  - `graph.png` - Visual representation of the compiled BMI workflow.
- `requirements.txt` - Python dependencies for LangChain, LangGraph, and various LLM integrations.

---

## 🛠️ Getting Started

### 1. Prerequisites & Environment Setup

This repository uses [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver) to manage environments. 

To set up the virtual environment:
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# Or: .venv\Scripts\activate on Windows

# Install the dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory to store your API keys safely:
```env
# Google Gemini API key (if using langchain-google-genai)
GEMINI_API_KEY="your-gemini-api-key-here"

# OpenAI API key (if using langchain-openai)
OPENAI_API_KEY="your-openai-api-key-here"

# LangSmith (highly recommended for tracing and debugging your agent graphs)
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="your-langsmith-api-key"
```

---

Happy learning! 🚀





