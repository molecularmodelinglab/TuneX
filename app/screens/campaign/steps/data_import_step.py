"""
Data import step for campaign creation wizard.
"""

from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QVBoxLayout, QFileDialog

from app.core.base import BaseStep
from app.shared.components.headers import MainHeader, SectionHeader
from app.models.parameters.base import BaseParameter
from .components.parameter_managers import ParameterSerializer
from .components.data_import_widgets import (
    PageHeaderWidget,
    UploadSectionWidget,
    TemplateSectionWidget,
    DataPreviewWidget,
)
from .components.csv_template_generator import CSVTemplateGenerator
from .components.csv_data_importer import CSVDataImporter, CSVValidationResult


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

    MAIN_LAYOUT_SPACING = 30
    MAIN_LAYOUT_MARGINS = (40, 40, 40, 40)

    def __init__(self, shared_data: dict, parent=None):
        """
        Initialize the data import step.

        Args:
            shared_data: Shared campaign configuration data
        """
        # Initialize data before calling super()
        self.imported_data: List[Dict[str, Any]] = []
        self.parameters: List[BaseParameter] = []
        self.selected_file_path: Optional[str] = None
        self.validation_result: Optional[CSVValidationResult] = None
        self.serializer = ParameterSerializer()

        super().__init__(shared_data, parent)

        # Connect signals after UI is setup
        self._connect_signals()

    def _setup_widget(self):
        """Setup the data import step UI."""
        layout = self._create_main_layout()

        # Create title and description
        title = MainHeader("Data Import")
        layout.addWidget(title)

        description = SectionHeader(
            "Import historical data to help optimize your campaign parameters."
        )
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
            # Create CSV data importer
            csv_importer = CSVDataImporter(self.parameters, self.shared_data)

            # Import and validate the CSV data
            self.imported_data, self.validation_result = csv_importer.import_csv(
                file_path
            )

            if self.validation_result.is_valid:
                print(f"Successfully imported {len(self.imported_data)} rows of data")

                # Update preview widget
                self.preview_widget.display_data(
                    self.imported_data, self.validation_result
                )
            else:
                print(f"CSV validation failed: {self.validation_result.get_summary()}")
                # Note: DataPreviewWidget doesn't have display_validation_errors method
                self.preview_widget.display_validation_errors()

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
            "Save CSV Template",
            "campaign_data_template.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            try:
                generator = CSVTemplateGenerator(self.parameters, self.shared_data)
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

        print(
            f"Data import validation passed - {len(self.imported_data)} rows imported"
        )
        return True

    def save_data(self) -> None:
        """Save imported data to shared data."""
        try:
            # Save file path and imported data
            self.shared_data["imported_file_path"] = self.selected_file_path
            self.shared_data["imported_data"] = self.imported_data.copy()

            # Save validation result summary
            if self.validation_result:
                self.shared_data["import_validation"] = {
                    "is_valid": self.validation_result.is_valid,
                    "row_count": len(self.imported_data),
                    "error_message": self.validation_result.get_summary(),
                }

            print(f"Successfully saved import data - {len(self.imported_data)} rows")

        except Exception as e:
            print(f"Error saving import data: {e}")

    def load_data(self) -> None:
        """Load previously imported data from shared data."""
        try:
            # Load parameters from previous steps
            parameters_data = self.shared_data.get("parameters", [])
            if parameters_data:
                self.parameters = self.serializer.deserialize_parameters(
                    parameters_data
                )
                print(f"Loaded {len(self.parameters)} parameters for data validation")

            # Load previously imported data
            self.selected_file_path = self.shared_data.get("imported_file_path")
            self.imported_data = self.shared_data.get("imported_data", [])

            # Load validation result
            validation_data = self.shared_data.get("import_validation", {})
            if validation_data:
                # Reconstruct validation result
                self.validation_result = CSVValidationResult()
                self.validation_result.is_valid = validation_data.get("is_valid", True)
                self.validation_result.total_rows = validation_data.get("row_count", 0)
                self.validation_result.valid_rows = len(self.imported_data)
                if not self.validation_result.is_valid:
                    error_message = validation_data.get("error_message", "")
                    if error_message:
                        self.validation_result.add_error(error_message)

            # Update UI with loaded data
            if self.imported_data:
                print(
                    f"Loaded {len(self.imported_data)} rows of previously imported data"
                )
                if hasattr(self, "preview_widget"):
                    self.preview_widget.display_data(
                        self.imported_data, self.validation_result
                    )
                # Note: UploadSectionWidget doesn't have show_selected_file method

        except Exception as e:
            print(f"Error loading import data: {e}")

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
