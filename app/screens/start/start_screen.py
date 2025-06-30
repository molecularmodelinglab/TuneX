"""
Start screen for TuneX application.
Main entry point showing welcome UI and navigation to other screens.
"""

from typing import List

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseScreen
from app.models.campaign import Campaign
from app.screens.start.components.campaign_loader import CampaignLoader
from app.screens.start.components.recent_campaigns import RecentCampaignsWidget
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.headers import MainHeader, SectionHeader
from app.shared.styles.theme import get_widget_styles


class StartScreen(BaseScreen):
    """
    Main start screen for TuneX application.

    Displays welcome UI with options to create new campaigns
    or browse existing ones.
    """

    # Signals for navigation
    new_campaign_requested = pyqtSignal()
    browse_campaigns_requested = pyqtSignal()

    WINDOW_TITLE = "TuneX - Welcome"
    HEADER_TEXT = "TuneX"
    NEW_CAMPAIGN_BUTTON_TEXT = "+ New Campaign"
    BROWSE_CAMPAIGNS_BUTTON_TEXT = "Browse All"
    RECENT_CAMPAIGNS_HEADER_TEXT = "Recently Opened Campaigns"
    MARGINS = (30, 30, 30, 30)
    SPACING = 25
    BUTTON_SPACING = 15

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.campaigns: List[Campaign] = []
        self.loader: CampaignLoader | None = None
        self._update_campaigns_display()

    def set_workspace(self, workspace_path: str):
        """Set workspace and refresh campaigns."""
        self.workspace_path = workspace_path
        self.loader = CampaignLoader(workspace_path)
        self._refresh_campaigns()

    def _refresh_campaigns(self):
        """Load campaigns and update display."""
        if not self.loader:
            return
        self.campaigns = self.loader.load_campaigns()
        print(f"Loaded campaigns: {[c.name for c in self.campaigns]}")

        if hasattr(self, "recent_campaigns_widget") and self.recent_campaigns_widget is not None:
            self.recent_campaigns_widget.update_campaigns(self.campaigns)

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
        self._create_campaigns_section()

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
        self.new_campaign_btn = PrimaryButton(self.NEW_CAMPAIGN_BUTTON_TEXT)
        self.new_campaign_btn.setObjectName("NewCampaignButton")
        self.new_campaign_btn.clicked.connect(self.new_campaign_requested.emit)

        # Browse All button
        self.browse_all_btn = SecondaryButton(self.BROWSE_CAMPAIGNS_BUTTON_TEXT)
        self.browse_all_btn.setObjectName("BrowseAllButton")
        self.browse_all_btn.clicked.connect(self.browse_campaigns_requested.emit)

        button_layout.addWidget(self.new_campaign_btn)
        button_layout.addWidget(self.browse_all_btn)
        button_layout.addStretch()  # Push buttons to left

        self.main_layout.addLayout(button_layout)

    def _create_campaigns_section(self):
        """Create campaigns section with dynamic content."""
        # Section title
        section_header = SectionHeader(self.RECENT_CAMPAIGNS_HEADER_TEXT)
        self.main_layout.addWidget(section_header)
        self.main_layout.addSpacing(15)

        # Create container for dynamic content
        self.recent_campaigns_widget = RecentCampaignsWidget()
        self.main_layout.addWidget(self.recent_campaigns_widget)

    def _update_campaigns_display(self):
        """Update the campaigns display based on loaded campaigns."""
        if hasattr(self, "recent_campaigns_widget"):
            self.recent_campaigns_widget.update_campaigns(self.campaigns)

    def _apply_styles(self):
        """Apply screen-specific styles."""
        self.setStyleSheet(
            get_widget_styles()
            + """
            /* "+ New Campaign" Button */
            #NewCampaignButton {
                background-color: #007BFF; /* A vibrant blue */
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
            }
            #NewCampaignButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
            }

            /* "Browse All" Button */
            #BrowseAllButton {
                background-color: white;
                color: #333333; /* Dark gray text */
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border: 1px solid #CCCCCC; /* Light gray border */
                border-radius: 8px;
            }
            #BrowseAllButton:hover {
                background-color: #f0f0f0; /* Light gray on hover */
            }
        """
        )
