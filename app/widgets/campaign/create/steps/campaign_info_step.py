from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QComboBox,
)

from app.widgets.campaign.enums import TargetMode

WINDOW_TITLE = "Create New Campaign"


class CampaignInfoStep(QWidget):
    """
    First step of campaign creation wizard.

    Collects basic campaign information: name, description, and target configuration.
    Users must fill required fields (name and target name) before proceeding to next step.
    """

    LABELS = {
        "name": "Campaign name:",
        "description": "Description:",
        "target_name": "Name:",
        "target_mode": "Mode:",
        "target_section": "Target:",
    }
    DEFAULT_TARGET_MODE = TargetMode.MAX

    def __init__(self, campaign_data: Dict[str, Any]) -> None:
        super().__init__()
        self.campaign_data = campaign_data
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates the UI layout"""
        main_layout = QVBoxLayout(self)
        self._create_title(main_layout)
        self._create_form(main_layout)

    def _create_title(self, parent_layout: QVBoxLayout) -> None:
        """Creates title section"""
        title = QLabel(WINDOW_TITLE)
        parent_layout.addWidget(title)

    def _create_form(self, parent_layout: QVBoxLayout) -> None:
        """Creates form with all input fields"""
        form_layout = QFormLayout()
        parent_layout.addLayout(form_layout)

        self._create_basic_fields(form_layout)
        self._create_target_section(form_layout)

    def _create_basic_fields(self, form_layout: QFormLayout) -> None:
        """Creates campaign name and description input fields"""
        self.name_input = QLineEdit()
        form_layout.addRow(self.LABELS["name"], self.name_input)

        self.description_input = QTextEdit()
        form_layout.addRow(self.LABELS["description"], self.description_input)

    def _create_target_section(self, form_layout: QFormLayout) -> None:
        """Creates target name and mode selection section"""
        # Horizontal layout for side-by-side fields
        target_layout = QHBoxLayout()

        # Target name field
        self.target_name_input = QLineEdit()
        target_layout.addWidget(QLabel(self.LABELS["target_name"]))
        target_layout.addWidget(self.target_name_input)

        # Target mode dropdown
        self.target_mode_combo = QComboBox()
        self._populate_target_mode_combo()
        target_layout.addWidget(QLabel(self.LABELS["target_mode"]))
        target_layout.addWidget(self.target_mode_combo)

        # Add target section to main form
        form_layout.addRow(self.LABELS["target_section"], target_layout)

    def _populate_target_mode_combo(self) -> None:
        """Populates target mode dropdown with available enum values"""
        for mode in TargetMode:
            self.target_mode_combo.addItem(mode.value)

    def validate(self) -> bool:
        """
        Validates form data before proceeding to next step.

        Returns:
            bool: True if all required fields are filled, False otherwise
        """
        # Campaign name is required
        if not self.name_input.text().strip():
            # TODO: Show error message to user or disable "Next" button?
            print("Campaign name is required")
            return False

        # Target name is required
        if not self.target_name_input.text().strip():
            # TODO: Show error message to user or disable "Next" button?
            print("Target name is required")
            return False

        return True

    def save_data(self) -> None:
        """Saves form data to campaign_data for use in campaign creation"""
        self.campaign_data["name"] = self.name_input.text()
        self.campaign_data["description"] = self.description_input.toPlainText()

        # Save target configuration
        self.campaign_data["target"]["name"] = self.target_name_input.text()
        self.campaign_data["target"]["mode"] = self.target_mode_combo.currentText()

    def load_data(self) -> None:
        """Loads data from campaign_data into form fields when returning to this step"""
        self.name_input.setText(self.campaign_data.get("name", ""))
        self.description_input.setPlainText(self.campaign_data.get("description", ""))

        # Load target configuration
        target_data = self.campaign_data.get("target", {})
        target_name = target_data.get("name", "")
        self.target_name_input.setText(target_name)

        target_mode = target_data.get("mode", self.DEFAULT_TARGET_MODE.value)
        # Find and set the combo box index
        index = self.target_mode_combo.findText(target_mode)
        if index >= 0:
            self.target_mode_combo.setCurrentIndex(index)
