"""
Interactive campaign card component for displaying campaign information.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout

from app.models.campaign import Campaign


class CampaignCard(QFrame):
    """Interactive card for displaying campaign information."""

    campaign_selected = Signal(Campaign)

    def __init__(self, campaign: Campaign, parent=None):
        super().__init__(parent)
        self.campaign = campaign
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

        self.icon_label = self._create_campaign_icon()
        layout.addWidget(self.icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        self.name_label = QLabel(self.campaign.name)
        self.name_label.setObjectName("CampaignName")
        info_layout.addWidget(self.name_label)

        self.details_label = QLabel(self._get_campaign_details())
        self.details_label.setObjectName("CampaignDetails")
        info_layout.addWidget(self.details_label)

        self.date_label = QLabel(self._get_last_accessed())
        self.date_label.setObjectName("CampaignDate")
        info_layout.addWidget(self.date_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Status indicator
        self.status_indicator = self._create_status_indicator()
        layout.addWidget(self.status_indicator)

    def _create_campaign_icon(self) -> QLabel:
        """Create campaign icon/avatar."""
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._get_campaign_color()
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawEllipse(4, 4, 56, 56)

        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(painter.font())
        font = painter.font()
        font.setPixelSize(24)
        font.setBold(True)
        painter.setFont(font)

        initial = self.campaign.name[0].upper() if self.campaign.name else "C"
        painter.drawText(4, 4, 56, 56, Qt.AlignmentFlag.AlignCenter, initial)
        painter.end()

        icon_label.setPixmap(pixmap)
        return icon_label

    def _get_campaign_color(self) -> QColor:
        """Get a color for the campaign based on its name."""
        # Simple hash-based color generation
        hash_value = hash(self.campaign.name) % 360
        return QColor.fromHsv(hash_value, 180, 220)

    def _get_campaign_details(self) -> str:
        """Get campaign details string."""
        if hasattr(self.campaign, "parameters") and self.campaign.parameters:
            param_count = len(self.campaign.parameters)
            return f"{param_count} parameter{'s' if param_count != 1 else ''}"
        return "No parameters defined"

    def _get_last_accessed(self) -> str:
        """Get last accessed date string."""
        if hasattr(self.campaign, "accessed_at") and self.campaign.accessed_at:
            return f"Accessed {self.campaign.accessed_at.strftime('%b %d, %Y')}"
        return "Recently created"

    def _create_status_indicator(self) -> QLabel:
        """Create status indicator."""
        indicator = QLabel("●")
        indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        indicator.setFixedSize(12, 12)

        # Set color based on campaign status
        if hasattr(self.campaign, "status"):
            if self.campaign.status == "active":
                color = "#4CAF50"
            elif self.campaign.status == "completed":
                color = "#2196F3"
            else:
                color = "#FFC107"
        else:
            color = "#9E9E9E"

        indicator.setStyleSheet(f"color: {color}; font-size: 12px;")
        return indicator

    def _setup_styling(self):
        """Setup card styling."""
        self.setObjectName("CampaignCard")

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
            self.campaign_selected.emit(self.campaign)
        super().mousePressEvent(event)
