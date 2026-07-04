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
Practice with parallel branch executions, map-reduce operations, and fan-in/fan-out patterns.
- [1_batsman_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Parallel%20Workflows/1_batsman_workflow.py) - A parallel batsman stats calculator graph. Computes strike rate, balls per boundary, and boundary percentage in parallel branches and merges them into a final summary.
- [2_UPSC_essay_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Parallel%20Workflows/2_UPSC_essay_workflow.py) - A parallel essay evaluation workflow. Evaluates language quality, depth of analysis, and clarity of thought concurrently using structured outputs (Pydantic), fanning in to aggregate individual scores and compile a summarized feedback report.

### 🌿 [Conditional Workflows](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Conditional%20Workflows)
Practice with conditional routing, dynamic node transitions, and branching logic.
- [1_quadratic_equation_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Conditional%20Workflows/1_quadratic_equation_workflow.py) - A conditional routing state graph that solves quadratic equations. Calculates the discriminant and uses conditional edges to route the state to calculate real roots, repeating roots, or identify no real roots.
- [2_review_reply_workflow.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/Conditional%20Workflows/2_review_reply_workflow.py) - A conditional review processing workflow. Classifies review sentiment using structured output. Routes positive reviews directly to a warm thank-you generator node, and routes negative reviews through an issue diagnosis node (determining issue type, tone, and urgency) before generating an empathetic resolution support reply.

### 🔁 [Iterative Workflows](file:///Users/shlokbam/Documents/Code/Agnetic_AI/%20Iterative%20Workflows)
Practice with loop-based state machines, feedback loops, self-correction, and human-in-the-loop patterns.
- [1_X_post_generator.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/%20Iterative%20Workflows/1_X_post_generator.py) - An iterative Twitter/X post generator workflow. Generates a humorous tweet, critiques/evaluates it using structured output (evaluating humor, punchiness, virality, format, and originality), and loops back to optimize the draft based on the feedback until it is approved or hits the maximum iteration limit.

### 💬 [ChatBots](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot)
Practice building conversational interfaces, managing message histories, and stateful chat loops.
- [1_basic_chatbot.py](file:///Users/shlokbam/Documents/Code/Agnetic_AI/ChatBot/1_basic_chatbot.py) - A basic chatbot graph that uses `ChatMistralAI` and LangGraph's `add_messages` state annotation to maintain conversation state. Includes an interactive terminal loop to chat with the model.

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





