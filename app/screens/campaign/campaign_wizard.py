from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
)

from app.widgets.campaign.create.steps.campaign_info_step import CampaignInfoStep
from app.widgets.campaign.create.steps.parameters_step import ParametersStep
from app.widgets.campaign.create.steps.data_import_step import DataImportStep


class CreateCampaignWindow(QMainWindow):
    """
    Main coordinator for campaign creation wizard.
    
    Manages navigation between 3 steps: campaign info, parameters, and data import.
    Handles shared data between steps and validation flow.
    
    Attributes:
        current_step (int): Current wizard step index (0-2)
        campaign_data (dict): Shared configuration data between all steps
            - name (str): Campaign name
            - description (str): Campaign description  
            - target (dict): Target configuration with name and mode
            - parameters (list): List of experiment parameters
        
        stacked_widget (QStackedWidget): Container for switching between step widgets
        step1_widget (CampaignInfoStep): Basic campaign information step
        step2_widget (ParametersStep): Experiment parameters configuration step
        step3_widget (DataImportStep): Historical data import step
        
        back_button (QPushButton): Navigation button to previous step
        next_button (QPushButton): Navigation button to next step or finish
    """

    def __init__(self):
        super().__init__()
        self.current_step = 0

        # Shared data between all steps
        self.campaign_data = {
            "name": "",
            "description": "",
            "target": {"name": "", "mode": "Max"},
            "parameters": [],  # Will be filled by ParametersStep
        }

        self.uploaded_file = None

        self.setup_ui()

    def setup_ui(self):
        """Creates main UI structure"""
        self.setWindowTitle("TuneX - Create New Campaign")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Create content area with steps
        self.create_content_area(main_layout)

        # Create navigation buttons
        self.create_navigation(main_layout)

        # Show first step
        self.update_step_display()

    def create_content_area(self, parent_layout):
        """Creates main content area with step widgets"""
        self.stacked_widget = QStackedWidget()

        # Create step widgets - each gets access to shared data
        self.step1_widget = CampaignInfoStep(self.campaign_data)
        self.step2_widget = ParametersStep(self.campaign_data)
        self.step3_widget = DataImportStep(self.campaign_data)

        # Add to stack
        self.stacked_widget.addWidget(self.step1_widget)
        self.stacked_widget.addWidget(self.step2_widget)
        self.stacked_widget.addWidget(self.step3_widget)

        parent_layout.addWidget(self.stacked_widget)

    def create_navigation(self, parent_layout):
        """Creates navigation buttons"""
        nav_layout = QHBoxLayout()

        # Back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_next)

        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.next_button)

        parent_layout.addLayout(nav_layout)

    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()

    def go_next(self):
        """Go to next step or finish"""
        # Get current step widget for validation
        current_widget = self.stacked_widget.currentWidget()

        # Validate current step before proceeding
        if not current_widget.validate():
            return  # Stay on current step if validation fails

        # Save current step data
        current_widget.save_data()

        if self.current_step < 2:
            self.current_step += 1
            self.update_step_display()
        else:
            # Last step - create campaign
            self.create_campaign()

    def update_step_display(self):
        """Updates current step display"""
        # Switch to current step
        self.stacked_widget.setCurrentIndex(self.current_step)

        # Update navigation buttons
        self.back_button.setEnabled(self.current_step > 0)

        if self.current_step == 2:
            self.next_button.setText("Create Campaign")
        else:
            self.next_button.setText("Next")

        # Load data into current step
        current_widget = self.stacked_widget.currentWidget()
        current_widget.load_data()

    def create_campaign(self):
        """Create campaign with collected data"""
        print("Creating campaign with data:")
        print(f"Campaign Data: {self.campaign_data}")

        # TODO: Implement database save and campaign initialization"
        self.close()