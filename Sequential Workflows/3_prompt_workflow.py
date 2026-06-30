import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

load_dotenv()
model = ChatMistralAI(model="mistral-small-latest", verbose=True)

class LLMState(TypedDict):
    topic : str
    outline : str
    content : str

def create_outline(state:LLMState) -> LLMState:
    prompt = f"give me an outline for this topic : {state['topic']}"
    response = model.invoke(prompt)
    state["outline"] = response.content
    return state

def create_content(state:LLMState) -> LLMState:
    prompt = f"give me content for this topic : {state['outline']}"
    response = model.invoke(prompt)
    state["content"] = response.content
    return state

graph = StateGraph(LLMState)

graph.add_node("create_outline",create_outline)
graph.add_node("create_content",create_content)

graph.add_edge(START,"create_outline")
graph.add_edge("create_outline","create_content")
graph.add_edge("create_content",END)

workflow = graph.compile()

initial_state = {"topic" : "Artificial Intelligence"}
final_state = workflow.invoke(initial_state)
print(final_state["content"])


try:
    png_data = workflow.get_graph().draw_mermaid_png()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(script_dir, "graph.png")
    with open(graph_path, "wb") as f:
        f.write(png_data)
    print(f"Graph visualization successfully saved as '{graph_path}'!")
except Exception as e:
    print(f"Could not save graph visualization: {e}")

