import subprocess


class GitError(Exception):
    pass


class Git:
    def __init__(self) -> None:
        self._run_git_command("rev-parse", "--git-dir")

    def _run_git_command(self, *args: str, capture_output: bool = False) -> str | None:
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

    @classmethod
    def clone_repository_from_github(cls, repo_url: str, target_dir: str) -> None:
        subprocess.run(
            ["git", "clone", repo_url, target_dir],
            check=True,
            capture_output=True,
            text=True
        )

    def get_current_branch(self) -> str:
        return self._run_git_command("rev-parse", "--abbrev-ref", "HEAD", capture_output=True).strip()

    def get_all_branches(self) -> list[str]:
        branches = self._run_git_command("branch", "--format=%(refname:short)", capture_output=True)
        return [b for b in branches.splitlines() if b]

    def check_working_directory_clean(self) -> bool:
        status = self._run_git_command("status", "--porcelain", capture_output=True)
        return not status

    def clean_working_directory(self) -> None:
        self._run_git_command("clean", "-fdx")
        self._run_git_command("reset", "--hard")

    def checkout_branch(self, branch: str) -> None:
        self._run_git_command("checkout", branch)

    def pull_branch(self, branch: str) -> None:
        self._run_git_command("pull", "origin", branch)

    def push_branch(self, branch: str) -> None:
        self._run_git_command("push", "origin", branch)

    def merge_branch(self, target_branch: str) -> None:
        self._run_git_command("merge", target_branch)
