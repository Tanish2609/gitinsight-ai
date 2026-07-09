from graph.state import GraphState

def selector_node(state : GraphState) -> GraphState:
    index = state['current_index']
    state['current_file'] = state["source_files"][index]
    state["current_index"] += 1
    return state

