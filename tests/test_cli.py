from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from gimer.cli import cleanup_repository, main, merge
from gimer.git import UserAbortedError


class TestCLI:
    @pytest.fixture(autouse=True)
    def _common_mocks(self, mocker):
        self.mock_git = mocker.patch('gimer.cli.Git')
        self.mock_get_github_repo_path = mocker.patch('gimer.cli.get_github_repo_path')
        self.mock_os_chdir = mocker.patch('os.chdir')
        self.mock_inquirer_fuzzy = mocker.patch('gimer.cli.inquirer.fuzzy')
        self.mock_confirm_ask = mocker.patch('gimer.cli.Confirm.ask')
        self.mock_shutil_rmtree = mocker.patch('gimer.cli.shutil.rmtree')
        self.mock_console_print = mocker.patch('gimer.cli.console.print')

        # Set default return values
        mock_path = Mock(spec=Path)
        mock_path.__truediv__ = Mock(return_value=Mock())
        (mock_path / '.git').exists = Mock(return_value=True)
        self.mock_get_github_repo_path.return_value = mock_path

        mock_git_instance = Mock()
        mock_git_instance.check_working_directory_clean.return_value = True
        mock_git_instance.get_branches.return_value = ['main', 'develop']
        self.mock_git.return_value = mock_git_instance

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_main_basic(self, runner):
        with patch('gimer.cli.merge') as mock_merge:
            result = runner.invoke(main, ['https://github.com/user/repo.git'])
            assert result.exit_code == 0
            mock_merge.assert_called_once()

    def test_main_with_options(self, runner):
        with patch('gimer.cli.merge') as mock_merge:
            result = runner.invoke(main, [
                'https://github.com/user/repo.git',
                '--source', 'feature',
                '--target', 'main',
                '--dry-run',
                '--cleanup',
                '--confirm-all',
            ])
            assert result.exit_code == 0
            args = mock_merge.call_args[0]
            config = args[4]
            assert config['dry_run'] is True
            assert config['confirm_all'] is True

    def test_main_user_aborted(self, runner):
        with patch('gimer.cli.merge') as mock_merge:
            mock_merge.side_effect = UserAbortedError("Cancelled")
            result = runner.invoke(main, ['https://github.com/user/repo.git'])
            assert result.exit_code == 0

    def test_main_with_cleanup(self, runner):
        with patch('gimer.cli.cleanup_repository') as mock_cleanup:
            result = runner.invoke(main, [
                'https://github.com/user/repo.git',
                '--cleanup'
            ])
            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

    def test_merge_function(self):
        mock_git_instance = self.mock_git.return_value
        self.mock_inquirer_fuzzy.return_value.execute.side_effect = ['develop', 'main']

        repo_path = self.mock_get_github_repo_path.return_value
        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', None, None, config)

        mock_git_instance.fetch.assert_called_once()
        mock_git_instance.checkout_branch.assert_any_call('develop')
        mock_git_instance.checkout_branch.assert_any_call('main')
        mock_git_instance.pull_branch.assert_any_call('develop')
        mock_git_instance.pull_branch.assert_any_call('main')
        mock_git_instance.merge_branch.assert_called_once_with('develop')
        mock_git_instance.push_branch.assert_called_once_with('main')

    def test_merge_function_clone_if_not_exists(self):
        mock_git_instance = self.mock_git.return_value
        repo_path = self.mock_get_github_repo_path.return_value
        (repo_path / '.git').exists.return_value = False

        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', 'main', 'main', config)

        mock_git_instance.clone_repository.assert_called_once_with('https://github.com/user/repo.git')

    def test_merge_function_dirty_working_directory(self):
        mock_git_instance = self.mock_git.return_value
        mock_git_instance.check_working_directory_clean.return_value = False
        self.mock_confirm_ask.return_value = True

        repo_path = self.mock_get_github_repo_path.return_value
        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', 'main', 'main', config)

        mock_git_instance.clean_working_directory.assert_called_once()

    def test_merge_function_dirty_cancelled(self):
        mock_git_instance = self.mock_git.return_value
        mock_git_instance.check_working_directory_clean.return_value = False
        self.mock_confirm_ask.return_value = False

        repo_path = self.mock_get_github_repo_path.return_value
        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', 'main', 'main', config)

        mock_git_instance.clean_working_directory.assert_not_called()

    def test_merge_conflict_resolution(self):
        mock_git_instance = self.mock_git.return_value
        mock_git_instance.merge_branch.side_effect = Exception("CONFLICT: merge conflict")
        mock_git_instance.is_merge_in_progress.return_value = True

        repo_path = self.mock_get_github_repo_path.return_value
        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', 'main', 'main', config)

        mock_git_instance.resolve_conflicts.assert_called_once()
        mock_git_instance.commit_merge.assert_called_once()

    def test_merge_conflict_aborted(self):
        mock_git_instance = self.mock_git.return_value
        mock_git_instance.merge_branch.side_effect = Exception("CONFLICT: merge conflict")
        mock_git_instance.is_merge_in_progress.return_value = False

        repo_path = self.mock_get_github_repo_path.return_value
        config = {'dry_run': False, 'no_confirm': False, 'confirm_all': False}

        merge(repo_path, 'https://github.com/user/repo.git', 'main', 'main', config)

        mock_git_instance.resolve_conflicts.assert_called_once()
        mock_git_instance.commit_merge.assert_not_called()

    def test_cleanup_repository(self):
        repo_path = "/test/repo"
        cleanup_repository(repo_path)

        self.mock_os_chdir.assert_called_once_with("..")
        self.mock_shutil_rmtree.assert_called_once_with(repo_path)
