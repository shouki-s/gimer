import os
from pathlib import Path
from unittest.mock import patch

from gimer.cache import get_cache_dir, get_repo_cache_path


def test_get_cache_dir_macos():
    with patch('platform.system', return_value='Darwin'):
        cache_dir = get_cache_dir()
        expected = Path.home() / "Library" / "Caches" / "gimer" / "repos"
        assert cache_dir == expected
        assert cache_dir.exists()

def test_get_cache_dir_linux():
    with patch('platform.system', return_value='Linux'):
        cache_dir = get_cache_dir()
        expected = Path.home() / ".cache" / "gimer" / "repos"
        assert cache_dir == expected
        assert cache_dir.exists()

def test_get_cache_dir_windows():
    with patch('platform.system', return_value='Windows'):
        with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'}):
            cache_dir = get_cache_dir()
            expected = Path('C:\\Users\\Test\\AppData\\Local') / "gimer" / "cache" / "repos"
            assert cache_dir == expected
            assert cache_dir.exists()

def test_get_cache_dir_unknown():
    with patch('platform.system', return_value='Unknown'):
        with patch.dict(os.environ, {'TMPDIR': '/tmp'}):
            cache_dir = get_cache_dir()
            expected = Path('/tmp') / "gimer" / "repos"
            assert cache_dir == expected
            assert cache_dir.exists()

def test_get_repo_cache_path():
    repo_url = "https://github.com/user/repo.git"
    cache_path = get_repo_cache_path(repo_url)
    expected = get_cache_dir() / "repo"
    assert cache_path == expected
