import os
import subprocess

from InquirerPy import inquirer
from rich.console import Console

console = Console()


class GitError(Exception):
    pass


class UserAbortedError(Exception):
    """Exception raised when the user aborts the operation."""


class Git:
    def __init__(self, dry_run: bool = False, confirm: str | None = None) -> None:
        self.dry_run = dry_run
        self.confirm = confirm

    def _should_confirm(self, command: str) -> bool:
        if not self.confirm:
            return False
        if self.confirm == "all":
            return True
        if self.confirm == "origin":
            # Check if command affects origin
            origin_commands = {"push"}
            return command in origin_commands
        return False

    def _run_git_command(self, *args: str, capture_output: bool = False) -> str | None:
        console.print(f"[yellow]≫ git {' '.join(args)}[/yellow]")
        if self.dry_run:
            return None

        if self._should_confirm(args[0]) and not inquirer.confirm("Execute this command?",default=True).execute():
            raise UserAbortedError("Command execution cancelled by user")

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

    def clone_repository(self, repo_url: str) -> None:
        self._run_git_command("clone", repo_url, os.getcwd())

    def get_branches(self) -> list[str]:
        branches = self._run_git_command("branch", "--format=%(refname:short)", "--remotes", capture_output=True)
        return [b.replace("origin/", "") for b in branches.splitlines() if b and b != "origin/HEAD"]

    def check_working_directory_clean(self) -> bool:
        status = self._run_git_command("status", "--porcelain", capture_output=True)
        return not status

    def clean_working_directory(self) -> None:
        self._run_git_command("clean", "-fdx")
        self._run_git_command("reset", "--hard")

    def checkout_branch(self, branch: str) -> None:
        self._run_git_command("checkout", branch)

    def fetch(self) -> None:
        self._run_git_command("fetch", "origin")

    def pull_branch(self, branch: str) -> None:
        self._run_git_command("pull", "origin", branch)

    def push_branch(self, branch: str) -> None:
        self._run_git_command("push", "origin", branch)

    def merge_branch(self, target_branch: str) -> None:
        self._run_git_command("merge", "--no-edit", target_branch)

    def is_merge_in_progress(self) -> bool:
        """Check if a merge is in progress."""
        try:
            self._run_git_command("rev-parse", "--verify", "MERGE_HEAD", capture_output=True)
            return True
        except GitError:
            return False

    def resolve_conflicts(self) -> None:
        """Open editor to resolve merge conflicts."""
        self._run_git_command("mergetool")

    def abort_merge(self) -> None:
        """Abort the current merge operation."""
        self._run_git_command("merge", "--abort")

    def commit_merge(self) -> None:
        """Commit the merge after conflict resolution."""
        self._run_git_command("commit")
