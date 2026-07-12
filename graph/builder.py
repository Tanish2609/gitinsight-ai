from langgraph.graph import StateGraph, START, END

from graph.state import GraphState

from nodes.clone_repo import clone_repo_node
from nodes.parse_repo import parse_repo_node
from nodes.should_continue import should_continue
from nodes.selector import selector_node
from nodes.reviewer import reviewer_node
from nodes.summarizer import summarizer_node
from nodes.report_writer import report_writer_node
from nodes.file_summarizer import file_summarizer_node
builder = StateGraph(GraphState)

builder.add_node("clone_repo", clone_repo_node)
builder.add_node("parse_repo", parse_repo_node)
builder.add_node("selector" , selector_node)
builder.add_node("reviewer" , reviewer_node)
builder.add_node("summarizer" , summarizer_node)
builder.add_node("report_writer" , report_writer_node)
builder.add_node("file_summarizer", file_summarizer_node)

builder.add_edge(START, "clone_repo")
builder.add_edge("clone_repo", "parse_repo")
builder.add_edge("parse_repo", "selector")
builder.add_edge("selector", "reviewer")
builder.add_edge("reviewer", "file_summarizer")

builder.add_conditional_edges(
    "file_summarizer",
    should_continue
)
builder.add_edge('summarizer' , "report_writer")
builder.add_edge("report_writer" , END)


graph = builder.compile()
