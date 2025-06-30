"""
Campaign creation wizard screen.
Multi-step process for creating new campaigns.
"""

import json
import os
from datetime import datetime

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseScreen
from app.models.campaign import Campaign
from app.screens.campaign.steps.campaign_info_step import CampaignInfoStep
from app.screens.campaign.steps.data_import_step import DataImportStep
from app.screens.campaign.steps.parameters_step import ParametersStep
from app.shared.components.buttons import NavigationButton
from app.shared.styles.theme import get_navigation_styles, get_widget_styles


class CampaignWizard(BaseScreen):
    """
    Campaign creation wizard with multiple steps.

    Manages navigation between campaign setup steps and
    collects all necessary data for campaign creation.
    """

    # Navigation signals
    back_to_start_requested = pyqtSignal()
    campaign_created = pyqtSignal(Campaign)  # Emits campaign data when created

    WINDOW_TITLE = "TuneX - Create Campaign"
    BACK_BUTTON_TEXT = "← Back"
    NEXT_BUTTON_TEXT = "Next →"
    CREATE_CAMPAIGN_BUTTON_TEXT = "Create Campaign"
    MAIN_LAYOUT_MARGINS = (0, 0, 0, 0)
    MAIN_LAYOUT_SPACING = 0
    NAV_LAYOUT_MARGINS = (30, 20, 30, 20)
    NAV_LAYOUT_SPACING = 15

    def __init__(self, parent=None):
        # Initialize data before calling super() since BaseScreen calls _setup_screen()
        self.current_step = 0
        self.total_steps = 3
        self.workspace_path = None

        # Shared campaign data
        self.campaign = Campaign()

        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)

    def _setup_screen(self):
        """Setup the campaign wizard UI."""
        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(*self.MAIN_LAYOUT_MARGINS)
        main_layout.setSpacing(self.MAIN_LAYOUT_SPACING)

        # Create content area
        self._create_content_area(main_layout)

        # Create navigation
        self._create_navigation(main_layout)

        # Initialize display
        self._update_step_display()

    def _create_content_area(self, parent_layout):
        """Create main content area with step widgets."""
        self.stacked_widget = QStackedWidget()

        # Create step widgets
        self.step_widgets = [
            CampaignInfoStep(self.campaign),
            ParametersStep(self.campaign),
            DataImportStep(self.campaign),
        ]

        # Add to stacked widget
        for step_widget in self.step_widgets:
            self.stacked_widget.addWidget(step_widget)

        parent_layout.addWidget(self.stacked_widget)

    def _create_navigation(self, parent_layout):
        """Create navigation buttons."""
        # Navigation container
        nav_container = QWidget()
        nav_container.setObjectName("NavigationContainer")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(*self.NAV_LAYOUT_MARGINS)
        nav_layout.setSpacing(self.NAV_LAYOUT_SPACING)

        # Back button
        self.back_button = NavigationButton(self.BACK_BUTTON_TEXT, "back")
        self.back_button.clicked.connect(self._go_back)

        # Add stretch to push buttons apart
        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()

        # Next button
        self.next_button = NavigationButton(self.NEXT_BUTTON_TEXT, "next")
        self.next_button.clicked.connect(self._go_next)
        nav_layout.addWidget(self.next_button)

        parent_layout.addWidget(nav_container)

    def _go_back(self):
        """Navigate to previous step or start screen."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_display()
        else:
            # Go back to start screen
            self.back_to_start_requested.emit()

    def _go_next(self):
        """Navigate to next step or create campaign."""
        # Get current step widget
        current_widget = self.stacked_widget.currentWidget()

        # Validate current step
        if not current_widget.validate():
            return  # Stay on current step if validation fails

        # Save current step data
        current_widget.save_data()

        if self.current_step < self.total_steps - 1:
            # Go to next step
            self.current_step += 1
            self._update_step_display()
        else:
            # Create campaign
            self._create_campaign()

    def _update_step_display(self):
        """Update current step display and navigation."""
        # Switch to current step
        self.stacked_widget.setCurrentIndex(self.current_step)

        # Update navigation buttons
        self.back_button.setEnabled(True)  # Always enabled (can go to start)

        # Update next button text
        if self.current_step == self.total_steps - 1:
            self.next_button.setText(self.CREATE_CAMPAIGN_BUTTON_TEXT)
        else:
            self.next_button.setText(self.NEXT_BUTTON_TEXT)

        # Load data into current step
        current_widget = self.stacked_widget.currentWidget()
        current_widget.load_data()

    def _create_campaign(self):
        """Create campaign with collected data."""
        print("Creating campaign with data:")
        print(f"Campaign Data: {self.campaign}")

        # Save campaign to file
        self._save_campaign_to_file()

        # Emit campaign created signal
        self.campaign_created.emit(self.campaign)

        # Go back to start screen
        self.back_to_start_requested.emit()

    def _save_campaign_to_file(self):
        """Save the campaign data to a JSON file in the workspace."""
        if not self.workspace_path:
            print("Error: Workspace path not set. Cannot save campaign.")
            return

        try:
            campaign_data = self.campaign.to_dict()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.campaign.name}_{timestamp}.json"

            # Correctly join paths to create the full file path
            campaigns_dir = os.path.join(self.workspace_path, "campaigns")
            os.makedirs(campaigns_dir, exist_ok=True)
            file_path = os.path.join(campaigns_dir, filename)

            with open(file_path, "w") as f:
                json.dump(campaign_data, f, indent=4)
            print(f"Campaign saved to {file_path}")

        except Exception as e:
            print(f"Error saving campaign to file: {e}")

    def reset_wizard(self):
        """Reset wizard to initial state."""
        self.current_step = 0

        # Reset campaign data
        self.campaign.reset()

        # Reset all step widgets
        for step_widget in self.step_widgets:
            step_widget.reset()

        self._update_step_display()

    def _apply_styles(self):
        """Apply wizard-specific styles."""
        styles = get_widget_styles() + get_navigation_styles()
        self.setStyleSheet(styles)
