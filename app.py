"""
GitInsight AI — Streamlit UI
Wraps graph.builder.graph (LangGraph) for interactive repo review.
"""

import time
import traceback
from datetime import datetime

import streamlit as st

from graph.builder import graph


# ──────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitInsight AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# Styling — dark theme, consistent with your other project UIs
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #58a6ff, #79c0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .status-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .status-card.active {
        border-color: #58a6ff;
        box-shadow: 0 0 0 1px #58a6ff33;
    }
    .status-card.done {
        border-color: #3fb950;
    }
    .status-card.error {
        border-color: #f85149;
    }
    .file-pill {
        display: inline-block;
        background-color: #21262d;
        color: #c9d1d9;
        border-radius: 6px;
        padding: 2px 10px;
        margin: 2px;
        font-size: 0.82rem;
        font-family: monospace;
    }
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-box .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
    }
    .metric-box .label {
        color: #8b949e;
        font-size: 0.85rem;
    }
    div[data-testid="stExpander"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    code {
        color: #79c0ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────
defaults = {
    "review_running": False,
    "review_done": False,
    "review_error": None,
    "final_state": None,
    "log_events": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_review_state():
    st.session_state.review_running = False
    st.session_state.review_done = False
    st.session_state.review_error = None
    st.session_state.final_state = None
    st.session_state.log_events = []


# ──────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/user/repo",
        help="Public GitHub repo URL to analyze.",
    )

    st.markdown("---")
    max_display_files = st.slider(
        "Files to preview in sidebar", min_value=5, max_value=50, value=15, step=5
    )

    st.markdown("---")
    run_btn = st.button(
        "🚀 Start Review",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.review_running,
    )
    if st.session_state.review_running:
        st.caption("Review in progress — please wait...")

    if st.session_state.review_done or st.session_state.review_error:
        if st.button("🔄 Reset", use_container_width=True):
            reset_review_state()
            st.rerun()

    st.markdown("---")
    st.caption("GitInsight AI · LangGraph-powered repo reviewer")

# ──────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🔍 GitInsight AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated GitHub repository code review, powered by LangGraph</div>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# Kick off review
# ──────────────────────────────────────────────────────────────────────────
if run_btn:
    if not repo_url or not repo_url.strip():
        st.error("Please enter a GitHub repository URL before starting.")
    else:
        reset_review_state()
        st.session_state.review_running = True
        st.session_state.repo_url = repo_url.strip()
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# Run graph with live progress (stream if supported, else invoke)
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.review_running and not st.session_state.review_done:

    initial_state = {
        "repo_url": st.session_state.repo_url,
        "repo_path": None,
        "source_files": [],
        "current_file": None,
        "current_index": 0,
        "chunk_reviews": [],
        "reviews": {},
        "final_review": "",
        "report_path": None,
    }

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    metrics_placeholder = st.empty()

    def render_progress(state: dict, node_name: str = None):
        source_files = state.get("source_files") or []
        current_index = state.get("current_index") or 0
        total = len(source_files)

        with progress_placeholder.container():
            if total > 0:
                st.progress(min(current_index / total, 1.0))
            else:
                st.progress(0.0)

        with status_placeholder.container():
            label = node_name or "Working..."
            current_file = state.get("current_file")
            file_line = ""
            if current_file:
                file_line = (
                    '<br><span style="color:#8b949e">Current file: '
                    f'<code>{current_file}</code></span>'
                )
            st.markdown(
                f'<div class="status-card active">🟢 <b>{label}</b>{file_line}</div>',
                unsafe_allow_html=True,
            )

        with metrics_placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.markdown(
                f'<div class="metric-box"><div class="value">{total}</div>'
                f'<div class="label">Source Files</div></div>',
                unsafe_allow_html=True,
            )
            c2.markdown(
                f'<div class="metric-box"><div class="value">{current_index}</div>'
                f'<div class="label">Files Processed</div></div>',
                unsafe_allow_html=True,
            )
            c3.markdown(
                f'<div class="metric-box"><div class="value">{len(state.get("chunk_reviews") or [])}</div>'
                f'<div class="label">Chunk Reviews</div></div>',
                unsafe_allow_html=True,
            )

    try:
        final_state = None

        # Prefer streaming for live progress; fall back to a single invoke
        # if the compiled graph doesn't expose .stream() the way we expect.
        used_stream = False
        try:
            for step in graph.stream(initial_state):
                used_stream = True
                # step is typically {node_name: partial_state}
                for node_name, node_state in step.items():
                    if isinstance(node_state, dict):
                        final_state = {**(final_state or initial_state), **node_state}
                        render_progress(final_state, node_name=node_name)
                        st.session_state.log_events.append(
                            f"[{datetime.now().strftime('%H:%M:%S')}] Completed node: {node_name}"
                        )
            if final_state is None:
                raise RuntimeError("Stream produced no state.")
        except (AttributeError, TypeError, RuntimeError):
            # graph.stream not available/compatible — fall back to invoke
            if not used_stream:
                status_placeholder.markdown(
                    '<div class="status-card active">🟢 <b>Running full analysis (no live stream available)...</b></div>',
                    unsafe_allow_html=True,
                )
                final_state = graph.invoke(initial_state)

        st.session_state.final_state = final_state
        st.session_state.review_done = True
        st.session_state.review_running = False
        st.rerun()

    except Exception as e:
        st.session_state.review_error = f"{e}"
        st.session_state.review_running = False
        status_placeholder.markdown(
            f'<div class="status-card error">🔴 <b>Review Failed</b><br>'
            f'<span style="color:#8b949e">{e}</span></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Show full traceback"):
            st.code(traceback.format_exc())

# ──────────────────────────────────────────────────────────────────────────
# Error state (persisted after rerun)
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.review_error and not st.session_state.review_running:
    st.error(f"Repository Review Failed: {st.session_state.review_error}")

# ──────────────────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.review_done and st.session_state.final_state:
    state = st.session_state.final_state

    st.markdown(
        '<div class="status-card done">✅ <b>Repository Review Completed Successfully!</b></div>',
        unsafe_allow_html=True,
    )

    source_files = state.get("source_files") or []
    reviews = state.get("reviews") or {}
    chunk_reviews = state.get("chunk_reviews") or []
    final_review = state.get("final_review") or ""
    report_path = state.get("report_path")

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        [
            ("Files Analyzed", len(source_files)),
            ("Chunk Reviews", len(chunk_reviews)),
            ("Reviewed Files", len(reviews)),
            ("Report", "Ready" if report_path else "—"),
        ],
    ):
        col.markdown(
            f'<div class="metric-box"><div class="value">{value}</div>'
            f'<div class="label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab_overview, tab_files, tab_chunks, tab_report = st.tabs(
        ["📊 Overview", "📁 Source Files", "🧩 Chunk Reviews", "📄 Final Report"]
    )

    with tab_overview:
        st.subheader("Repository")
        st.code(state.get("repo_url", "—"), language=None)
        st.subheader("Local Clone Path")
        st.code(state.get("repo_path") or "—", language=None)

        if st.session_state.log_events:
            st.subheader("Execution Log")
            st.code("\n".join(st.session_state.log_events), language=None)

    with tab_files:
        st.subheader(f"Source Files ({len(source_files)})")
        if source_files:
            preview = source_files[:max_display_files]
            pills = "".join(f'<span class="file-pill">{f}</span>' for f in preview)
            st.markdown(pills, unsafe_allow_html=True)
            if len(source_files) > max_display_files:
                st.caption(f"...and {len(source_files) - max_display_files} more")
        else:
            st.info("No source files recorded in final state.")

    with tab_chunks:
        st.subheader(f"Per-File / Chunk Reviews ({len(chunk_reviews)})")
        if reviews:
            for fname, review_text in reviews.items():
                with st.expander(f"📄 {fname}"):
                    st.markdown(review_text)
        elif chunk_reviews:
            for i, chunk in enumerate(chunk_reviews, 1):
                with st.expander(f"Chunk {i}"):
                    st.markdown(chunk if isinstance(chunk, str) else str(chunk))
        else:
            st.info("No chunk-level reviews found in final state.")

    with tab_report:
        st.subheader("Final Aggregated Review")
        if final_review:
            st.markdown(final_review)
        else:
            st.info("No final review text found in state.")

        if report_path:
            st.markdown("---")
            try:
                with open(report_path, "rb") as f:
                    report_bytes = f.read()
                st.download_button(
                    "⬇️ Download Markdown Report",
                    data=report_bytes,
                    file_name=report_path.name,
                    mime="text/markdown",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Report path recorded but could not be opened: {e}")

elif not st.session_state.review_running and not st.session_state.review_error:
    st.info("👈 Enter a GitHub repository URL in the sidebar and click **Start Review** to begin.")