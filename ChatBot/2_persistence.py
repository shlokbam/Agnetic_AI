import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatMistralAI(model="mistral-small-latest", api_key=os.getenv("MISTRAL_API_KEY"))

class JokeState(TypedDict):
    topic: str
    joke: str
    explanation: str

def generate_joke(state: JokeState):
    prompt = f'generate a joke on the topic {state["topic"]}'
    response = llm.invoke(prompt).content
    return {"joke": response}

def generate_explanation(state: JokeState):
    prompt = f'write an explanation for the joke - {state["joke"]}'
    response = llm.invoke(prompt).content
    return {'explanation': response}

graph = StateGraph(JokeState)

graph.add_node('generate_joke', generate_joke)
graph.add_node('generate_explanation', generate_explanation)

graph.add_edge(START, 'generate_joke')
graph.add_edge('generate_joke', 'generate_explanation')
graph.add_edge('generate_explanation', END)

checkpointer = InMemorySaver()
workflow = graph.compile(checkpointer=checkpointer)

# config1 = {"configurable": {"thread_id": "1"}}
# workflow.invoke({'topic':'pizza'}, config=config1)

# print(workflow.get_state(config1))

# print("History for config1:")
# for state in workflow.get_state_history(config1):
#     print(state)
#     print("=" * 50)

config2 = {"configurable": {"thread_id": "2"}}
workflow.invoke({'topic':'pasta'}, config=config2)

print(workflow.get_state(config2))
    
print("History for config2:")
for state in workflow.get_state_history(config2):
    print(state)
    print("=" * 50)


