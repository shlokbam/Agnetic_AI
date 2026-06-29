from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BMIState(TypedDict):
    weight_kg : float
    height_m : float
    bmi : float
    category : str 

def calculate_bmi(state: BMIState) -> BMIState:
    weight  = state["weight_kg"]
    height = state["height_m"]
    bmi = weight/(height**2)
    state["bmi"] = bmi
    return state

def label_bmi(state: BMIState) -> BMIState:
    bmi = state["bmi"]
    if bmi < 18.5:
        state["category"] = "Underweight"
    elif 18.5 <= bmi <= 22.9:
        state["category"] = "Normal weight"
    elif 25 <= bmi <= 30:
        state["category"] = "Overweight"
    else:
        state["category"] = "Obese"
    
    return state

graph = StateGraph(BMIState)

graph.add_node("calculate_bmi",calculate_bmi)
graph.add_node("label_bmi",label_bmi)

graph.add_edge(START,"calculate_bmi")
graph.add_edge("calculate_bmi","label_bmi")
graph.add_edge("label_bmi",END)

workflow = graph.compile()

initial_state = {"weight_kg" : 85, "height_m" : 1.75 }
final_state = workflow.invoke(initial_state)

print(final_state)

try:
    import os
    png_data = workflow.get_graph().draw_mermaid_png()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(script_dir, "graph.png")
    with open(graph_path, "wb") as f:
        f.write(png_data)
    print(f"Graph visualization successfully saved as '{graph_path}'!")
except Exception as e:
    print(f"Could not save graph visualization: {e}")
    