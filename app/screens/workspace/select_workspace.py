"""
Select workspace screen for TuneX application
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseScreen
from app.shared.components.buttons import PrimaryButton
from app.shared.components.headers import MainHeader
from app.shared.styles.theme import get_widget_styles


class SelectWorkspaceScreen(BaseScreen):
    """
    Select workspace screen for TuneX application
    """

    WINDOW_TITLE = "TuneX - Select Workspace"
    HEADER_TEXT = "TuneX"
    SELECT_WORKSPACE_BUTTON_TEXT = "Select workspace"
    MARGINS = (30, 30, 30, 30)
    SPACING = 25
    BUTTON_SPACING = 15

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
        self.select_workspace_btn.setObjectName("SelectWorkspaceButton")

        button_layout.addWidget(self.select_workspace_btn)

        self.main_layout.addLayout(button_layout)

    def _apply_styles(self):
        """Apply screen-specific styles."""
        self.setStyleSheet(
            get_widget_styles()
            + """
            /* "Select Workspace" Button */
            #SelectWorkspaceButton {
                background-color: #007BFF; /* A vibrant blue */
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
            }
            #SelectWorkspaceButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
            }
        """
        )
