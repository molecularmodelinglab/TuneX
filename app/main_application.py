"""
Main application window for TuneX.
Manages navigation between different screens.
"""

from typing import Optional

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.screens.start.start_screen import StartScreen
from app.screens.campaign.campaign_wizard import CampaignWizard


class MainApplication(QMainWindow):
    """
    Main application window that manages navigation between screens.

    Uses a QStackedWidget to handle different screens:
    - Start screen (welcome/home)
    - Campaign wizard (multi-step campaign creation)
    - Additional screens can be easily added
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneX")
        self.setGeometry(100, 100, 1200, 800)  # Increased window size

        # Setup main navigation
        self._setup_navigation()

        # Connect screen navigation
        self._connect_navigation()

        # Start with welcome screen
        self.show_start_screen()

    def _setup_navigation(self):
        """Setup the main navigation structure."""
        # Create stacked widget for screen management
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.start_screen = StartScreen()
        self.campaign_wizard = CampaignWizard()

        # Add screens to stack
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.campaign_wizard)

    def _connect_navigation(self):
        """Connect navigation signals between screens."""
        # Start screen navigation
        self.start_screen.new_campaign_requested.connect(self.show_campaign_wizard)
        self.start_screen.browse_campaigns_requested.connect(self.show_browse_campaigns)

        # Campaign wizard navigation
        self.campaign_wizard.back_to_start_requested.connect(self.show_start_screen)
        self.campaign_wizard.campaign_created.connect(self.on_campaign_created)

    def show_start_screen(self):
        """Navigate to the start screen."""
        self.stacked_widget.setCurrentWidget(self.start_screen)
        self.setWindowTitle("TuneX - Welcome")

    def show_campaign_wizard(self):
        """Navigate to campaign creation wizard."""
        # Reset wizard state when starting new campaign
        self.campaign_wizard.reset_wizard()
        self.stacked_widget.setCurrentWidget(self.campaign_wizard)
        self.setWindowTitle("TuneX - Create Campaign")

    def show_browse_campaigns(self):
        """Navigate to browse campaigns screen."""
        # TODO: Implement browse campaigns screen
        print("Browse campaigns functionality coming soon!")

    def on_campaign_created(self, campaign_data: dict):
        """Handle campaign creation completion."""
        print(f"Campaign created successfully: {campaign_data.get('name', 'Unnamed')}")

        # TODO: Save campaign to database/file
        # TODO: Show success message
        # TODO: Navigate to campaign details or start screen

        # For now, just return to start screen
        self.show_start_screen()

    def navigate_to(self, screen_name: str, data: Optional[dict] = None):
        """
        Generic navigation method for screen-to-screen communication.

        Args:
            screen_name: Name of the target screen
            data: Optional data to pass to the target screen
        """
        if screen_name == "start":
            self.show_start_screen()
        elif screen_name == "campaign_wizard":
            self.show_campaign_wizard()
        elif screen_name == "browse_campaigns":
            self.show_browse_campaigns()
        else:
            print(f"Unknown screen: {screen_name}")

    def closeEvent(self, event):
        """Handle application close event."""
        # TODO: Add any cleanup logic here
        # TODO: Ask user to save unsaved changes
        event.accept()
