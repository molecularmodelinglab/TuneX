import json
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.core.settings import (
    APP_NAME,
    LAST_WORKSPACE_KEY,
    RECENT_WORKSPACE_COUNT,
    RECENT_WORKSPACES_KEY,
    SETTINGS_FILENAME,
    _get_settings_path,
    _read_settings,
    _update_recent_workspaces,
    _write_settings,
    get_last_workspace,
    get_recent_workspace_paths,
    get_recent_workspaces,
    save_last_workspace,
)
from app.models.workspace import Workspace


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


class TestWorkspace:
    """Test Workspace dataclass functionality."""

    def test_workspace_creation_with_auto_name(self):
        workspace = Workspace(path="/path/to/MyProject")
        assert workspace.name == "MyProject"
        assert workspace.path == "/path/to/MyProject"
        assert isinstance(workspace.accessed_at, datetime)

    def test_workspace_creation_with_explicit_name(self):
        workspace = Workspace(path="/path/to/folder", name="Custom Name")
        assert workspace.name == "Custom Name"
        assert workspace.path == "/path/to/folder"

    def test_workspace_from_dict(self):
        data = {"path": "/test/path", "name": "Test Workspace", "accessed_at": "2024-12-15T10:30:00"}
        workspace = Workspace.from_dict(data)
        assert workspace.path == "/test/path"
        assert workspace.name == "Test Workspace"
        assert workspace.accessed_at == datetime.fromisoformat("2024-12-15T10:30:00")

    def test_workspace_to_dict(self):
        workspace = Workspace(path="/test/path", name="Test Workspace", accessed_at=datetime(2024, 12, 15, 10, 30, 0))
        result = workspace.to_dict()
        expected = {"path": "/test/path", "name": "Test Workspace", "accessed_at": "2024-12-15T10:30:00"}
        assert result == expected


class TestUpdateRecentWorkspaces:
    """Test updating recent workspaces."""

    def test_update_recent_workspaces_empty_settings(self):
        settings = {}
        path = "/path/to/workspace"

        _update_recent_workspaces(settings, path)

        assert RECENT_WORKSPACES_KEY in settings
        workspaces = settings[RECENT_WORKSPACES_KEY]
        assert len(workspaces) == 1
        assert workspaces[0]["path"] == path
        assert workspaces[0]["name"] == "workspace"

    def test_update_recent_workspaces_new_path(self):
        # Create settings with existing workspace
        existing_workspace = Workspace(path="/old/path", name="old").to_dict()
        settings = {RECENT_WORKSPACES_KEY: [existing_workspace]}
        new_path = "/new/path"

        _update_recent_workspaces(settings, new_path)

        workspaces = settings[RECENT_WORKSPACES_KEY]
        assert len(workspaces) == 2
        assert workspaces[0]["path"] == new_path  # Most recent first
        assert workspaces[1]["path"] == "/old/path"

    def test_update_recent_workspaces_existing_path_updates_time(self):
        # Create settings with existing workspaces
        old_time = datetime(2024, 1, 1, 12, 0, 0)
        workspace1 = Workspace(path="/path1", accessed_at=old_time).to_dict()
        workspace2 = Workspace(path="/path2", accessed_at=old_time).to_dict()
        settings = {RECENT_WORKSPACES_KEY: [workspace1, workspace2]}

        _update_recent_workspaces(settings, "/path2")

        workspaces = settings[RECENT_WORKSPACES_KEY]
        assert len(workspaces) == 2
        assert workspaces[0]["path"] == "/path2"  # Moved to front
        # Time should be updated (newer than old_time)
        updated_time = datetime.fromisoformat(workspaces[0]["accessed_at"])
        assert updated_time > old_time

    def test_update_recent_workspaces_exceeds_limit(self):
        # Create settings at the limit
        initial_workspaces = []
        for i in range(RECENT_WORKSPACE_COUNT):
            ws = Workspace(path=f"/path{i}", name=f"path{i}").to_dict()
            initial_workspaces.append(ws)

        settings = {RECENT_WORKSPACES_KEY: initial_workspaces}
        new_path = "/new/path"

        _update_recent_workspaces(settings, new_path)

        workspaces = settings[RECENT_WORKSPACES_KEY]
        assert len(workspaces) == RECENT_WORKSPACE_COUNT
        assert workspaces[0]["path"] == new_path  # New path at front

        # Check that we have the correct number of items
        paths = [ws["path"] for ws in workspaces]
        assert new_path in paths
        # The new path should be first due to sorting by accessed_at
        assert paths[0] == new_path


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

        # Check that workspace was added to recent list
        workspaces = written_settings[RECENT_WORKSPACES_KEY]
        assert len(workspaces) == 1
        assert workspaces[0]["path"] == path

    @patch("app.core.settings._write_settings")
    @patch("app.core.settings._read_settings")
    def test_save_last_workspace_existing_settings(self, mock_read, mock_write):
        old_workspace = Workspace(path="/old/workspace", name="old").to_dict()
        existing_settings = {
            LAST_WORKSPACE_KEY: "/old/workspace",
            RECENT_WORKSPACES_KEY: [old_workspace],
        }
        mock_read.return_value = existing_settings
        new_path = "/new/workspace"

        save_last_workspace(new_path)

        # Verify write_settings was called
        mock_write.assert_called_once()
        written_settings = mock_write.call_args[0][0]
        assert written_settings[LAST_WORKSPACE_KEY] == new_path
        assert written_settings[RECENT_WORKSPACES_KEY][0]["path"] == new_path


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
        workspace_dicts = [
            Workspace(path="/path1", name="path1").to_dict(),
            Workspace(path="/path2", name="path2").to_dict(),
            Workspace(path="/path3", name="path3").to_dict(),
        ]
        mock_read.return_value = {RECENT_WORKSPACES_KEY: workspace_dicts}

        result = get_recent_workspaces()

        assert len(result) == 3
        assert all(isinstance(ws, Workspace) for ws in result)
        assert result[0].path == "/path1"
        assert result[1].path == "/path2"
        assert result[2].path == "/path3"

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspaces_not_exists(self, mock_read):
        mock_read.return_value = {}

        result = get_recent_workspaces()
        assert result == []

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspaces_handles_legacy_format(self, mock_read):
        # Test that the current implementation handles empty results gracefully
        # (Your current settings.py doesn't support legacy string format)
        mock_read.return_value = {RECENT_WORKSPACES_KEY: ["/path1", "/path2"]}

        result = get_recent_workspaces()

        # Current implementation should return empty list since it only handles dict format
        assert len(result) == 0

    @patch("app.core.settings._read_settings")
    def test_get_recent_workspace_paths_backward_compatibility(self, mock_read):
        workspace_dicts = [
            Workspace(path="/path1", name="Workspace1").to_dict(),
            Workspace(path="/path2", name="Workspace2").to_dict(),
        ]
        mock_read.return_value = {RECENT_WORKSPACES_KEY: workspace_dicts}

        result = get_recent_workspace_paths()
        assert result == ["/path1", "/path2"]


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
                workspaces = get_recent_workspaces()
                assert len(workspaces) == 1
                assert workspaces[0].path == "/first/workspace"

                # Save second workspace
                save_last_workspace("/second/workspace")

                # Verify order (most recent first)
                assert get_last_workspace() == "/second/workspace"
                workspaces = get_recent_workspaces()
                assert len(workspaces) == 2
                assert workspaces[0].path == "/second/workspace"
                assert workspaces[1].path == "/first/workspace"

                # Save first workspace again (should move to top)
                save_last_workspace("/first/workspace")

                assert get_last_workspace() == "/first/workspace"
                workspaces = get_recent_workspaces()
                assert workspaces[0].path == "/first/workspace"
                assert workspaces[1].path == "/second/workspace"

    def test_recent_workspaces_limit_integration(self):
        """Test that recent workspaces respect the limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")

            with patch("app.core.settings._get_settings_path", return_value=settings_path):
                # Add more workspaces than the limit
                for i in range(RECENT_WORKSPACE_COUNT + 3):
                    save_last_workspace(f"/workspace{i}")

                workspaces = get_recent_workspaces()

                # Should only have the limit number of workspaces
                assert len(workspaces) == RECENT_WORKSPACE_COUNT
                # Should have the most recent ones (sorted by access time)
                assert workspaces[0].path == f"/workspace{RECENT_WORKSPACE_COUNT + 2}"


@pytest.mark.parametrize(
    "initial_workspace_paths, new_path, expected_first_path",
    [
        # Empty list
        ([], "/new", "/new"),
        # New path at front
        (["/old"], "/new", "/new"),
        # Move existing to front
        (["/a", "/b", "/c"], "/b", "/b"),
    ],
)
def test_update_recent_workspaces_parametrized(initial_workspace_paths, new_path, expected_first_path):
    """Parametrized tests for recent workspace updates."""
    # Convert paths to workspace dicts
    initial_workspaces = [
        Workspace(path=path, name=os.path.basename(path)).to_dict() for path in initial_workspace_paths
    ]
    settings = {RECENT_WORKSPACES_KEY: initial_workspaces}

    _update_recent_workspaces(settings, new_path)

    workspaces = settings[RECENT_WORKSPACES_KEY]
    assert workspaces[0]["path"] == expected_first_path
    assert len(workspaces) <= RECENT_WORKSPACE_COUNT
