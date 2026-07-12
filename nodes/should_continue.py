from graph.state import GraphState
from langgraph.graph import END

def should_continue(state : GraphState):
    index = state["current_index"]
    if(index >= len(state["source_files"])):
        return "summarizer"
    else:
        return "selector"

