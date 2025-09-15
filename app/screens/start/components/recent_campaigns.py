from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from app.core.base import BaseWidget
from app.models.campaign import Campaign
from app.shared.components.campaign_card import CampaignCard
from app.shared.components.cards import EmptyStateCard
from app.shared.styles.theme import get_widget_styles


class RecentCampaignsWidget(BaseWidget):
    """
    Widget to display all campaigns with search functionality.
    """

    campaign_selected = Signal(Campaign)

    NO_RECENT_CAMPAIGNS_TEXT = "No campaigns yet"
    NO_RECENT_CAMPAIGNS_SUBTEXT = "Create your first campaign"
    NO_CAMPAIGNS_FOUND_TEXT = "No campaigns found"
    NO_CAMPAIGNS_FOUND_SUBTEXT = "Try a different search term"
    SEARCH_PLACEHOLDER_TEXT = "Search campaigns..."
    CAMPAIGN_LABEL_STYLESHEET = "padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 2px;"
    CARD_SPACING = 8
    LAYOUT_MARGINS = (0, 0, 0, 0)
    SCROLL_AREA_STYLE = """QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollArea > QWidget > QWidget {
        background: transparent;
    }"""

    def __init__(self, parent=None):
        self.campaigns: list[Campaign] = []
        self.search_term: str = ""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _setup_widget(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(*self.LAYOUT_MARGINS)
        self.main_layout.setSpacing(self.CARD_SPACING)
        self.setLayout(self.main_layout)

        # Search bar
        self._create_search_bar()
        # Campaigns
        self._create_campaigns_container()

    def _create_campaigns_container(self):
        """Create campaigns widget."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(400)

        self.scroll_area.setStyleSheet(self.SCROLL_AREA_STYLE)

        # Container widget for scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, self.CARD_SPACING, 0, self.CARD_SPACING)
        self.scroll_layout.setSpacing(self.CARD_SPACING)
        self.scroll_area.setWidget(self.scroll_content)

        # Add scroll area to main layout
        self.main_layout.addWidget(self.scroll_area)

    def _create_search_bar(self):
        """Create the search bar widget."""
        self.search_container = QWidget()
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(0, 0, 0, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.SEARCH_PLACEHOLDER_TEXT)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_input)

        self.main_layout.insertWidget(0, self.search_container)

    def _on_search_text_changed(self, text: str):
        """Handle search text changes."""
        self.search_term = text.lower()
        self._update_display()

    def update_campaigns(self, campaigns: list[Campaign]):
        self.campaigns = campaigns
        self._update_display()

    def _get_filtered_campaigns(self):
        filtered_campaigns = self.campaigns
        if self.search_term:
            filtered_campaigns = [c for c in self.campaigns if self.search_term in c.name.lower()]
        return filtered_campaigns

    def _update_display(self):
        self._clear_layout()
        filtered_campaigns = self._get_filtered_campaigns()
        if filtered_campaigns:
            self._show_campaigns_list()
        else:
            self._show_empty_state()
        self._apply_styles()

    def _clear_layout(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_campaigns_list(self):
        filtered_campaigns = self._get_filtered_campaigns()

        # Show all campaigns (sorted by accessed_at, most recent first)
        display_campaigns = sorted(filtered_campaigns, key=lambda x: x.accessed_at or datetime.min, reverse=True)

        for campaign in display_campaigns:
            card = CampaignCard(campaign)
            card.campaign_selected.connect(self.campaign_selected.emit)
            self.scroll_layout.addWidget(card)

        # Add stretch to push content to top
        self.scroll_layout.addStretch()

    def _show_empty_state(self):
        icon_pixmap = self._get_empty_campaigns_icon()

        if self.search_term:
            primary_message = self.NO_CAMPAIGNS_FOUND_TEXT
            secondary_message = self.NO_CAMPAIGNS_FOUND_SUBTEXT
        else:
            primary_message = self.NO_RECENT_CAMPAIGNS_TEXT
            secondary_message = self.NO_RECENT_CAMPAIGNS_SUBTEXT

        empty_state = EmptyStateCard(
            primary_message=primary_message,
            secondary_message=secondary_message,
            icon_pixmap=icon_pixmap,
        )
        self.scroll_layout.addWidget(empty_state)
        self.scroll_layout.addStretch()

    def _get_empty_campaigns_icon(self) -> QPixmap:
        """Get icon for empty campaigns state."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        font = QFont("Segoe UI Emoji", 25)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🚀")
        painter.end()

        return pixmap

    def _apply_styles(self):
        """Apply screen-specific styles."""
        self.setStyleSheet(
            get_widget_styles()
            + """
            /* Campaign Cards */
            #CampaignCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 0px;
            }

            #CampaignCard[hovered="true"] {
                border-color: #007BFF;
                background-color: #f8f9fa;
            }

            #CampaignName {
                font-size: 16px;
                font-weight: 600;
                color: #333333;
                margin: 0px;
            }

            #CampaignDetails {
                font-size: 13px;
                color: #666666;
                margin: 0px;
            }

            #CampaignDate {
                font-size: 12px;
                color: #999999;
                margin: 0px;
            }

            /* Existing button styles */
            #NewCampaignButton {
                background-color: #007BFF;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
            }
            #NewCampaignButton:hover {
                background-color: #0056b3;
            }

            #BrowseAllButton {
                background-color: white;
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
            }
            #BrowseAllButton:hover {
                background-color: #f0f0f0;
            }
        """
        )
