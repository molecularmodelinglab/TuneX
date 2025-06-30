"""
Data import step for campaign creation wizard.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import QFileDialog, QVBoxLayout

from app.core.base import BaseStep
from app.models.campaign import Campaign
from app.models.parameters import ParameterSerializer
from app.models.parameters.base import BaseParameter
from app.shared.components.headers import MainHeader, SectionHeader

from .components.csv_data_importer import CSVDataImporter, CSVValidationResult
from .components.csv_template_generator import CSVTemplateGenerator
from .components.data_import_widgets import (
    DataPreviewWidget,
    PageHeaderWidget,
    TemplateSectionWidget,
    UploadSectionWidget,
)


class DataImportStep(BaseStep):
    """
    Third step of campaign creation wizard.

    This step coordinates multiple specialized widgets:
    - PageHeaderWidget: Title and description
    - UploadSectionWidget: File upload functionality
    - TemplateSectionWidget: Template generation
    - DataPreviewWidget: Data preview and validation

    The step follows the same pattern as other wizard steps:
    - validate(): Check if data is properly imported and valid
    - save_data(): Save imported data to shared_data
    - load_data(): Load previously imported data (if any)
    """

    TITLE = "Data Import"
    DESCRIPTION = "Import historical data to help optimize your campaign parameters."
    SAVE_TEMPLATE_DIALOG_TITLE = "Save CSV Template"
    DEFAULT_TEMPLATE_FILENAME = "campaign_data_template.csv"
    CSV_FILE_FILTER = "CSV Files (*.csv);;All Files (*)"

    MAIN_LAYOUT_SPACING = 30
    MAIN_LAYOUT_MARGINS = (40, 40, 40, 40)

    def __init__(self, wizard_data: Campaign, parent=None):
        """
        Initialize the data import step.

        Args:
            wizard_data: The campaign data model
        """
        # Initialize data before calling super()
        self.imported_data: List[Dict[str, Any]] = []
        self.parameters: List[BaseParameter] = []
        self.selected_file_path: Optional[str] = None
        self.validation_result: Optional[CSVValidationResult] = None
        self.serializer = ParameterSerializer()

        super().__init__(wizard_data, parent)
        self.campaign: Campaign = self.wizard_data

        # Connect signals after UI is setup
        self._connect_signals()

    def _setup_widget(self):
        """Setup the data import step UI."""
        layout = self._create_main_layout()

        # Create title and description
        title = MainHeader(self.TITLE)
        layout.addWidget(title)

        description = SectionHeader(self.DESCRIPTION)
        layout.addWidget(description)

        # Create specialized widgets
        self.header_widget = PageHeaderWidget()
        self.upload_widget = UploadSectionWidget()
        self.template_widget = TemplateSectionWidget()
        self.preview_widget = DataPreviewWidget()

        layout.addWidget(self.header_widget)
        layout.addWidget(self.upload_widget)
        layout.addWidget(self.template_widget)
        layout.addWidget(self.preview_widget)
        layout.addStretch()

    def _create_main_layout(self) -> QVBoxLayout:
        """Create and configure the main layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(self.MAIN_LAYOUT_SPACING)
        layout.setContentsMargins(*self.MAIN_LAYOUT_MARGINS)
        return layout

    def _connect_signals(self) -> None:
        """Connect signals from child widgets."""
        if hasattr(self, "upload_widget"):
            self.upload_widget.file_selected.connect(self._on_file_selected)
        if hasattr(self, "template_widget"):
            self.template_widget.template_requested.connect(self._on_template_requested)

    def _on_file_selected(self, file_path: str) -> None:
        """Handle file selection from upload widget."""
        print(f"File selected: {file_path}")

        self.selected_file_path = file_path

        self._import_and_validate_csv(file_path)

    def _import_and_validate_csv(self, file_path: str) -> None:
        """
        Import CSV file and validate data against configured parameters.

        Args:
            file_path: Path to the CSV file to import
        """
        if not self.parameters:
            print("No parameters configured - cannot validate CSV data")
            print("Please configure parameters in Step 2 before importing data")
            return

        try:
            csv_importer = CSVDataImporter(self.parameters, self.campaign)
            self.imported_data, self.validation_result = csv_importer.import_csv(file_path)
            self._update_preview()

        except Exception as e:
            print(f"Error importing CSV file: {e}")
            # Note: DataPreviewWidget doesn't have display_error method

    def _on_template_requested(self) -> None:
        """Handle template download request."""
        if not self.parameters:
            print("No parameters configured - cannot generate template")
            return

        # Show file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.SAVE_TEMPLATE_DIALOG_TITLE,
            self.DEFAULT_TEMPLATE_FILENAME,
            self.CSV_FILE_FILTER,
        )

        if file_path:
            try:
                generator = CSVTemplateGenerator(self.parameters, self.campaign)
                generator.generate_template(file_path)
                print(f"Template saved to: {file_path}")

                # Template saved successfully (no UI update method available)

            except Exception as e:
                print(f"Error generating template: {e}")
                # Error occurred (no UI update method available)

    def validate(self) -> bool:
        """
        Validate that data import is complete and valid.

        Data import is optional, so this step always passes validation.
        However, if data is imported, it must be valid.

        Returns:
            bool: True if no data imported or data is valid, False if data is invalid
        """
        if not self.imported_data:
            print("No data imported - proceeding without historical data")
            return True

        if self.validation_result and not self.validation_result.is_valid:
            print(f"Imported data is invalid: {self.validation_result.get_summary()}")
            return False

        print(f"Data import validation passed - {len(self.imported_data)} rows imported")
        return True

    def save_data(self) -> None:
        """Save imported data to shared data."""
        try:
            # Save imported data
            self.campaign.initial_dataset = self.imported_data.copy()

            print(f"Successfully saved import data - {len(self.imported_data)} rows")
            print(self.campaign.to_dict())
        except Exception as e:
            print(f"Error saving import data: {e}")

    def load_data(self) -> None:
        """Load previously imported data from the campaign model."""
        try:
            self.parameters = self.campaign.parameters
            self.imported_data = self.campaign.initial_dataset

            if self.imported_data:
                self._validate_data()
                self._update_preview()
                print(f"Loaded and re-validated {len(self.imported_data)} rows of data")

        except Exception as e:
            print(f"Error loading import data: {e}")

    def _validate_data(self) -> None:
        """Re-validate the current self.imported_data."""
        if not self.parameters:
            print("No parameters configured - cannot validate CSV data")
            return

        csv_importer = CSVDataImporter(self.parameters, self.campaign)
        self.imported_data, self.validation_result = csv_importer.validate_data(self.imported_data)

    def _update_preview(self) -> None:
        """Update the preview widget with the current data and validation results."""
        if not hasattr(self, "preview_widget"):
            return

        if self.validation_result and self.validation_result.is_valid:
            print(f"Successfully imported {len(self.imported_data)} rows of data")
            self.preview_widget.display_data(self.imported_data, self.validation_result)
        elif self.validation_result:
            print(f"CSV validation failed: {self.validation_result.get_summary()}")
            self.preview_widget.display_validation_errors()

    def reset(self):
        """Reset import step to initial state."""
        self.selected_file_path = None
        self.imported_data = []
        self.validation_result = None

        # Reset UI widgets
        if hasattr(self, "preview_widget"):
            self.preview_widget.clear_data()
        # Note: UploadSectionWidget doesn't have a clear method,
        # so we'll just reset our internal state
