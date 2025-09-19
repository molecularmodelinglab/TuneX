"""
Interactive workspace card component for displaying workspace information.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout

from app.core.settings import Workspace


class WorkspaceCard(QFrame):
    """Interactive card for displaying workspace information."""

    workspace_selected = Signal(str)

    def __init__(self, workspace: Workspace, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self._hover_effect = None
        self._setup_ui()
        self._setup_styling()
        self._setup_animations()

    def _setup_ui(self):
        """Setup the card UI components."""
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.icon_label = self._create_workspace_icon()
        layout.addWidget(self.icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        self.name_label = QLabel(self.workspace.name)
        self.name_label.setObjectName("WorkspaceName")
        info_layout.addWidget(self.name_label)

        self.details_label = QLabel(self._get_workspace_details())
        self.details_label.setObjectName("WorkspaceDetails")
        info_layout.addWidget(self.details_label)

        self.date_label = QLabel(self._get_last_accessed())
        self.date_label.setObjectName("WorkspaceDate")
        info_layout.addWidget(self.date_label)

        layout.addLayout(info_layout)
        layout.addStretch()

    def _create_workspace_icon(self) -> QLabel:
        """Create workspace icon/avatar."""
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._get_workspace_color()
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawEllipse(4, 4, 56, 56)

        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(painter.font())
        font = painter.font()
        font.setPixelSize(24)
        font.setBold(True)
        painter.setFont(font)

        initial = self.workspace.name[0].upper() if self.workspace.name else "W"
        painter.drawText(4, 4, 56, 56, Qt.AlignmentFlag.AlignCenter, initial)
        painter.end()

        icon_label.setPixmap(pixmap)
        return icon_label

    def _get_workspace_color(self) -> QColor:
        """Get a color for the workspace based on its name."""
        # Simple hash-based color generation with workspace-appropriate colors
        hash_value = hash(self.workspace.name) % 360
        # Use slightly different saturation/value for distinction from campaigns
        return QColor.fromHsv(hash_value, 160, 200)

    def _get_workspace_details(self) -> str:
        """Get workspace details string."""
        return f"Path: {self.workspace.path}"

    def _get_last_accessed(self) -> str:
        """Get last accessed date string."""
        if self.workspace.accessed_at:
            return f"Accessed {self.workspace.accessed_at.strftime('%b %d, %Y')}"
        return "Never accessed"

    def _setup_styling(self):
        """Setup card styling."""
        self.setObjectName("WorkspaceCard")

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def _setup_animations(self):
        """Setup hover animations."""
        self._scale_animation = QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(150)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.workspace_selected.emit(self.workspace.path)
        super().mousePressEvent(event)
