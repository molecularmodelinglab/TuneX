"""
Reusable card components for TuneX application.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class Card(QFrame):
    """Basic card container with consistent styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFrameStyle(QFrame.Shape.StyledPanel)


class EmptyStateCard(QFrame):
    """Card displaying empty state with icon and message."""

    def __init__(
        self,
        primary_message: str = "No items found",
        secondary_message: str = "Try a different action",
        icon_pixmap: QPixmap = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("EmptyStateCard")
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # Add icon if provided
        if icon_pixmap:
            icon_label = QLabel()
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        # Primary message
        primary_label = QLabel(primary_message)
        primary_label.setObjectName("PrimaryMessage")
        primary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        primary_label.setStyleSheet("""
            QLabel#PrimaryMessage {
                font-size: 18px;
                font-weight: bold;
                color: #555555;
            }
        """)
        layout.addWidget(primary_label)

        # Secondary message
        secondary_label = QLabel(secondary_message)
        secondary_label.setObjectName("SecondaryMessage")
        secondary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        secondary_label.setStyleSheet("""
            QLabel#SecondaryMessage {
                font-size: 14px;
                color: #888888;
            }
        """)
        layout.addWidget(secondary_label)
