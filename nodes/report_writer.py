from pathlib import Path

from graph.state import GraphState


def report_writer_node(state: GraphState) -> GraphState:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # repo ka naam repo_path se nikal lo
    repo_name = (
    state["repo_url"]
    .rstrip("/")
    .split("/")[-1]
    )

    report_path = reports_dir / f"{repo_name}_review.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(state["final_review"])

    state["report_path"] = report_path

    print(f"\nReport saved at: {report_path}")

    return state