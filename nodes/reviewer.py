from graph.state import GraphState
from models.llm import llm
from tools.file_reader import read_file
from prompts.reviewer import REVIEWER_PROMPT


review_chain = REVIEWER_PROMPT | llm


def reviewer_node(state: GraphState) -> GraphState:

    current_file = state["current_file"]

    file_content = read_file(current_file)

    relative_path = str(
        current_file.relative_to(state["repo_path"])
    )

    # Skip empty/error files
    if (
        file_content == "Empty File"
        or file_content.startswith("File Not Found")
        or file_content.startswith("Permission Denied")
        or file_content.startswith("Error Reading File")
    ):
        state["reviews"][relative_path] = file_content
        return state

    prompt_value = {
        "current_file": relative_path,
        "file_content": file_content,
    }

    review = review_chain.invoke(prompt_value)

    state["reviews"][relative_path] = review.content

    return state



