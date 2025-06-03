import subprocess


class GitError(Exception):
    pass

def run_git_command(*args: str, capture_output: bool = False) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=capture_output,
            text=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        raise GitError(f"git {' '.join(args)} failed: {e.stderr}") from e

def clone_repository_from_github(repo_url: str, target_dir: str) -> None:
    run_git_command("clone", repo_url, target_dir)

def get_repository() -> None:
    run_git_command("rev-parse", "--git-dir")

def get_current_branch() -> str:
    return run_git_command("rev-parse", "--abbrev-ref", "HEAD", capture_output=True).strip()

def get_all_branches() -> list[str]:
    branches = run_git_command("branch", "--format=%(refname:short)", capture_output=True)
    return [b for b in branches.splitlines() if b]

def check_working_directory_clean() -> bool:
    status = run_git_command("status", "--porcelain", capture_output=True)
    return not status

def clean_working_directory() -> None:
    run_git_command("clean", "-fdx")
    run_git_command("reset", "--hard")

def checkout_branch(branch: str) -> None:
    run_git_command("checkout", branch)

def push_branch(branch: str) -> None:
    run_git_command("push", "origin", branch)

def merge_branch(target_branch: str) -> None:
    run_git_command("merge", target_branch)
