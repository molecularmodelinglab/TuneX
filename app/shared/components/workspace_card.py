"""
Interactive workspace card component for displaying workspace information.
"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame

from app.core.settings import Workspace
from app.shared.components.card_components import (
    CardEventMixin,
    create_avatar_label,
    create_card_layout,
    create_info_label,
    generate_color_from_name,
    setup_card_widget,
)


class WorkspaceCard(QFrame, CardEventMixin):
    """Interactive card for displaying workspace information."""

    workspace_selected = Signal(str)  # Emits the workspace path

    # Workspace-specific color settings (different from campaigns)
    WORKSPACE_COLOR_SATURATION = 160
    WORKSPACE_COLOR_VALUE = 200

    # Object names for styling
    CARD_OBJECT_NAME = "WorkspaceCard"
    NAME_OBJECT_NAME = "WorkspaceName"
    DETAILS_OBJECT_NAME = "WorkspaceDetails"
    DATE_OBJECT_NAME = "WorkspaceDate"

    # Text constants
    NEVER_ACCESSED_TEXT = "Never accessed"
    ACCESSED_FORMAT = "Accessed %b %d, %Y"
    PATH_PREFIX = "Path: "
    FALLBACK_INITIAL = "W"

    def __init__(self, workspace: Workspace, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self._setup_ui()

    def _setup_ui(self):
        """Setup the card UI components."""
        # Apply standard card setup
        self._scale_animation = setup_card_widget(self, object_name=self.CARD_OBJECT_NAME, shadow=True, animation=True)

        # Create layout
        layout, info_layout = create_card_layout()
        self.setLayout(layout)

        # Create and add icon
        self.icon_label = self._create_workspace_icon()
        layout.addWidget(self.icon_label)

        # Create and add info labels
        self.name_label = create_info_label(self.workspace.name, self.NAME_OBJECT_NAME)
        info_layout.addWidget(self.name_label)

        self.details_label = create_info_label(self._get_workspace_details(), self.DETAILS_OBJECT_NAME)
        info_layout.addWidget(self.details_label)

        self.date_label = create_info_label(self._get_last_accessed(), self.DATE_OBJECT_NAME)
        info_layout.addWidget(self.date_label)

        layout.addLayout(info_layout)
        layout.addStretch()

    def _create_workspace_icon(self):
        """Create workspace icon/avatar."""
        color = self._get_workspace_color()
        initial = self.workspace.name[0].upper() if self.workspace.name else self.FALLBACK_INITIAL
        return create_avatar_label(initial, color)

    def _get_workspace_color(self):
        """Get a color for the workspace based on its name."""
        return generate_color_from_name(
            self.workspace.name, self.WORKSPACE_COLOR_SATURATION, self.WORKSPACE_COLOR_VALUE
        )

    def _get_workspace_details(self) -> str:
        """Get workspace details string."""
        return f"{self.PATH_PREFIX}{os.path.basename(self.workspace.path)}"

    def _get_last_accessed(self) -> str:
        """Get last accessed date string."""
        if self.workspace.accessed_at:
            return self.workspace.accessed_at.strftime(self.ACCESSED_FORMAT)
        return self.NEVER_ACCESSED_TEXT

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.workspace_selected.emit(self.workspace.path)
        super().mousePressEvent(event)
