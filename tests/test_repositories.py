from pathlib import Path

import pytest

from gimer.repositories import get_github_repo_path, get_repos_path


class TestRepositories:
    @pytest.fixture(autouse=True)
    def _common_mocks(self, mocker):
        self.mock_system = mocker.patch('gimer.repositories.platform.system')
        self.mock_mkdir = mocker.patch('pathlib.Path.mkdir')
        self.mock_os_environ_get = mocker.patch('gimer.repositories.os.environ.get')

        self.mock_system.return_value = 'darwin'
        self.mock_os_environ_get.return_value = None

    def test_get_repos_path_macos(self):
        self.mock_system.return_value = 'darwin'
        repos_dir = get_repos_path()
        expected = Path.home() / "Library" / "Caches" / "gimer" / "repos"
        assert repos_dir == expected
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_repos_path_linux(self):
        self.mock_system.return_value = 'linux'
        repos_dir = get_repos_path()
        expected = Path.home() / ".cache" / "gimer" / "repos"
        assert repos_dir == expected
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_repos_path_windows(self):
        self.mock_system.return_value = 'windows'
        def mock_environ_get(key, default=""):
            if key == "LOCALAPPDATA":
                return 'C:\\Users\\Test\\AppData\\Local'
            return default
        self.mock_os_environ_get.side_effect = mock_environ_get

        repos_dir = get_repos_path()
        expected = Path('C:\\Users\\Test\\AppData\\Local') / "gimer" / "cache" / "repos"
        assert repos_dir == expected
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_repos_path_unknown(self):
        self.mock_system.return_value = 'unknown'
        def mock_environ_get(key, default=""):
            if key == "TMPDIR":
                return '/tmp'
            return default
        self.mock_os_environ_get.side_effect = mock_environ_get

        repos_dir = get_repos_path()
        expected = Path('/tmp') / "gimer" / "repos"
        assert repos_dir == expected
        self.mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_github_repo_path(self):
        repo_url = "https://github.com/user/repo.git"
        repo_path = get_github_repo_path(repo_url)
        expected = get_repos_path() / "github.com" / "user" / "repo"
        assert repo_path == expected
        self.mock_mkdir.assert_called_with(parents=True, exist_ok=True)
