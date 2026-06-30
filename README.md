# 🤖 Agentic_AI

A hands-on codebase for learning, practicing, and building stateful Agentic AI workflows using LangChain and LangGraph. As I progress, this repository will serve as a workspace for folders, scripts, notebooks, and prototype agents.

---

## 📂 Repository Structure

### 🔄 [Sequential Workflows](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Sequential%20Workflows)
Practice with sequential node execution, basic state flows, and deterministic graphs.
- [1_bmi_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Sequential%20Workflows/1_bmi_workflow.py) - A state-based BMI calculator graph. Computes the BMI of a person based on height and weight, categorizes it, and saves a visualization of the graph flow.
- [2_llm_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Sequential%20Workflows/2_llm_workflow.py) - A basic LLM node connection workflow using `ChatMistralAI` to prompt and query the LLM sequentially.
- [3_prompt_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Sequential%20Workflows/3_prompt_workflow.py) - A multi-step sequential content generation graph. First outlines a topic, then generates full content based on the outline using `ChatMistralAI`.

### 🔀 [Parallel Workflows](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Parallel%20Workflows)
*(Planned)* Practice with parallel branch executions, map-reduce operations, and fan-in/fan-out patterns.

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

Create a [.env](file:///Users/shlokbam/Documents/Code/Agnetic_AI/.env) file in the root directory to store your API keys safely:
```env
# Mistral AI API key (used in the LLM workflows)
MISTRAL_API_KEY="your-mistral-api-key-here"

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





