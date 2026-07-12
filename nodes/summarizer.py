from graph.state import GraphState
from models.llm import llm
from prompts.summarizer import SUMMARIZER_PROMPT


chain = SUMMARIZER_PROMPT | llm
def summarizer_node(state : GraphState) -> GraphState:
    
    reviews = state["reviews"]
    combined_reviews = ""

    for file_name, review in state["reviews"].items():
        combined_reviews += (
            f"## {file_name}\n\n"
            f"{review}\n\n"
        )
    prompt_value = {
        "reviews" : combined_reviews
    } 
    

    response = chain.invoke(prompt_value)
    final_review = response.content
    state['final_review'] = final_review

    return state