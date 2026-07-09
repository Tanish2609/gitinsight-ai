from langgraph.graph import StateGraph, START, END

from graph.state import GraphState

from nodes.clone_repo import clone_repo_node
from nodes.parse_repo import parse_repo_node


builder = StateGraph(GraphState)

builder.add_node("clone_repo", clone_repo_node)
builder.add_node("parse_repo", parse_repo_node)

builder.add_edge(START, "clone_repo")
builder.add_edge("clone_repo", "parse_repo")
builder.add_edge("parse_repo", END)

graph = builder.compile()