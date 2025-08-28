"""
Manages persistent application settings.
"""

import json
import os
from typing import Optional

from PySide6.QtCore import QStandardPaths

APP_NAME = "TuneX"
SETTINGS_FILENAME = "settings.json"
LAST_WORKSPACE_KEY = "last_workspace_path"


def _get_settings_path() -> str:
    """
    Determines the platform-specific path for the settings file.
    Example: C:/Users/<user>/AppData/Local/TuneX/TuneX/settings.json
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
    try:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        print(f"Error writing settings: {e}")


def save_last_workspace(path: str):
    """Saves the path of the last used workspace."""
    settings = _read_settings()
    settings[LAST_WORKSPACE_KEY] = path
    _write_settings(settings)


def get_last_workspace() -> Optional[str]:
    """Retrieves the path of the last used workspace."""
    settings = _read_settings()
    return settings.get(LAST_WORKSPACE_KEY)