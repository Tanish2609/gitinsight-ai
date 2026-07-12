from graph.state import GraphState
from tools.parser import get_source_files

def parse_repo_node(state : GraphState) -> GraphState:

    files = get_source_files(state["repo_path"])

    print(f"Total files: {len(files)}")

    state["source_files"] = files
    
    return state