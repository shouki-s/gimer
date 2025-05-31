import git
from git import GitCommandError, Repo


class GitError(Exception):
    pass

class NotGitRepositoryError(GitError):
    pass

class MergeError(GitError):
    pass

def get_repository() -> Repo:
    try:
        return git.Repo('.')
    except git.InvalidGitRepositoryError as e:
        raise NotGitRepositoryError("This directory is not a Git repository.") from e

def get_current_branch(repo: Repo) -> str:
    return repo.active_branch.name

def get_all_branches(repo: Repo) -> list[str]:
    return [branch.name for branch in repo.branches]

def check_working_directory_clean(repo: Repo) -> bool:
    return not repo.is_dirty()

def merge_branch(repo: Repo, target_branch: str) -> None:
    try:
        repo.git.merge(target_branch)
    except GitCommandError as e:
        raise MergeError(str(e)) from e
