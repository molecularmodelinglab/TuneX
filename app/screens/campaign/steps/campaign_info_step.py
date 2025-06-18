"""
Campaign information step for campaign creation wizard.
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QComboBox,
)

from app.core.base import BaseStep
from app.shared.components.headers import MainHeader
from app.models.enums import TargetMode
from app.shared.components.headers import SectionHeader


class CampaignInfoStep(BaseStep):
    """
    First step of campaign creation wizard.

    Collects basic campaign information: name, description, and target configuration.
    """

    def __init__(self, shared_data: dict, parent=None):
        super().__init__(shared_data, parent)

    def _setup_widget(self):
        """Setup the campaign info step UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Title
        title = MainHeader("Campaign Information")
        main_layout.addWidget(title)

        # Form
        self._create_form(main_layout)

        # Add stretch
        main_layout.addStretch()

    def _create_form(self, parent_layout):
        """Create form with all input fields."""
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        parent_layout.addLayout(form_layout)

        # Campaign name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter campaign name")
        self.name_input.setObjectName("FormInput")
        form_label = SectionHeader("Campaign Name:")
        form_label.setObjectName("FormLabel")
        form_layout.addRow(form_label, self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter campaign description")
        self.description_input.setFixedHeight(100)
        self.description_input.setObjectName("FormInput")
        desc_label = SectionHeader("Description:")
        desc_label.setObjectName("FormLabel")
        form_layout.addRow(desc_label, self.description_input)

        # Target section
        self._create_target_section(form_layout)

    def _create_target_section(self, form_layout):
        """Create target configuration section."""
        target_layout = QHBoxLayout()
        target_layout.setSpacing(15)

        # Target name
        self.target_name_input = QLineEdit()
        self.target_name_input.setPlaceholderText("Enter target name")
        self.target_name_input.setObjectName("FormInput")
        target_layout.addWidget(self.target_name_input)

        # Target mode
        self.target_mode_combo = QComboBox()
        self.target_mode_combo.setObjectName("FormInput")
        self._populate_target_mode_combo()
        target_layout.addWidget(self.target_mode_combo)

        target_label = SectionHeader("Target/Objective:")
        target_label.setObjectName("FormLabel")
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
        self.shared_data["name"] = self.name_input.text().strip()
        self.shared_data["description"] = self.description_input.toPlainText().strip()
        self.shared_data["target"]["name"] = self.target_name_input.text().strip()
        self.shared_data["target"]["mode"] = self.target_mode_combo.currentText()

    def load_data(self):
        """Load data from shared data into form."""
        self.name_input.setText(self.shared_data.get("name", ""))
        self.description_input.setPlainText(self.shared_data.get("description", ""))

        target_data = self.shared_data.get("target", {})
        self.target_name_input.setText(target_data.get("name", ""))

        target_mode = target_data.get("mode", TargetMode.MAX.value)
        index = self.target_mode_combo.findText(target_mode)
        if index >= 0:
            self.target_mode_combo.setCurrentIndex(index)

    def reset(self):
        """Reset form to initial state."""
        self.name_input.clear()
        self.description_input.clear()
        self.target_name_input.clear()
        self.target_mode_combo.setCurrentIndex(0)
