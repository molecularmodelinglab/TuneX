"""
Manages persistent application settings.
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from PySide6.QtCore import QStandardPaths

from app.models.workspace import Workspace

RECENT_WORKSPACE_COUNT = 5
APP_NAME = "BASIL"
SETTINGS_FILENAME = "settings.json"
LAST_WORKSPACE_KEY = "last_workspace_path"
RECENT_WORKSPACES_KEY = "recent_workspaces"


def _get_settings_path() -> str:
    """
    Determines the platform-specific path for the settings file.
    Example: C:/Users/<user>/AppData/Local/BASIL/BASIL/settings.json
    """
    config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    # QStandardPaths may add the app name, so we ensure our folder is there
    app_config_dir = os.path.join(config_dir, APP_NAME)
    os.makedirs(app_config_dir, exist_ok=True)
    return os.path.join(app_config_dir, SETTINGS_FILENAME)


def _read_settings() -> dict:
    """Reads the contents of the settings file."""
    settings_path = _get_settings_path()
    if not os.path.exists(settings_path):
        return {}
    try:
        with open(settings_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _write_settings(settings: dict):
    """Writes a dictionary to the settings file."""
    settings_path = _get_settings_path()
    logger = logging.getLogger(__name__)
    try:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        logger.error(f"Error writing settings: {e}")


def _load_workspaces_from_settings(settings: dict) -> List[Workspace]:
    """Load and convert workspace data from settings dict."""
    workspace_data = settings.get(RECENT_WORKSPACES_KEY, [])
    workspaces = []

    for item in workspace_data:
        if isinstance(item, dict):
            workspace = Workspace.from_dict(item)
        else:
            continue

        workspaces.append(workspace)

    return workspaces


def _save_workspaces_to_settings(settings: dict, workspaces: List[Workspace]):
    """Save workspace objects to settings dict."""
    settings[RECENT_WORKSPACES_KEY] = [workspace.to_dict() for workspace in workspaces]


def _update_recent_workspaces(settings: dict, workspace_path: str):
    """Updates recent workspace list with time-based sorting."""
    workspaces = _load_workspaces_from_settings(settings)
    now = datetime.now()

    # Remove existing entry if present
    workspaces = [w for w in workspaces if w.path != workspace_path]

    # Insert new/updated workspace at front
    workspaces.insert(0, Workspace(path=workspace_path, accessed_at=now))

    # Trim to limit
    workspaces = workspaces[:RECENT_WORKSPACE_COUNT]

    _save_workspaces_to_settings(settings, workspaces)


def save_last_workspace(path: str):
    """Saves the path of the last used workspace and updates recent list."""
    settings = _read_settings()
    settings[LAST_WORKSPACE_KEY] = path
    _update_recent_workspaces(settings, path)
    _write_settings(settings)


def get_last_workspace() -> Optional[str]:
    """Retrieves the path of the last used workspace."""
    settings = _read_settings()
    return settings.get(LAST_WORKSPACE_KEY)


def get_recent_workspaces() -> List[Workspace]:
    """Retrieves the list of recent workspaces, sorted by access time (most recent first)."""
    settings = _read_settings()
    workspaces = _load_workspaces_from_settings(settings)
    return workspaces[:RECENT_WORKSPACE_COUNT]


def get_recent_workspace_paths() -> List[str]:
    """Retrieves just the paths of recent workspaces for backward compatibility."""
    workspaces = get_recent_workspaces()
    return [workspace.path for workspace in workspaces]
