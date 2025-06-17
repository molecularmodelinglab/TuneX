"""
Campaign creation wizard screen.
Multi-step process for creating new campaigns.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)
from PySide6.QtCore import Signal as pyqtSignal

from app.core.base import BaseScreen
from app.shared.components.buttons import NavigationButton
from app.shared.styles.theme import get_widget_styles, get_navigation_styles, get_form_styles
from app.screens.campaign.steps.campaign_info_step import CampaignInfoStep
from app.screens.campaign.steps.parameters_step import ParametersStep  
from app.screens.campaign.steps.data_import_step import DataImportStep


class CampaignWizard(BaseScreen):
    """
    Campaign creation wizard with multiple steps.
    
    Manages navigation between campaign setup steps and
    collects all necessary data for campaign creation.
    """
    
    # Navigation signals
    back_to_start_requested = pyqtSignal()
    campaign_created = pyqtSignal(dict)  # Emits campaign data when created
    
    def __init__(self, parent=None):
        # Initialize data before calling super() since BaseScreen calls _setup_screen()
        self.current_step = 0
        self.total_steps = 3
        
        # Shared campaign data
        self.campaign_data = {
            "name": "",
            "description": "",
            "target": {"name": "", "mode": "Max"},
            "parameters": [],
        }
        
        super().__init__(parent)
        self.setWindowTitle("TuneX - Create Campaign")
    
    def _setup_screen(self):
        """Setup the campaign wizard UI."""
        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
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
            CampaignInfoStep(self.campaign_data),
            ParametersStep(self.campaign_data),
            DataImportStep(self.campaign_data)
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
        nav_layout.setContentsMargins(30, 20, 30, 20)
        nav_layout.setSpacing(15)
        
        # Back button
        self.back_button = NavigationButton("← Back", "back")
        self.back_button.clicked.connect(self._go_back)
        
        # Add stretch to push buttons apart
        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()
        
        # Next button
        self.next_button = NavigationButton("Next →", "next")
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
            self.next_button.setText("Create Campaign")
        else:
            self.next_button.setText("Next →")
        
        # Load data into current step
        current_widget = self.stacked_widget.currentWidget()
        current_widget.load_data()
    
    def _create_campaign(self):
        """Create campaign with collected data."""
        print("Creating campaign with data:")
        print(f"Campaign Data: {self.campaign_data}")
        
        # Emit campaign created signal
        self.campaign_created.emit(self.campaign_data.copy())
        
        # Go back to start screen
        self.back_to_start_requested.emit()
    
    def reset_wizard(self):
        """Reset wizard to initial state."""
        self.current_step = 0
        
        # Reset campaign data
        self.campaign_data = {
            "name": "",
            "description": "",
            "target": {"name": "", "mode": "Max"},
            "parameters": [],
        }
        
        # Reset all step widgets
        for step_widget in self.step_widgets:
            step_widget.reset()
        
        self._update_step_display()
    
    def _apply_styles(self):
        """Apply wizard-specific styles."""
        styles = get_widget_styles() + get_navigation_styles()
        self.setStyleSheet(styles)

