from time import perf_counter

from graph.state import GraphState
from models.llm import llm
from tools.file_reader import read_file
from tools.chunker import chunk_text
from prompts.reviewer import REVIEWER_PROMPT

review_chain = REVIEWER_PROMPT | llm


def reviewer_node(state: GraphState) -> GraphState:

    current_file = state["current_file"]
    file_content = read_file(current_file)

    print(f"\nReviewing: {current_file}")

    # ---------- Small Files ----------
    if len(file_content) < 4000:

        start = perf_counter()

        response = review_chain.invoke(
            {
                "current_file": str(current_file.relative_to(state["repo_path"])),
                "file_content": file_content,
            }
        )

        print(f"Completed in {perf_counter() - start:.2f}s")

        state["chunk_reviews"] = [response.content]

        return state

    # ---------- Large Files ----------
    chunks = chunk_text(file_content)
    chunk_reviews = []

    file_start = perf_counter()

    for i, chunk in enumerate(chunks, start=1):

        chunk_start = perf_counter()

        response = review_chain.invoke(
            {
                "current_file": str(current_file.relative_to(state["repo_path"])),
                "file_content": chunk,
            }
        )

        chunk_reviews.append(response.content)

        print(
            f"Chunk {i}/{len(chunks)} completed in "
            f"{perf_counter() - chunk_start:.2f}s"
        )

    print(f"Total review time: {perf_counter() - file_start:.2f}s")

    state["chunk_reviews"] = chunk_reviews

    return state



