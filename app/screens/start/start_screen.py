"""
Start screen for TuneX application.
Main entry point showing welcome UI and navigation to other screens.
"""

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseScreen
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.cards import EmptyStateCard
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
    NO_RECENT_CAMPAIGNS_TEXT = "No recent campaigns"
    NO_RECENT_CAMPAIGNS_SUBTEXT = "Browse or create a new one"
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
        self._create_recent_campaigns_section()

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

    def _create_recent_campaigns_section(self):
        """Create recent campaigns section."""
        # Section title
        section_header = SectionHeader(self.RECENT_CAMPAIGNS_HEADER_TEXT)
        self.main_layout.addWidget(section_header)
        self.main_layout.addSpacing(15)

        # Empty state card
        icon_pixmap = self._get_folder_icon_pixmap()
        empty_state = EmptyStateCard(
            primary_message=self.NO_RECENT_CAMPAIGNS_TEXT,
            secondary_message=self.NO_RECENT_CAMPAIGNS_SUBTEXT,
            icon_pixmap=icon_pixmap,
        )

        self.main_layout.addWidget(empty_state)

    def _get_folder_icon_pixmap(self) -> QPixmap:
        """Get folder icon as pixmap."""
        style = self.style()
        icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        return icon.pixmap(64, 64)

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
