from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
import time

class CrashState(TypedDict):
    input: str
    step1: str
    step2: str
    step3: str

def step_1(state: CrashState) -> CrashState:
    print("Step 1 executed")
    return {"step1": "done", "input": state["input"]}

should_hang = True

def step_2(state: CrashState) -> CrashState:
    global should_hang
    if should_hang:
        print("Step 2 hanging... (Simulating crash. Please press Ctrl+C now!)")
        should_hang = False
        time.sleep(1000)
    else:
        print("Step 2 resumed and completed successfully!")
    return {"step2": "done"}

def step_3(state: CrashState) -> CrashState:
    print("Step 3 executed")
    return {"step3": "done"}

builder = StateGraph(CrashState)
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

builder.set_entry_point("step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

try:
    print("Running graph...")
    graph.invoke({"input": "start"}, config={"configurable": {"thread_id": 'thread-1'}})
except KeyboardInterrupt:
    print("Manually interrupted.")

print("Re-running the graph...")
final_state = graph.invoke(None, config={"configurable": {"thread_id": 'thread-1'}})
print("Final State:", final_state)

print(list(graph.get_state_history({"configurable": {"thread_id": 'thread-1'}})))
