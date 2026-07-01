from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import os

class BatsmanState(TypedDict):
    runs: int
    balls: int
    fours: int
    sixes: int
    sr: float
    bpb: float
    boundary_percent: float
    summary: str

def calculate_sr(state:BatsmanState) -> BatsmanState:
    sr = (state["runs"] / state["balls"]) * 100
    return {"sr" : sr}

def calculate_bpb(state:BatsmanState) -> BatsmanState:
    bpb = state['balls']/(state['fours'] + state['sixes'])
    return {"bpb" : bpb}

def calculate_boundary_percentage(state:BatsmanState) -> BatsmanState:
    boundary_percentage = ((state['fours']*4 + state['sixes']*6) / state['runs'])*100
    return {"boundary_percent" : boundary_percentage}

def summary(state: BatsmanState):
    summary = f"""
    You scored {state['runs']} runs in {state['balls']} balls
    strike_rate = {state['sr']}
    balls_per_boundary = {state['bpb']}
    boundary_percentage = {state['boundary_percent']}
    """
    return {"summary" : summary}

graph = StateGraph(BatsmanState)

graph.add_node("calculate_sr",calculate_sr)
graph.add_node("calculate_bpb",calculate_bpb)
graph.add_node("calculate_boundary_percentage",calculate_boundary_percentage)
graph.add_node("summary",summary)

graph.add_edge(START,"calculate_sr")
graph.add_edge(START,"calculate_bpb")
graph.add_edge(START,"calculate_boundary_percentage")
graph.add_edge("calculate_sr","summary")
graph.add_edge("calculate_bpb","summary")
graph.add_edge("calculate_boundary_percentage","summary")
graph.add_edge("summary",END)

workflow = graph.compile()

initial_state = {"runs": 80, "balls": 40, "fours": 8, "sixes": 2}
final_state = workflow.invoke(initial_state)
print(final_state["summary"])


try:
    png_data = workflow.get_graph().draw_mermaid_png()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(script_dir, "graph.png")
    with open(graph_path, "wb") as f:
        f.write(png_data)
    print(f"Graph visualization successfully saved as '{graph_path}'!")
except Exception as e:
    print(f"Could not save graph visualization: {e}") 

