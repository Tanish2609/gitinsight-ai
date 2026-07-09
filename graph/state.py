from pathlib import Path
from langgraph.graph import StateGraph , START , END
from typing import TypedDict

class GraphState(TypedDict):
    repo_url : str
    repo_path : Path
    source_files : list[Path]
    current_index : int = 0
    current_file : Path | None
    reviews : dict

