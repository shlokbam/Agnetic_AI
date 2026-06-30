import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

load_dotenv()

class LLMState(TypedDict):
    ques: str
    ans: str

def prompt(state: LLMState) -> LLMState:
    raw_question = state["ques"]
    state["ques"] = f"Please explain the following topic in detail: {raw_question}"
    return state


def llm(state: LLMState) -> LLMState:
    model = ChatMistralAI(model="mistral-small-latest", verbose=True)
    response = model.invoke(state["ques"])
    state["ans"] = response.content
    return state

graph = StateGraph(LLMState)

graph.add_node("prompt", prompt)
graph.add_node("llm", llm)

graph.add_edge(START, "prompt")
graph.add_edge("prompt", "llm")
graph.add_edge("llm", END)

workflow = graph.compile()

final_state = workflow.invoke({"ques" : "Explain About Cricket"})
print(final_state)

try:
    png_data = workflow.get_graph().draw_mermaid_png()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(script_dir, "graph.png")
    with open(graph_path, "wb") as f:
        f.write(png_data)
    print(f"Graph visualization successfully saved as '{graph_path}'!")
except Exception as e:
    print(f"Could not save graph visualization: {e}")