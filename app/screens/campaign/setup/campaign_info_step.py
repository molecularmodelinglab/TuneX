"""
Campaign information step for campaign creation wizard.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseStep
from app.models.campaign import Campaign, Target
from app.models.enums import TargetMode
from app.shared.components.buttons import DangerButton, PrimaryButton
from app.shared.components.headers import MainHeader, SectionHeader


class TargetRow(QWidget):
    """Individual target row widget."""

    def __init__(self, target: Target, on_remove_callback, parent=None):
        super().__init__(parent)
        self.target = target
        self.on_remove_callback = on_remove_callback
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Target name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter target name")
        self.name_input.setObjectName("FormInput")
        self.name_input.setText(self.target.name)
        layout.addWidget(self.name_input)

        # Target mode combo
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("FormInput")
        for mode in TargetMode:
            self.mode_combo.addItem(mode.value)

        # Set current mode
        index = self.mode_combo.findText(self.target.mode or TargetMode.MAX.value)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        layout.addWidget(self.mode_combo)

        # Remove button
        self.remove_btn = DangerButton("Remove")
        self.remove_btn.setToolTip("Remove this target")
        self.remove_btn.clicked.connect(lambda: self.on_remove_callback(self))
        layout.addWidget(self.remove_btn)

    def get_target_data(self) -> Target:
        """Get target data from this row."""
        self.target.name = self.name_input.text().strip()
        self.target.mode = self.mode_combo.currentText()
        return self.target

    def is_valid(self) -> bool:
        """Check if this target row has valid data."""
        return bool(self.name_input.text().strip())


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
    TARGETS_LABEL = "Targets/Objectives:"
    FORM_INPUT_OBJECT_NAME = "FormInput"
    FORM_LABEL_OBJECT_NAME = "FormLabel"
    ADD_TARGET_BUTTON_TEXT = "Add Another Target"

    MARGINS = (30, 30, 30, 30)
    MAIN_SPACING = 25
    FORM_SPACING = 15
    TARGET_SPACING = 10
    DESCRIPTION_HEIGHT = 100

    def __init__(self, wizard_data: Campaign, parent=None):
        super().__init__(wizard_data, parent)
        self.campaign: Campaign = self.wizard_data
        self.target_rows: list[TargetRow] = []

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
        self._create_targets_section(form_layout)

    def _create_targets_section(self, form_layout):
        """Create targets configuration section."""
        targets_widget = QWidget()
        targets_widget.setObjectName("TargetsWidget")
        targets_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        targets_layout = QVBoxLayout(targets_widget)
        targets_layout.setContentsMargins(0, 0, 0, 0)
        targets_layout.setSpacing(self.TARGET_SPACING)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        scroll_area.setMinimumHeight(200)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setObjectName("TargetsScrollArea")

        self.targets_container = QWidget()
        self.targets_layout = QVBoxLayout(self.targets_container)
        self.targets_container.setObjectName("TargetsContainer")
        self.targets_container.setStyleSheet("""
            QWidget#TargetsContainer {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 0px;
            }
        """)
        # self.targets_layout = QVBoxLayout(self.targets_container)
        self.targets_layout.setContentsMargins(10, 10, 10, 10)
        self.targets_layout.setSpacing(5)

        scroll_area.setWidget(self.targets_container)
        targets_layout.addWidget(scroll_area)

        self.add_target_btn = PrimaryButton(self.ADD_TARGET_BUTTON_TEXT)
        self.add_target_btn.setObjectName("PrimaryButton")
        self.add_target_btn.setFixedWidth(250)
        self.add_target_btn.setToolTip("Add a new target to the campaign")
        self.add_target_btn.clicked.connect(self._handle_add_target_click)
        targets_layout.addWidget(self.add_target_btn)

        targets_label = SectionHeader(self.TARGETS_LABEL)
        targets_label.setObjectName(self.FORM_LABEL_OBJECT_NAME)
        form_layout.addRow(targets_label, targets_widget)

    def _handle_add_target_click(self):
        """Slot for the 'Add Target' button. Calls _add_target_row with no target."""
        self._add_target_row()

    def _add_target_row(self, target: Target | None = None):
        """Add a new target row."""
        if target is None:
            target = Target()

        target_row = TargetRow(target, self._remove_target_row)
        self.target_rows.append(target_row)
        self.targets_layout.addWidget(target_row)

        # Update remove button visibility
        self._update_remove_buttons()

    def _remove_target_row(self, target_row: TargetRow):
        """Remove a target row."""
        if target_row in self.target_rows:
            self.target_rows.remove(target_row)
            self.targets_layout.removeWidget(target_row)
            target_row.deleteLater()
            self._update_remove_buttons()

    def _update_remove_buttons(self):
        """Update remove button visibility based on number of targets."""
        show_remove = len(self.target_rows) > 1
        for row in self.target_rows:
            row.remove_btn.setVisible(show_remove)

    def validate(self) -> bool:
        """Validate form data."""
        if not self.name_input.text().strip():
            print("Campaign name is required")  # TODO: Better error handling
            return False

        if not self.target_rows:
            print("At least one target is required")  # TODO: Better error handling
            return False

        valid_targets = [row for row in self.target_rows if row.is_valid()]
        if not valid_targets:
            print("At least one target must have a name")  # TODO: Better error handling
            return False

        return True

    def save_data(self):
        """Save form data to shared data."""
        self.campaign.name = self.name_input.text().strip()
        self.campaign.description = self.description_input.toPlainText().strip()

        self.campaign.targets = []
        for row in self.target_rows:
            if row.is_valid():
                self.campaign.targets.append(row.get_target_data())

    def load_data(self):
        """Load data from shared data into form."""
        self.name_input.setText(self.campaign.name)
        self.description_input.setPlainText(self.campaign.description)

        # Clear existing target rows
        for row in self.target_rows[:]:
            self._remove_target_row(row)

        # Load targets or add one empty target if none exist
        if self.campaign.targets:
            for target in self.campaign.targets:
                self._add_target_row(target)
        else:
            self._add_target_row()

    def reset(self):
        """Reset form to initial state."""
        self.name_input.clear()
        self.description_input.clear()

        for row in self.target_rows[:]:
            self._remove_target_row(row)
        self._add_target_row()
