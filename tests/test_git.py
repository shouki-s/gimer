import subprocess
from unittest.mock import Mock

import pytest

from gimer.git import Git, GitError, UserAbortedError


class TestGit:
    @pytest.fixture(autouse=True)
    def _common_mocks(self, mocker):
        self.mock_subprocess_run = mocker.patch('gimer.git.subprocess.run')
        self.mock_console_print = mocker.patch('gimer.git.console.print')
        self.mock_inquirer_confirm = mocker.patch('gimer.git.inquirer.confirm')
        self.mock_os_getcwd = mocker.patch('os.getcwd')

        self.mock_os_getcwd.return_value = "/current/dir"
        mock_result = Mock()
        mock_result.stdout = ""
        self.mock_subprocess_run.return_value = mock_result

    @pytest.fixture
    def git(self):
        return Git(dry_run=False, no_confirm=True, confirm_all=False)

    @pytest.fixture
    def git_dry_run(self):
        return Git(dry_run=True, no_confirm=False, confirm_all=False)

    @pytest.fixture
    def git_confirm_all(self):
        return Git(dry_run=False, no_confirm=False, confirm_all=True)

    @pytest.fixture
    def git_confirm_origin(self):
        return Git(dry_run=False, no_confirm=False, confirm_all=False)

    def test_init(self):
        git = Git()
        assert git.dry_run is False
        assert git.no_confirm is False
        assert git.confirm_all is False

        git = Git(dry_run=True, no_confirm=True, confirm_all=True)
        assert git.dry_run is True
        assert git.no_confirm is True
        assert git.confirm_all is True

    def test_should_confirm_no_confirm(self, git):
        assert git._should_confirm("push") is False
        assert git._should_confirm("pull") is False

    def test_should_confirm_all(self, git_confirm_all):
        assert git_confirm_all._should_confirm("push") is True
        assert git_confirm_all._should_confirm("pull") is True

    def test_should_confirm_origin(self, git_confirm_origin):
        assert git_confirm_origin._should_confirm("push") is True
        assert git_confirm_origin._should_confirm("pull") is False

    def test_run_git_command_success(self, git):
        mock_result = Mock()
        mock_result.stdout = "output"
        self.mock_subprocess_run.return_value = mock_result

        result = git._run_git_command("status", capture_output=True)

        self.mock_console_print.assert_called_once_with("[yellow]≫ git status[/yellow]")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "status"],
            check=True,
            capture_output=True,
            text=True
        )
        assert result == "output"

    def test_run_git_command_dry_run(self, git_dry_run):
        result = git_dry_run._run_git_command("status")

        self.mock_console_print.assert_called_once_with("[yellow]≫ git status[/yellow]")
        self.mock_subprocess_run.assert_not_called()
        assert result is None

    def test_run_git_command_failure(self, git):
        error = subprocess.CalledProcessError(1, "git")
        error.stderr = "error message"
        self.mock_subprocess_run.side_effect = error

        with pytest.raises(GitError) as exc_info:
            git._run_git_command("status")

        assert "git status failed: error message" in str(exc_info.value)

    def test_run_git_command_confirm_cancelled(self, git_confirm_all):
        self.mock_inquirer_confirm.return_value.execute.return_value = False

        with pytest.raises(UserAbortedError):
            git_confirm_all._run_git_command("push")

        self.mock_subprocess_run.assert_not_called()

    def test_clone_repository(self, git):
        git.clone_repository("https://github.com/user/repo.git")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "clone", "https://github.com/user/repo.git", "/current/dir"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_get_branches(self, git):
        self.mock_subprocess_run.return_value.stdout = "origin/main\norigin/develop\norigin/HEAD"
        branches = git.get_branches()
        assert branches == ["main", "develop"]

    def test_check_working_directory_clean_true(self, git):
        self.mock_subprocess_run.return_value.stdout = ""
        assert git.check_working_directory_clean() is True

    def test_check_working_directory_clean_false(self, git):
        self.mock_subprocess_run.return_value.stdout = "M modified_file.py"
        assert git.check_working_directory_clean() is False

    def test_clean_working_directory(self, git):
        git.clean_working_directory()
        assert self.mock_subprocess_run.call_count == 2
        calls = self.mock_subprocess_run.call_args_list
        assert calls[0][0][0] == ["git", "clean", "-fdx"]
        assert calls[1][0][0] == ["git", "reset", "--hard"]

    def test_checkout_branch(self, git):
        git.checkout_branch("develop")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "checkout", "develop"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_fetch(self, git):
        git.fetch()
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "fetch", "origin"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_pull_branch(self, git):
        git.pull_branch("main")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "pull", "origin", "main"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_push_branch(self, git):
        git.push_branch("main")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "push", "origin", "main"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_merge_branch(self, git):
        git.merge_branch("develop")
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "merge", "--no-edit", "develop"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_is_merge_in_progress_true(self, git):
        self.mock_subprocess_run.return_value.stdout = "merge_head_hash"
        assert git.is_merge_in_progress() is True

    def test_is_merge_in_progress_false(self, git):
        self.mock_subprocess_run.side_effect = GitError("No MERGE_HEAD")
        assert git.is_merge_in_progress() is False

    def test_resolve_conflicts(self, git):
        git.resolve_conflicts()
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "mergetool"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_abort_merge(self, git):
        git.abort_merge()
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "merge", "--abort"],
            check=True,
            capture_output=False,
            text=True
        )

    def test_commit_merge(self, git):
        git.commit_merge()
        self.mock_subprocess_run.assert_called_once_with(
            ["git", "commit"],
            check=True,
            capture_output=False,
            text=True
        )
