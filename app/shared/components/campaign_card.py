"""
Interactive campaign card component for displaying campaign information.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel

from app.models.campaign import Campaign
from app.shared.components.card_components import (
    DEFAULT_AVATAR_SATURATION,
    DEFAULT_AVATAR_VALUE,
    CardEventMixin,
    create_avatar_label,
    create_card_layout,
    create_info_label,
    generate_color_from_name,
    setup_card_widget,
)


class CampaignCard(QFrame, CardEventMixin):
    """Interactive card for displaying campaign information."""

    campaign_selected = Signal(Campaign)

    # Campaign-specific color settings
    CAMPAIGN_COLOR_SATURATION = DEFAULT_AVATAR_SATURATION
    CAMPAIGN_COLOR_VALUE = DEFAULT_AVATAR_VALUE

    # Status indicator constants
    STATUS_INDICATOR_SIZE = (12, 12)
    STATUS_INDICATOR_SYMBOL = "●"
    STATUS_COLORS = {"active": "#4CAF50", "completed": "#2196F3", "default": "#FFC107", "none": "#9E9E9E"}
    STATUS_INDICATOR_FONT_SIZE = "12px"

    # Object names for styling
    CARD_OBJECT_NAME = "CampaignCard"
    NAME_OBJECT_NAME = "CampaignName"
    DETAILS_OBJECT_NAME = "CampaignDetails"
    DATE_OBJECT_NAME = "CampaignDate"

    # Text constants
    NO_PARAMETERS_TEXT = "No parameters defined"
    RECENTLY_CREATED_TEXT = "Recently created"
    ACCESSED_FORMAT = "Accessed %b %d, %Y"
    PARAMETERS_SINGULAR = "parameter"
    PARAMETERS_PLURAL = "parameters"

    def __init__(self, campaign: Campaign, parent=None):
        super().__init__(parent)
        self.campaign = campaign
        self._setup_ui()

    def _setup_ui(self):
        """Setup the card UI components."""
        # Apply standard card setup
        self._scale_animation = setup_card_widget(self, object_name=self.CARD_OBJECT_NAME, shadow=True, animation=True)

        # Create layout
        layout, info_layout = create_card_layout()
        self.setLayout(layout)

        # Create and add icon
        self.icon_label = self._create_campaign_icon()
        layout.addWidget(self.icon_label)

        # Create and add info labels
        self.name_label = create_info_label(self.campaign.name, self.NAME_OBJECT_NAME)
        info_layout.addWidget(self.name_label)

        self.details_label = create_info_label(self._get_campaign_details(), self.DETAILS_OBJECT_NAME)
        info_layout.addWidget(self.details_label)

        self.date_label = create_info_label(self._get_last_accessed(), self.DATE_OBJECT_NAME)
        info_layout.addWidget(self.date_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Status indicator
        self.status_indicator = self._create_status_indicator()
        layout.addWidget(self.status_indicator)

    def _create_campaign_icon(self) -> QLabel:
        """Create campaign icon/avatar."""
        color = self._get_campaign_color()
        return create_avatar_label(self.campaign.name, color)

    def _get_campaign_color(self):
        """Get a color for the campaign based on its name."""
        return generate_color_from_name(self.campaign.name, self.CAMPAIGN_COLOR_SATURATION, self.CAMPAIGN_COLOR_VALUE)

    def _get_campaign_details(self) -> str:
        """Get campaign details string."""
        if hasattr(self.campaign, "parameters") and self.campaign.parameters:
            param_count = len(self.campaign.parameters)
            param_word = self.PARAMETERS_SINGULAR if param_count == 1 else self.PARAMETERS_PLURAL
            return f"{param_count} {param_word}"
        return self.NO_PARAMETERS_TEXT

    def _get_last_accessed(self) -> str:
        """Get last accessed date string."""
        if hasattr(self.campaign, "accessed_at") and self.campaign.accessed_at:
            return self.campaign.accessed_at.strftime(self.ACCESSED_FORMAT)
        return self.RECENTLY_CREATED_TEXT

    def _create_status_indicator(self) -> QLabel:
        """Create status indicator."""
        indicator = QLabel(self.STATUS_INDICATOR_SYMBOL)
        indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        indicator.setFixedSize(*self.STATUS_INDICATOR_SIZE)

        # Set color based on campaign status
        if hasattr(self.campaign, "status") and self.campaign.status:
            color = self.STATUS_COLORS.get(self.campaign.status, self.STATUS_COLORS["default"])
        else:
            color = self.STATUS_COLORS["none"]

        indicator.setStyleSheet(f"color: {color}; font-size: {self.STATUS_INDICATOR_FONT_SIZE};")
        return indicator

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.campaign_selected.emit(self.campaign)
        super().mousePressEvent(event)
