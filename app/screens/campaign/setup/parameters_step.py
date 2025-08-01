"""
Parameters configuration step for campaign creation wizard.
"""

from typing import List, Optional

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout

from app.core.base import BaseStep
from app.models.campaign import Campaign
from app.models.parameters.base import BaseParameter
from app.shared.components.headers import MainHeader, SectionHeader

from .components.parameter_managers import ParameterRowManager


class ParametersStep(BaseStep):
    """
    Second step of campaign creation wizard.

    This step coordinates the parameter configuration UI by delegating
    specific responsibilities to specialized managers:

    - ParameterRowManager: Handles table rows and UI widgets
    - ParameterSerializer: Handles save/load operations
    - Constraint widgets: Handle individual parameter editing and validation

    The class itself focuses on the overall workflow and user interactions.
    """

    # UI constants
    ADD_BUTTON_TEXT = "+ Add Parameter"

    def __init__(self, wizard_data: Campaign, parent=None):
        """
        Initialize the parameters configuration step.

        Args:
            wizard_data: The campaign data model
        """
        # Initialize parameters list before calling super()
        self.parameters: List[Optional[BaseParameter]] = []

        super().__init__(wizard_data, parent)
        self.campaign: Campaign = self.wizard_data

        # Connect UI signals
        self._connect_signals()

    def _setup_widget(self):
        """Setup the parameters step UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Title
        title = MainHeader("Parameter Configuration")
        main_layout.addWidget(title)

        # Description
        description = SectionHeader("Configure the parameters you want to optimize in your campaign.")
        main_layout.addWidget(description)

        # Setup managers
        self._setup_managers()

        # Parameters table
        self._table = self.row_manager.get_table_widget()
        main_layout.addWidget(self._table)

        # Control buttons
        buttons_layout = self._create_buttons_layout()
        main_layout.addLayout(buttons_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

    def _create_buttons_layout(self) -> QHBoxLayout:
        """Create the layout containing control buttons."""
        layout = QHBoxLayout()

        self._add_button = QPushButton(self.ADD_BUTTON_TEXT)
        self._add_button.setObjectName("PrimaryButton")
        self._add_button.setToolTip("Add a new parameter to the campaign")
        layout.addWidget(self._add_button)

        layout.addStretch()

        return layout

    def _setup_managers(self) -> None:
        """Initialize the specialized managers for different responsibilities."""
        # Manager for table rows and UI widgets (creates and owns the table)
        self.row_manager = ParameterRowManager(self.parameters)

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        if hasattr(self, "_add_button"):
            self._add_button.clicked.connect(self._on_add_parameter)

    def _on_add_parameter(self) -> None:
        """
        Handle the 'Add Parameter' button click.

        Delegates the actual row creation to the row manager.
        """
        self.row_manager.add_new_parameter_row()

    def validate(self) -> bool:
        """
        Validate all configured parameters.

        This method delegates validation to the row manager, which in turn
        asks each constraint widget to validate itself. Each widget handles
        both UI-to-parameter synchronization and parameter validation.

        Returns:
            bool: True if all parameters are valid, False otherwise

        Note:
            Validation errors are handled by the row manager and displayed
            to the user appropriately.
        """
        is_valid, error_message = self.row_manager.validate_all_widgets()

        if not is_valid:
            # TODO: Implement user-friendly error display (dialog/status bar instead of print)
            print(f"Parameter validation failed: {error_message}")
        else:
            print(f"Successfully validated {len(self.parameters)} parameters")

        return is_valid

    def save_data(self) -> None:
        """
        Save the current parameter configuration to shared data.

        This method ensures UI data is synchronized to parameter objects,
        then serializes the parameters for storage in the campaign data.
        """
        try:
            # Ensure all UI data is synced to parameter objects
            self.row_manager.sync_ui_to_parameters()

            # Filter out any None values before saving
            valid_parameters = [p for p in self.parameters if p is not None]
            self.campaign.parameters = valid_parameters

            print(f"Successfully saved {len(self.parameters)} parameters to campaign data")

            # Debug output - in production this might be logged instead
            for i, param in enumerate(self.campaign.parameters, 1):
                print(f"  Parameter {i}: {param.name} ({param.parameter_type.value})")

        except Exception as e:
            print(f"Error saving parameters: {e}")
            # In a real application, you would handle this error more gracefully

    def load_data(self) -> None:
        """
        Load parameter configuration from shared data.

        This method is called when returning to this step or loading an
        existing campaign. It deserializes the parameter data and populates
        the UI table.
        """
        try:
            # Get parameters data from campaign
            loaded_parameters = self.campaign.parameters

            if not loaded_parameters:
                print("No saved parameters found - starting with empty table")
                return

            print(f"Loading {len(loaded_parameters)} parameters from campaign data")

            # Update our parameters list
            self.parameters.clear()
            self.parameters.extend(loaded_parameters)

            # Populate the UI table with loaded parameters
            self.row_manager.load_parameters_to_table(loaded_parameters)

            print(f"Successfully loaded {len(loaded_parameters)} parameters")

            # Debug output
            for param in loaded_parameters:
                print(f"  Loaded: {param}")

        except Exception as e:
            print(f"Error loading parameters: {e}")

    def reset(self):
        """Reset parameters to initial state."""
        self.parameters.clear()
        if hasattr(self, "row_manager"):
            self.row_manager.clear_table()
