from graph.state import GraphState
from tools.parser import get_source_files

def parse_repo_node(state : GraphState) -> GraphState:

    files = get_source_files(state["repo_path"])

    state["source_files"] = files
    
    return state