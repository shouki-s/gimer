import os
import platform
import shutil
from pathlib import Path


def get_cache_dir() -> Path:
    system = platform.system().lower()

    if system == "darwin":  # macOS
        cache_dir = Path.home() / "Library" / "Caches" / "gimer" / "repos"
    elif system == "linux":
        cache_dir = Path.home() / ".cache" / "gimer" / "repos"
    elif system == "windows":
        cache_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "gimer" / "cache" / "repos"
    else:
        cache_dir = Path(os.environ.get("TMPDIR", "/tmp")) / "gimer" / "repos"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_repo_cache_path(repo_url: str) -> Path:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    return get_cache_dir() / repo_name

def cache_repository(repo_url: str, source_dir: Path) -> None:
    cache_path = get_repo_cache_path(repo_url)
    if cache_path.exists():
        shutil.rmtree(cache_path)
    shutil.copytree(source_dir, cache_path)

def get_cached_repository(repo_url: str) -> Path | None:
    cache_path = get_repo_cache_path(repo_url)
    return cache_path if cache_path.exists() else None
