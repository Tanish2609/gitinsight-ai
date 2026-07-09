from git import Repo
import tempfile
from pathlib import Path

def clone_repository(repo_url : str) -> Path:
    temp_dir = Path(tempfile.mkdtemp())

    Repo.clone_from(
        repo_url ,
        temp_dir
    )

    return temp_dir