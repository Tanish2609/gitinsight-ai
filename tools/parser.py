from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next"
}

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".html",
    ".css",
    ".md"
}

def get_source_files(repo_path : Path) -> list[Path]:

    source_files = []

    for file in repo_path.rglob("*"):
        
        if not file.is_file():
            continue
        if any(folder in file.parts for folder in IGNORE_DIRS):
            continue
        if file.suffix not in SUPPORTED_EXTENSIONS:
            continue
        source_files.append(file)
        
    return source_files
