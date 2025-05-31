import pytest
from git import Repo
from gimer.git_utils import (
    GitError,
    NotGitRepositoryError,
    MergeError,
    get_repository,
    get_current_branch,
    get_all_branches,
    check_working_directory_clean,
    merge_branch,
)

def test_check_working_directory_clean(mocker):
    mock_repo = mocker.Mock(spec=Repo)
    mock_repo.is_dirty.return_value = False
    assert check_working_directory_clean(mock_repo) is True

    mock_repo.is_dirty.return_value = True
    assert check_working_directory_clean(mock_repo) is False

def test_merge_branch_success(mocker):
    mock_repo = mocker.Mock(spec=Repo)
    merge_branch(mock_repo, "develop")
    mock_repo.git.merge.assert_called_once_with("develop")
