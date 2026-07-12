from graph.state import GraphState
from models.llm import llm
from prompts.file_summarizer import FILE_SUMMARIZER_PROMPT


summary_chain = FILE_SUMMARIZER_PROMPT | llm


def file_summarizer_node(state: GraphState) -> GraphState:

    relative_path = str(
        state["current_file"].relative_to(state["repo_path"])
    )

    # Only one review -> no need to summarize
    if len(state["chunk_reviews"]) == 1:
        state["reviews"][relative_path] = state["chunk_reviews"][0]
        state["chunk_reviews"] = []
        return state

    # Multiple chunk reviews -> summarize
    response = summary_chain.invoke(
        {
            "chunk_reviews": "\n\n".join(state["chunk_reviews"])
        }
    )

    state["reviews"][relative_path] = response.content
    state["chunk_reviews"] = []

    return state 