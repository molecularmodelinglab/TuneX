from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog

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


class DataImportStep(QWidget):
    """
    Step 3: Import experimental data from CSV files.

    This step coordinates multiple specialized widgets:
    - PageHeaderWidget: Title and description
    - UploadSectionWidget: File upload functionality
    - TemplateSectionWidget: Template generation

    The step follows the same pattern as other wizard steps:
    - validate(): Check if data is properly imported and valid
    - save_data(): Save imported data to campaign_data
    - load_data(): Load previously imported data (if any)
    """

    MAIN_LAYOUT_SPACING = 30
    MAIN_LAYOUT_MARGINS = (40, 40, 40, 40)

    def __init__(self, campaign_data: Dict[str, Any]) -> None:
        """
        Initialize the data import step.

        Args:
            campaign_data: Shared campaign configuration data
        """
        super().__init__()
        self.campaign_data = campaign_data
        self.imported_data: List[Dict[str, Any]] = []
        self.parameters: List[BaseParameter] = []
        self.selected_file_path: Optional[str] = None
        self.validation_result: Optional[CSVValidationResult] = None

        self.serializer = ParameterSerializer()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Create and arrange the main UI components."""
        layout = self._create_main_layout()

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
        self.upload_widget.file_selected.connect(self._on_file_selected)
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

        print(f"Importing CSV data from: {file_path}")
        print(f"Validating against {len(self.parameters)} configured parameters")

        importer = CSVDataImporter(self.parameters)
        self.imported_data, self.validation_result = importer.import_csv(file_path)

        self._display_import_results()

    def _display_import_results(self) -> None:
        """Display the results of CSV import and validation."""
        if not self.validation_result:
            return

        result = self.validation_result

        print("\n" + "=" * 50)
        print("CSV IMPORT RESULTS")
        print("=" * 50)

        print(f"{result.get_summary()}")
        print(f"Total rows processed: {result.total_rows}")
        print(f"Valid rows: {result.valid_rows}")

        if result.missing_columns:
            print(f"\n Missing columns: {', '.join(result.missing_columns)}")

        if result.extra_columns:
            print(f"\n Extra columns: {', '.join(result.extra_columns)}")

        if result.errors:
            print("\n General errors:")
            for error in result.errors:
                print(f"   • {error}")

        if result.row_errors:
            print("\n Row errors:")
            for row_num in sorted(result.row_errors.keys())[:5]:
                errors = result.row_errors[row_num]
                print(f"   Row {row_num}: {', '.join(errors)}")

            if len(result.row_errors) > 5:
                print(f"   ... and {len(result.row_errors) - 5} more rows with errors")

        if result.warnings:
            print("\n  Warnings:")
            for warning in result.warnings:
                print(f"   • {warning}")

        if result.is_valid:
            print(
                f"\n Successfully imported {len(self.imported_data)} rows of experimental data!"
            )

            self.preview_widget.display_data(self.imported_data, self.validation_result)
            preview_summary = self.preview_widget.get_display_summary()
            print(f" {preview_summary}")
        else:
            print("\n Please fix the errors above and try importing again.")
            self.preview_widget.clear_data()

        print("=" * 50 + "\n")

    def _on_template_requested(self, format_type: str) -> None:
        """Handle template generation request."""
        if format_type == "csv":
            self._generate_csv_template()
        else:
            print(f"Unsupported template format: {format_type}")

    def _generate_csv_template(self) -> None:
        """Generate and save CSV template based on configured parameters."""
        if not self.parameters:
            print("No parameters available for template generation")
            print("Please configure parameters in Step 2 before generating a template")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV Template", "experiment_template.csv", "CSV files (*.csv)"
        )

        if not file_path:
            print("Template generation cancelled by user")
            return

        generator = CSVTemplateGenerator(self.parameters)
        success = generator.generate_template(file_path)

        if success:
            template_info = generator.get_template_info()
            print("Template generation completed!")
            print(f"Columns: {', '.join(template_info['column_names'])}")
            print(f"Parameters included: {template_info['num_parameters']}")
            print(f"Example rows: {template_info['num_example_rows']}")
        else:
            print("Failed to generate template")

    def validate(self) -> bool:
        """
        Validate that experimental data has been imported and is valid.

        Returns:
            bool: True if validation passed, False otherwise
        """
        if not self.selected_file_path:
            print("No data file selected - skipping data import (optional step)")
            return True

        if not self.validation_result:
            print("File was selected but not processed - please try importing again")
            return False

        if not self.validation_result.is_valid:
            print("Data import failed validation - please fix errors and try again")
            return False

        print(f"Data import validation passed - {len(self.imported_data)} rows ready")
        return True

    def save_data(self) -> None:
        """
        Save imported experimental data to campaign configuration.
        """
        if (
            self.imported_data
            and self.validation_result
            and self.validation_result.is_valid
        ):
            self.campaign_data["experimental_data"] = self.imported_data
            print(
                f"Saved {len(self.imported_data)} rows of experimental data to campaign"
            )
        else:
            self.campaign_data["experimental_data"] = []
            print("No experimental data to save (optional step skipped)")

        if self.selected_file_path:
            self.campaign_data["data_file_path"] = self.selected_file_path

    def load_data(self) -> None:
        """
        Load previously imported experimental data (if any).
        """
        self._load_parameters_from_campaign_data()

    def _load_parameters_from_campaign_data(self) -> None:
        """
        Load parameters from campaign data for use in template generation.

        This method deserializes the parameters configured in the previous step
        so we can generate appropriate CSV templates.
        """
        try:
            parameters_data = self.campaign_data.get("parameters", [])
            if parameters_data:
                self.parameters = self.serializer.deserialize_parameters(
                    parameters_data
                )
                print(
                    f"Loaded {len(self.parameters)} parameters for template generation"
                )

                for param in self.parameters:
                    print(f"  Parameter: {param.name} ({param.parameter_type.value})")
            else:
                print("No parameters found in campaign data")
                self.parameters = []

        except Exception as e:
            print(f"Error loading parameters: {e}")
            self.parameters = []
