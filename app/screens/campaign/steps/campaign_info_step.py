"""
Campaign information step for campaign creation wizard.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from app.core.base import BaseStep
from app.models.campaign import Campaign
from app.models.enums import TargetMode
from app.shared.components.headers import MainHeader, SectionHeader


class CampaignInfoStep(BaseStep):
    """
    First step of campaign creation wizard.

    Collects basic campaign information: name, description, and target configuration.
    """

    TITLE = "Campaign Information"
    NAME_LABEL = "Campaign Name:"
    NAME_PLACEHOLDER = "Enter campaign name"
    DESCRIPTION_LABEL = "Description:"
    DESCRIPTION_PLACEHOLDER = "Enter campaign description"
    TARGET_LABEL = "Target/Objective:"
    TARGET_NAME_PLACEHOLDER = "Enter target name"
    FORM_INPUT_OBJECT_NAME = "FormInput"
    FORM_LABEL_OBJECT_NAME = "FormLabel"

    MARGINS = (30, 30, 30, 30)
    MAIN_SPACING = 25
    FORM_SPACING = 15
    TARGET_SPACING = 15
    DESCRIPTION_HEIGHT = 100

    def __init__(self, wizard_data: Campaign, parent=None):
        super().__init__(wizard_data, parent)
        self.campaign: Campaign = self.wizard_data

    def _setup_widget(self):
        """Setup the campaign info step UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*self.MARGINS)
        main_layout.setSpacing(self.MAIN_SPACING)

        # Title
        title = MainHeader(self.TITLE)
        main_layout.addWidget(title)

        # Form
        self._create_form(main_layout)

        # Add stretch
        main_layout.addStretch()

    def _create_form(self, parent_layout):
        """Create form with all input fields."""
        form_layout = QFormLayout()
        form_layout.setSpacing(self.FORM_SPACING)
        parent_layout.addLayout(form_layout)

        # Campaign name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.NAME_PLACEHOLDER)
        self.name_input.setObjectName(self.FORM_INPUT_OBJECT_NAME)
        form_label = SectionHeader(self.NAME_LABEL)
        form_label.setObjectName(self.FORM_LABEL_OBJECT_NAME)
        form_layout.addRow(form_label, self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(self.DESCRIPTION_PLACEHOLDER)
        self.description_input.setFixedHeight(self.DESCRIPTION_HEIGHT)
        self.description_input.setObjectName(self.FORM_INPUT_OBJECT_NAME)
        desc_label = SectionHeader(self.DESCRIPTION_LABEL)
        desc_label.setObjectName(self.FORM_LABEL_OBJECT_NAME)
        form_layout.addRow(desc_label, self.description_input)

        # Target section
        self._create_target_section(form_layout)

    def _create_target_section(self, form_layout):
        """Create target configuration section."""
        target_layout = QHBoxLayout()
        target_layout.setSpacing(self.TARGET_SPACING)

        # Target name
        self.target_name_input = QLineEdit()
        self.target_name_input.setPlaceholderText(self.TARGET_NAME_PLACEHOLDER)
        self.target_name_input.setObjectName(self.FORM_INPUT_OBJECT_NAME)
        target_layout.addWidget(self.target_name_input)

        # Target mode
        self.target_mode_combo = QComboBox()
        self.target_mode_combo.setObjectName(self.FORM_INPUT_OBJECT_NAME)
        self._populate_target_mode_combo()
        target_layout.addWidget(self.target_mode_combo)

        target_label = SectionHeader(self.TARGET_LABEL)
        target_label.setObjectName(self.FORM_LABEL_OBJECT_NAME)
        form_layout.addRow(target_label, target_layout)

    def _populate_target_mode_combo(self):
        """Populate target mode dropdown."""
        for mode in TargetMode:
            self.target_mode_combo.addItem(mode.value)

    def validate(self) -> bool:
        """Validate form data."""
        if not self.name_input.text().strip():
            print("Campaign name is required")  # TODO: Better error handling
            return False

        if not self.target_name_input.text().strip():
            print("Target name is required")  # TODO: Better error handling
            return False

        return True

    def save_data(self):
        """Save form data to shared data."""
        self.campaign.name = self.name_input.text().strip()
        self.campaign.description = self.description_input.toPlainText().strip()
        self.campaign.target.name = self.target_name_input.text().strip()
        self.campaign.target.mode = self.target_mode_combo.currentText()

    def load_data(self):
        """Load data from shared data into form."""
        self.name_input.setText(self.campaign.name)
        self.description_input.setPlainText(self.campaign.description)

        self.target_name_input.setText(self.campaign.target.name)

        target_mode = self.campaign.target.mode or TargetMode.MAX.value
        index = self.target_mode_combo.findText(target_mode)
        if index >= 0:
            self.target_mode_combo.setCurrentIndex(index)

    def reset(self):
        """Reset form to initial state."""
        self.name_input.clear()
        self.description_input.clear()
        self.target_name_input.clear()
        self.target_mode_combo.setCurrentIndex(0)
