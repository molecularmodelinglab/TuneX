from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QStyle, QVBoxLayout

from app.core.base import BaseWidget
from app.models.campaign import Campaign
from app.shared.components.campaign_card import CampaignCard
from app.shared.components.cards import EmptyStateCard
from app.shared.styles.theme import get_widget_styles


class RecentCampaignsWidget(BaseWidget):
    """
    Widget to display a list of recent campaigns.
    """

    campaign_selected = Signal(Campaign)

    NO_RECENT_CAMPAIGNS_TEXT = "No recent campaigns"
    NO_RECENT_CAMPAIGNS_SUBTEXT = "Browse or create a new one"
    CAMPAIGN_LABEL_STYLESHEET = "padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 2px;"
    CARD_SPACING = 8
    LAYOUT_MARGINS = (0, 0, 0, 0)

    def __init__(self, parent=None):
        self.campaigns: list[Campaign] = []
        super().__init__(parent)

    def _setup_widget(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(*self.LAYOUT_MARGINS)
        self.main_layout.setSpacing(self.CARD_SPACING)
        self.setLayout(self.main_layout)

    def update_campaigns(self, campaigns: list[Campaign]):
        self.campaigns = campaigns
        self._update_display()

    def _update_display(self):
        self._clear_layout()
        if self.campaigns:
            self._show_campaigns_list()
        else:
            self._show_empty_state()
        self._apply_styles()

    def _clear_layout(self):
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_campaigns_list(self):
        recent_campaigns = sorted(self.campaigns, key=lambda x: x.updated_at or datetime.min, reverse=True)[:5]

        for campaign in recent_campaigns:
            card = CampaignCard(campaign)
            card.campaign_selected.connect(self.campaign_selected.emit)
            self.main_layout.addWidget(card)

    def _show_empty_state(self):
        icon_pixmap = self._get_folder_icon_pixmap()
        empty_state = EmptyStateCard(
            primary_message=self.NO_RECENT_CAMPAIGNS_TEXT,
            secondary_message=self.NO_RECENT_CAMPAIGNS_SUBTEXT,
            icon_pixmap=icon_pixmap,
        )
        self.main_layout.addWidget(empty_state)

    def _get_folder_icon_pixmap(self) -> QPixmap:
        style = self.style()
        icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        return icon.pixmap(64, 64)

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
