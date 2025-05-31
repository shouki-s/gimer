import os
import platform
from pathlib import Path

from gimer.constants import System


def get_repos_path() -> Path:
    system = platform.system()
    if system == System.MACOS:
        repos_path = Path.home() / "Library" / "Caches" / "gimer" / "repos"
    elif system == System.LINUX:
        repos_path = Path.home() / ".cache" / "gimer" / "repos"
    elif system == System.WINDOWS:
        repos_path = Path(os.environ.get("LOCALAPPDATA", "")) / "gimer" / "cache" / "repos"
    else:
        repos_path = Path(os.environ.get("TMPDIR", "/tmp")) / "gimer" / "repos"
    repos_path.mkdir(parents=True, exist_ok=True)
    return repos_path

def get_github_repo_path(repo_url: str) -> Path:
    """Generate repository path from GitHub repository URL

    Args:
        repo_url (str): GitHub repository URL
            Example: https://github.com/user/repo.git

    Returns:
        Path: Repository path in repos directory
    """
    parts = repo_url.split("/")
    assert len(parts) >= 3, f"Invalid GitHub URL: {repo_url}"  # noqa: PLR2004
    repo_name = parts[-1].replace(".git", "")
    user_name = parts[-2]
    repo_path = get_repos_path() / "github.com" / user_name / repo_name
    repo_path.mkdir(parents=True, exist_ok=True)
    return repo_path
