from graph.state import GraphState
from tools.github import clone_repository

def clone_repo_node(state : GraphState) -> GraphState:
    
    repo_path = clone_repository(state["repo_url"])

    state["repo_path"] = repo_path

    print(state["repo_path"])
    return state