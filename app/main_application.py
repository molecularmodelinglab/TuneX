"""
Main application window for TuneX.
Manages navigation between different screens.
"""

from typing import Optional

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.models.campaign import Campaign
from app.screens.campaign.campaign_wizard import CampaignWizard
from app.screens.campaign.panel.campaign_panel import CampaignPanelScreen
from app.screens.start.start_screen import StartScreen
from app.screens.workspace.select_workspace import SelectWorkspaceScreen
from app.shared.constants import ScreenName


class MainApplication(QMainWindow):
    """
    Main application window that manages navigation between screens.

    Uses a QStackedWidget to handle different screens:
    - Start screen (welcome/home)
    - Campaign wizard (multi-step campaign creation)
    - Additional screens can be easily added
    """

    DEFAULT_WINDOW_TITLE = "TuneX"
    WELCOME_WINDOW_TITLE = "TuneX - Welcome"
    CREATE_CAMPAIGN_WINDOW_TITLE = "TuneX - Create Campaign"
    GEOMETRY = (100, 100, 1200, 800)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.DEFAULT_WINDOW_TITLE)
        self.setGeometry(*self.GEOMETRY)

        # Setup main navigation
        self._setup_navigation()

        # Connect screen navigation
        self._connect_navigation()

        # Start with welcome screen
        self.show_select_workspace()

    def _setup_navigation(self):
        """Setup the main navigation structure."""
        # Create stacked widget for screen management
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.start_screen = StartScreen()
        self.campaign_wizard = CampaignWizard()
        self.select_workspace = SelectWorkspaceScreen()
        self.campaign_panel = None  # Placeholder for the campaign panel

        # Add screens to stack
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.campaign_wizard)
        self.stacked_widget.addWidget(self.select_workspace)

    def _connect_navigation(self):
        """Connect navigation signals between screens."""
        # From workspace selection to the start screen
        self.select_workspace.workspace_selected.connect(self._on_workspace_selected)

        # Start screen navigation
        self.start_screen.new_campaign_requested.connect(self.show_campaign_wizard)
        self.start_screen.browse_campaigns_requested.connect(self.show_browse_campaigns)
        self.start_screen.back_requested.connect(self.show_select_workspace)
        self.start_screen.campaign_selected.connect(self.show_campaign_panel)

        # Campaign wizard navigation
        self.campaign_wizard.back_to_start_requested.connect(self.show_start_screen)
        self.campaign_wizard.campaign_created.connect(self.on_campaign_created)

    def show_start_screen(self):
        """Navigate to the start screen."""
        self.start_screen.set_workspace(self.current_workspace)
        self.stacked_widget.setCurrentWidget(self.start_screen)
        self.setWindowTitle(self.WELCOME_WINDOW_TITLE)

    def show_select_workspace(self):
        """Navigate to the start screen."""
        self.stacked_widget.setCurrentWidget(self.select_workspace)
        self.setWindowTitle(self.WELCOME_WINDOW_TITLE)

    def show_campaign_wizard(self):
        """Navigate to campaign creation wizard."""
        # Reset wizard state when starting new campaign
        self.campaign_wizard.reset_wizard()
        self.campaign_wizard.workspace_path = self.current_workspace
        self.stacked_widget.setCurrentWidget(self.campaign_wizard)
        self.setWindowTitle(self.CREATE_CAMPAIGN_WINDOW_TITLE)

    def show_campaign_panel(self, campaign: Campaign):
        """Navigate to the campaign panel screen."""
        if self.campaign_panel:
            self.stacked_widget.removeWidget(self.campaign_panel)
            self.campaign_panel.deleteLater()

        self.campaign_panel = CampaignPanelScreen(campaign)
        self.campaign_panel.home_requested.connect(self.show_start_screen)
        self.stacked_widget.addWidget(self.campaign_panel)
        self.stacked_widget.setCurrentWidget(self.campaign_panel)
        self.setWindowTitle(f"TuneX - {campaign.name}")

    def show_browse_campaigns(self):
        """Navigate to browse campaigns screen."""
        # TODO: Implement browse campaigns screen
        print("Browse campaigns functionality coming soon!")

    def on_campaign_created(self, campaign: Campaign):
        """Handle campaign creation completion."""
        print(f"Campaign created successfully: {campaign.name}")

        # TODO: Save campaign to database/file
        # TODO: Show success message
        # TODO: Navigate to campaign details or start screen

        # For now, just return to start screen
        self.show_start_screen()

    def _on_workspace_selected(self, workspace_path):
        """Handle workspace selection."""
        self.current_workspace = workspace_path
        self.show_start_screen()

    def navigate_to(self, screen_name: ScreenName, data: Optional[dict] = None):
        """
        Generic navigation method for screen-to-screen communication.

        Args:
            screen_name: Name of the target screen
            data: Optional data to pass to the target screen
        """
        if screen_name == ScreenName.START:
            self.show_start_screen()
        elif screen_name == ScreenName.CAMPAIGN_WIZARD:
            self.show_campaign_wizard()
        elif screen_name == ScreenName.BROWSE_CAMPAIGNS:
            self.show_browse_campaigns()
        elif screen_name == ScreenName.SELECT_WORKSPACE:
            self.show_select_workspace()
        else:
            print(f"Unknown screen: {screen_name}")

    def closeEvent(self, event):
        """Handle application close event."""
        # TODO: Add any cleanup logic here
        # TODO: Ask user to save unsaved changes
        event.accept()
