"""
Select workspace screen for TuneX application
"""

import json
import os
from datetime import datetime

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QSizePolicy, QVBoxLayout, QWidget

from app.core.base import BaseScreen
from app.shared.components.buttons import PrimaryButton
from app.shared.components.headers import MainHeader
from app.shared.constants import WorkspaceConstants
from app.shared.styles.theme import get_widget_styles


class SelectWorkspaceScreen(BaseScreen):
    """
    Select workspace screen for TuneX application
    """

    # Signals for navigation
    workspace_selected = pyqtSignal(str)

    # UI Text
    WINDOW_TITLE = "TuneX - Select Workspace"
    HEADER_TEXT = "TuneX"
    SELECT_WORKSPACE_BUTTON_TEXT = "Select workspace"
    SELECT_WORKSPACE_FOLDER_TEXT = "Select Workspace Folder"
    CREATE_WORKSPACE_TEXT = "Create Workspace"
    FOLDER_NOT_EMPTY_TEXT = "The selected folder is not empty.\nCreate workspace here anyway?"
    ERROR_TEXT = "Error"
    FAILED_TO_CREATE_WORKSPACE_TEXT = "Failed to create workspace:\n{}"
    WORKSPACE_SELECTED_TEXT = "Workspace selected: {}"

    # UI Identifiers
    SELECT_WORKSPACE_BUTTON_ID = "SelectWorkspaceButton"

    # Workspace Configuration
    WORKSPACE_CONFIG_NAME = "name"
    WORKSPACE_CONFIG_CREATED = "created"
    WORKSPACE_CONFIG_VERSION = "version"
    WORKSPACE_CONFIG_VERSION_VALUE = "1.0"

    # Layout
    MARGINS = (30, 30, 30, 30)
    SPACING = 25
    BUTTON_SPACING = 15

    # Styles
    SELECT_WORKSPACE_BUTTON_STYLE = """
        /* "Select Workspace" Button */
        #{} {{
            background-color: #007BFF; /* A vibrant blue */
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
        }}
        #{}:hover {{
            background-color: #0056b3; /* Darker blue on hover */
        }}
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)

    def _setup_screen(self):
        """Setup the start screen UI."""
        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(*self.MARGINS)
        self.main_layout.setSpacing(self.SPACING)

        # Create UI sections
        self._create_header()
        self._create_action_buttons()

        # Add stretch to push content to top
        self.main_layout.addStretch()

    def _create_header(self):
        """Create the application header."""
        header = MainHeader(self.HEADER_TEXT)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_layout.addWidget(header)

    def _create_action_buttons(self):
        """Create main action buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(self.BUTTON_SPACING)

        # New Campaign button
        self.select_workspace_btn = PrimaryButton(self.SELECT_WORKSPACE_BUTTON_TEXT)
        self.select_workspace_btn.clicked.connect(self._on_select_workspace)
        self.select_workspace_btn.setObjectName(self.SELECT_WORKSPACE_BUTTON_ID)

        button_layout.addWidget(self.select_workspace_btn)

        self.main_layout.addLayout(button_layout)

    def _on_select_workspace(self):
        """Handle workspace selection."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self.SELECT_WORKSPACE_FOLDER_TEXT,
            "",  # Start home directory
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder_path:  # User didn't cancel
            self._handle_workspace_folder(folder_path)

    def _handle_workspace_folder(self, folder_path):
        """Handle the selected workspace folder."""
        workspace_file = os.path.join(folder_path, WorkspaceConstants.WORKSPACE_CONFIG_FILENAME)

        if os.path.exists(workspace_file):
            self._open_existing_workspace(folder_path)
        else:
            self._create_new_workspace(folder_path)

    def _create_new_workspace(self, folder_path):
        """Create a new workspace in the selected folder."""
        if os.listdir(folder_path):
            reply = QMessageBox.question(
                self,
                self.CREATE_WORKSPACE_TEXT,
                self.FOLDER_NOT_EMPTY_TEXT,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            workspace_config = {
                WorkspaceConstants.WORKSPACE_NAME_KEY: os.path.basename(folder_path),
                WorkspaceConstants.WORKSPACE_CREATED_KEY: datetime.now().isoformat(),
                WorkspaceConstants.WORKSPACE_VERSION_KEY: WorkspaceConstants.WORKSPACE_VERSION_VALUE,
            }

            workspace_file = os.path.join(folder_path, WorkspaceConstants.WORKSPACE_CONFIG_FILENAME)
            with open(workspace_file, "w") as f:
                json.dump(workspace_config, f, indent=2)

            campaigns_dir = os.path.join(folder_path, WorkspaceConstants.CAMPAIGNS_DIRNAME)
            os.makedirs(campaigns_dir, exist_ok=True)

            self._workspace_selected(folder_path)

        except Exception as e:
            QMessageBox.critical(self, self.ERROR_TEXT, self.FAILED_TO_CREATE_WORKSPACE_TEXT.format(e))

    def _open_existing_workspace(self, folder_path):
        """Open an existing workspace."""
        self._workspace_selected(folder_path)

    def _workspace_selected(self, folder_path):
        """Called when a workspace is successfully selected."""
        print(self.WORKSPACE_SELECTED_TEXT.format(folder_path))
        self.workspace_selected.emit(folder_path)

    def _apply_styles(self):
        """Apply screen-specific styles."""
        self.setStyleSheet(
            get_widget_styles()
            + self.SELECT_WORKSPACE_BUTTON_STYLE.format(
                self.SELECT_WORKSPACE_BUTTON_ID, self.SELECT_WORKSPACE_BUTTON_ID
            )
        )
