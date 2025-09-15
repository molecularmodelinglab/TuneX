import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from app.core.settings import (
    APP_NAME,
    LAST_WORKSPACE_KEY,
    RECENT_WORKSPACE_COUNT,
    RECENT_WORKSPACE_PATHS_KEY,
    SETTINGS_FILENAME,
    _get_settings_path,
    _read_settings,
    _update_recent_workspace_paths,
    _write_settings,
    get_last_workspace,
    get_recent_workspaces,
    save_last_workspace,
)


class TestSettingsPath:
    """Test settings path generation."""

    @patch("app.core.settings.QStandardPaths.writableLocation")
    @patch("app.core.settings.os.makedirs")
    def test_get_settings_path_creates_directory(self, mock_makedirs, mock_writable_location):
        mock_writable_location.return_value = "/mock/config"

        result = _get_settings_path()

        expected_dir = os.path.join("/mock/config", APP_NAME)
        expected_path = os.path.join(expected_dir, SETTINGS_FILENAME)

        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        assert result == expected_path

    @patch("app.core.settings.QStandardPaths.writableLocation")
    def test_get_settings_path_integration(self, mock_writable_location):
        """Test path generation with actual file system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_writable_location.return_value = temp_dir

            result = _get_settings_path()
            expected_path = os.path.join(temp_dir, APP_NAME, SETTINGS_FILENAME)

            assert result == expected_path
            assert os.path.exists(os.path.dirname(result))


class TestReadSettings:
    """Test reading settings from file."""

    def test_read_settings_file_not_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("app.core.settings._get_settings_path", return_value=os.path.join(temp_dir, "nonexistent.json")):
                result = _read_settings()
                assert result == {}

    def test_read_settings_valid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            test_data = {"key": "value", "number": 42}

            with open(settings_path, "w") as f:
                json.dump(test_data, f)

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                result = _read_settings()
                assert result == test_data

    def test_read_settings_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")

            with open(settings_path, "w") as f:
                f.write("invalid json content {")

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                result = _read_settings()
                assert result == {}

    def test_read_settings_io_error(self):
        with patch("app.core.settings._get_settings_path", return_value="/invalid/path/settings.json"):
            with patch("app.core.settings.os.path.exists", return_value=True):
                result = _read_settings()
                assert result == {}


class TestWriteSettings:
    """Test writing settings to file."""

    def test_write_settings_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            test_data = {"test_key": "test_value", "numbers": [1, 2, 3]}

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                _write_settings(test_data)

            # Verify file was written correctly
            with open(settings_path, "r") as f:
                saved_data = json.load(f)
            assert saved_data == test_data

    def test_write_settings_formatting(self):
        """Test that settings are written with proper indentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            test_data = {"nested": {"key": "value"}}

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                _write_settings(test_data)

            with open(settings_path, "r") as f:
                content = f.read()
            # Check that it's formatted with indentation
            assert "{\n  " in content

    @patch("app.core.settings._get_settings_path")
    @patch("app.core.settings.logging.getLogger")
    def test_write_settings_io_error(self, mock_logger, mock_get_path):
        mock_get_path.return_value = "/invalid/path/settings.json"
        mock_log = Mock()
        mock_logger.return_value = mock_log

        _write_settings({"test": "data"})

        # Verify error was logged
        mock_log.error.assert_called_once()
        assert "Error writing settings" in str(mock_log.error.call_args)


class TestUpdateRecentWorkspacePaths:
    """Test updating recent workspace paths."""

    def test_update_recent_workspace_paths_empty_settings(self):
        settings = {}
        path = "/path/to/workspace"

        _update_recent_workspace_paths(settings, path)

        assert RECENT_WORKSPACE_PATHS_KEY in settings
        assert settings[RECENT_WORKSPACE_PATHS_KEY] == [path]

    def test_update_recent_workspace_paths_new_path(self):
        settings = {RECENT_WORKSPACE_PATHS_KEY: ["/old/path"]}
        new_path = "/new/path"

        _update_recent_workspace_paths(settings, new_path)

        expected = [new_path, "/old/path"]
        assert settings[RECENT_WORKSPACE_PATHS_KEY] == expected

    def test_update_recent_workspace_paths_existing_path_moves_to_top(self):
        settings = {RECENT_WORKSPACE_PATHS_KEY: ["/path1", "/path2", "/path3"]}
        existing_path = "/path2"

        _update_recent_workspace_paths(settings, existing_path)

        expected = ["/path2", "/path1", "/path3"]
        assert settings[RECENT_WORKSPACE_PATHS_KEY] == expected

    def test_update_recent_workspace_paths_exceeds_limit(self):
        # Create a list at the limit
        initial_paths = [f"/path{i}" for i in range(RECENT_WORKSPACE_COUNT)]
        settings = {RECENT_WORKSPACE_PATHS_KEY: initial_paths.copy()}
        new_path = "/new/path"

        _update_recent_workspace_paths(settings, new_path)

        # Should have new path at front and last item removed
        expected = [new_path] + initial_paths[:-1]
        assert settings[RECENT_WORKSPACE_PATHS_KEY] == expected
        assert len(settings[RECENT_WORKSPACE_PATHS_KEY]) == RECENT_WORKSPACE_COUNT

    def test_update_recent_workspace_paths_existing_path_at_limit(self):
        # Test moving existing path to top when at limit
        initial_paths = [f"/path{i}" for i in range(RECENT_WORKSPACE_COUNT)]
        settings = {RECENT_WORKSPACE_PATHS_KEY: initial_paths.copy()}
        existing_path = initial_paths[2]  # Move middle item to front

        _update_recent_workspace_paths(settings, existing_path)

        # Should move existing path to front, no items should be lost
        expected = [existing_path] + [p for p in initial_paths if p != existing_path]
        assert settings[RECENT_WORKSPACE_PATHS_KEY] == expected
        assert len(settings[RECENT_WORKSPACE_PATHS_KEY]) == RECENT_WORKSPACE_COUNT


class TestSaveLastWorkspace:
    """Test saving last workspace functionality."""

    @patch("app.core.settings._write_settings")
    @patch("app.core.settings._read_settings")
    def test_save_last_workspace_empty_settings(self, mock_read, mock_write):
        mock_read.return_value = {}
        path = "/path/to/workspace"

        save_last_workspace(path)

        # Check that write_settings was called with correct data
        mock_write.assert_called_once()
        written_settings = mock_write.call_args[0][0]
        assert written_settings[LAST_WORKSPACE_KEY] == path
        assert path in written_settings[RECENT_WORKSPACE_PATHS_KEY]

    @patch("app.core.settings._write_settings")
    @patch("app.core.settings._read_settings")
    def test_save_last_workspace_existing_settings(self, mock_read, mock_write):
        existing_settings = {
            LAST_WORKSPACE_KEY: "/old/workspace",
            RECENT_WORKSPACE_PATHS_KEY: ["/old/workspace", "/another/path"],
        }
        mock_read.return_value = existing_settings
        new_path = "/new/workspace"

        save_last_workspace(new_path)

        # Verify write_settings was called
        mock_write.assert_called_once()
        written_settings = mock_write.call_args[0][0]
        assert written_settings[LAST_WORKSPACE_KEY] == new_path
        assert written_settings[RECENT_WORKSPACE_PATHS_KEY][0] == new_path


class TestGetLastWorkspace:
    """Test retrieving last workspace."""

    @patch("app.core.settings._read_settings")
    def test_get_last_workspace_exists(self, mock_read):
        path = "/path/to/workspace"
        mock_read.return_value = {LAST_WORKSPACE_KEY: path}

        result = get_last_workspace()
        assert result == path

    @patch("app.core.settings._read_settings")
    def test_get_last_workspace_not_exists(self, mock_read):
        mock_read.return_value = {}

        result = get_last_workspace()
        assert result is None

    @patch("app.core.settings._read_settings")
    def test_get_last_workspace_none_value(self, mock_read):
        mock_read.return_value = {LAST_WORKSPACE_KEY: None}

        result = get_last_workspace()
        assert result is None


class TestGetRecentWorkspaces:
    """Test retrieving recent workspaces."""

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspaces_exists(self, mock_read):
        paths = ["/path1", "/path2", "/path3"]
        mock_read.return_value = {RECENT_WORKSPACE_PATHS_KEY: paths}

        result = get_recent_workspaces()
        assert result == paths

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspaces_not_exists(self, mock_read):
        mock_read.return_value = {}

        result = get_recent_workspaces()
        assert result == []

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspaces_empty_list(self, mock_read):
        mock_read.return_value = {RECENT_WORKSPACE_PATHS_KEY: []}

        result = get_recent_workspaces()
        assert result == []


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_workflow_integration(self):
        """Test the complete save/retrieve workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                # Save first workspace
                save_last_workspace("/first/workspace")

                # Verify it was saved
                assert get_last_workspace() == "/first/workspace"
                assert get_recent_workspaces() == ["/first/workspace"]

                # Save second workspace
                save_last_workspace("/second/workspace")

                # Verify order
                assert get_last_workspace() == "/second/workspace"
                assert get_recent_workspaces() == ["/second/workspace", "/first/workspace"]

                # Save first workspace again (should move to top)
                save_last_workspace("/first/workspace")

                assert get_last_workspace() == "/first/workspace"
                assert get_recent_workspaces() == ["/first/workspace", "/second/workspace"]

    def test_recent_workspaces_limit_integration(self):
        """Test that recent workspaces respect the limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                # Add more workspaces than the limit
                for i in range(RECENT_WORKSPACE_COUNT + 3):
                    save_last_workspace(f"/workspace{i}")

                recent = get_recent_workspaces()

                # Should only have the limit number of workspaces
                assert len(recent) == RECENT_WORKSPACE_COUNT
                # Should have the most recent ones
                assert recent[0] == f"/workspace{RECENT_WORKSPACE_COUNT + 2}"
                assert recent[-1] == f"/workspace{3}"


@pytest.mark.parametrize(
    "initial_paths, new_path, expected_result",
    [
        # Empty list
        ([], "/new", ["/new"]),
        # New path at front
        (["/old"], "/new", ["/new", "/old"]),
        # Move existing to front
        (["/a", "/b", "/c"], "/b", ["/b", "/a", "/c"]),
        # Exceed limit
        (
            [f"/p{i}" for i in range(RECENT_WORKSPACE_COUNT)],
            "/new",
            ["/new"] + [f"/p{i}" for i in range(RECENT_WORKSPACE_COUNT - 1)],
        ),
    ],
)
def test_update_recent_workspace_paths_parametrized(initial_paths, new_path, expected_result):
    """Parametrized tests for recent workspace path updates."""
    settings = {RECENT_WORKSPACE_PATHS_KEY: initial_paths.copy()}

    _update_recent_workspace_paths(settings, new_path)

    assert settings[RECENT_WORKSPACE_PATHS_KEY] == expected_result
    assert len(settings[RECENT_WORKSPACE_PATHS_KEY]) <= RECENT_WORKSPACE_COUNT
