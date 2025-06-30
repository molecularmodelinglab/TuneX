from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QStyle, QVBoxLayout

from app.core.base import BaseWidget
from app.models.campaign import Campaign
from app.shared.components.cards import EmptyStateCard


class RecentCampaignsWidget(BaseWidget):
    """
    Widget to display a list of recent campaigns.
    """

    NO_RECENT_CAMPAIGNS_TEXT = "No recent campaigns"
    NO_RECENT_CAMPAIGNS_SUBTEXT = "Browse or create a new one"
    CAMPAIGN_LABEL_STYLESHEET = "padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 2px;"
    LAYOUT_MARGINS = (0, 0, 0, 0)

    def __init__(self, parent=None):
        self.campaigns: list[Campaign] = []
        super().__init__(parent)

    def _setup_widget(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(*self.LAYOUT_MARGINS)
        self.setLayout(self.main_layout)

    def _apply_styles(self):
        """Apply styles to the campaign labels."""
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet(self.CAMPAIGN_LABEL_STYLESHEET)

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
        for campaign in self.campaigns:
            label = QLabel(f"{campaign.name}")
            self.main_layout.addWidget(label)

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
