"""
Specialized widgets for the data import step.

This module contains all UI components for the data import functionality:
- PageHeaderWidget: Page title and description
- FileValidator: File validation logic
- DragDropArea: Drag & drop functionality
- UploadSectionWidget: File upload coordination
- TemplateSectionWidget: Template generation buttons
- DataPreviewWidget: Display imported data with validation status

Each widget is self-contained and communicates via Qt signals.
Focus on functionality first - styling will be added later.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from .csv_data_importer import CSVValidationResult


class PageHeaderWidget(QWidget):
    """Widget for displaying page title and description."""

    # Text Constants
    TITLE_TEXT = "Import Previous Experiments"
    DESCRIPTION_TEXT = "Add existing experimental data from CSV files. This step is optional - you can skip it and create campaigns without historical data."

    # Layout Constants
    NO_MARGINS = (0, 0, 0, 0)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create and arrange header components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self.NO_MARGINS)

        self.title_label = QLabel(self.TITLE_TEXT)
        self.description_label = QLabel(self.DESCRIPTION_TEXT)

        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)


class FileValidator:
    """Handles file validation logic for CSV uploads."""

    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, str]:
        """
        Validate that the selected file is accessible and appears to be a CSV.

        Args:
            file_path: Path to the file to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return False, f"File does not exist: {file_path}"

            if not path.is_file():
                return False, f"Path is not a file: {file_path}"

            if path.suffix.lower() != ".csv":
                return False, f"File is not a CSV: {file_path}"

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.readline()
            except (PermissionError, UnicodeDecodeError) as e:
                return False, f"Cannot read file: {e}"

            return True, ""

        except Exception as e:
            return False, f"Error validating file: {e}"


class DragDropArea(QFrame):
    """Frame widget that handles drag & drop functionality for CSV files."""

    # Signals
    file_dropped = Signal(str)  # Emitted when valid file is dropped

    MIN_HEIGHT = 120
    LAYOUT_SPACING = 10
    NO_MARGINS = (0, 0, 0, 0)

    DROP_AREA_TEXT = "Drop CSV file here or"
    BROWSE_BUTTON_TEXT = "Browse CSV file"

    def __init__(self) -> None:
        super().__init__()
        self.file_validator = FileValidator()
        self._setup_ui()
        self._setup_drag_drop()

    def _setup_ui(self) -> None:
        """Create and arrange the drop area UI."""
        self.setMinimumHeight(self.MIN_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(self.LAYOUT_SPACING)
        layout.setContentsMargins(*self.NO_MARGINS)

        self.drop_text = QLabel(self.DROP_AREA_TEXT)
        self.drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.drop_text)

        self.browse_button = QPushButton(self.BROWSE_BUTTON_TEXT)
        layout.addWidget(self.browse_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_drag_drop(self) -> None:
        """Enable drag & drop functionality."""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if self._is_valid_drag(event):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag move event."""
        if self._is_valid_drag(event):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if self._is_valid_drag(event):
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                is_valid, error_msg = self.file_validator.validate_file(file_path)

                if is_valid:
                    print(f"File dropped: {file_path}")
                    self.file_dropped.emit(file_path)
                    event.accept()
                    return
                else:
                    print(error_msg)

        print("Invalid file dropped")
        event.ignore()

    def _is_valid_drag(self, event) -> bool:
        """Check if the drag event contains valid files."""
        if not event.mimeData().hasUrls():
            return False

        urls = event.mimeData().urls()
        if not urls:
            return False

        # Check if first file is a CSV
        file_path = urls[0].toLocalFile()
        return file_path.lower().endswith(".csv")


class UploadSectionWidget(QWidget):
    """Main widget for file upload functionality with drag&drop and browse button."""

    file_selected = Signal(str)  # Emitted when user selects a file

    SECTION_TITLE = "Upload experimental data"
    DIALOG_TITLE = "Select CSV File"
    FILE_FILTER = "CSV files (*.csv);;All files (*.*)"

    NO_MARGINS = (0, 0, 0, 0)

    def __init__(self) -> None:
        super().__init__()
        self.file_validator = FileValidator()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Create and arrange upload components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self.NO_MARGINS)

        # Section title
        self.section_title = QLabel(self.SECTION_TITLE)
        layout.addWidget(self.section_title)

        # Drag & drop area
        self.drop_area = DragDropArea()
        layout.addWidget(self.drop_area)

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.drop_area.browse_button.clicked.connect(self._on_browse_clicked)
        self.drop_area.file_dropped.connect(self._on_file_dropped)

    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.DIALOG_TITLE, "", self.FILE_FILTER
        )

        if file_path:
            is_valid, error_msg = self.file_validator.validate_file(file_path)

            if is_valid:
                print(f"Valid CSV file selected: {file_path}")
                self.file_selected.emit(file_path)
            else:
                print(f"Invalid file selected: {error_msg}")
        else:
            print("File selection cancelled by user")

    def _on_file_dropped(self, file_path: str) -> None:
        """Handle file dropped from drag & drop area."""
        self.file_selected.emit(file_path)


class TemplateSectionWidget(QWidget):
    """Widget for template generation functionality."""

    template_requested = Signal(str)  # Emitted with format type (csv, xlsx)

    SECTION_TITLE = "Generate a template"
    DOWNLOAD_CSV_BUTTON_TEXT = "Download CSV"

    NO_MARGINS = (0, 0, 0, 0)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Create and arrange template components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self.NO_MARGINS)

        self.section_title = QLabel(self.SECTION_TITLE)
        layout.addWidget(self.section_title)

        self.download_csv_button = QPushButton(self.DOWNLOAD_CSV_BUTTON_TEXT)
        layout.addWidget(self.download_csv_button)

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.download_csv_button.clicked.connect(self._on_download_csv_clicked)

    def _on_download_csv_clicked(self) -> None:
        """Handle CSV template download."""
        self.template_requested.emit("csv")


class DataPreviewWidget(QWidget):
    """
    Widget for displaying imported CSV data with validation status.

    Shows successfully imported data in a table with proper headers
    and provides visual feedback about the import process.
    """

    SECTION_TITLE = "Data Preview"
    NO_DATA_TEXT = "No data imported yet"
    EMPTY_DATA_TEXT = "No valid data to display"

    # Layout constants
    NO_MARGINS = (0, 0, 0, 0)
    TABLE_MIN_HEIGHT = 200

    def __init__(self) -> None:
        super().__init__()
        self.imported_data: List[Dict[str, Any]] = []
        self.validation_result: Optional["CSVValidationResult"] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create and arrange preview components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self.NO_MARGINS)

        # Section title
        self.section_title = QLabel(self.SECTION_TITLE)
        layout.addWidget(self.section_title)

        # Preview table
        self.table = self._create_preview_table()
        layout.addWidget(self.table)

        # Initially show no data message
        self._show_no_data_message()

    def _create_preview_table(self) -> QTableWidget:
        """Create and configure the data preview table."""
        table = QTableWidget()
        table.setMinimumHeight(self.TABLE_MIN_HEIGHT)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)

        # Configure headers
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        table.verticalHeader().setVisible(True)  # Show row numbers

        return table

    def display_data(
        self,
        imported_data: List[Dict[str, Any]],
        validation_result: "CSVValidationResult",
    ) -> None:
        """
        Display imported data with validation status.

        Args:
            imported_data: Successfully imported and validated data
            validation_result: Validation results with error information
        """
        self.imported_data = imported_data
        self.validation_result = validation_result

        if not imported_data:
            self._show_empty_data_message()
            return

        self._populate_table()
        print(f"Displaying {len(imported_data)} rows in preview table")

    def _populate_table(self) -> None:
        """Populate the table with imported data."""
        if not self.imported_data:
            return

        # Get column headers from first row
        headers = list(self.imported_data[0].keys())

        self.table.setRowCount(len(self.imported_data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Populate table data
        for row_index, row_data in enumerate(self.imported_data):
            for col_index, header in enumerate(headers):
                value = row_data.get(header, "")
                item = QTableWidgetItem(str(value))

                # Make cells read-only
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.table.setItem(row_index, col_index, item)

        # Auto-resize columns to content
        self.table.resizeColumnsToContents()

    def _show_no_data_message(self) -> None:
        """Show message when no data has been imported."""
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Status"])

        item = QTableWidgetItem(self.NO_DATA_TEXT)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 0, item)

    def _show_empty_data_message(self) -> None:
        """Show message when no valid data to display."""
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Status"])

        item = QTableWidgetItem(self.EMPTY_DATA_TEXT)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 0, item)

    def clear_data(self) -> None:
        """Clear the preview table and reset to initial state."""
        self.imported_data = []
        self.validation_result = None
        self._show_no_data_message()

    def get_display_summary(self) -> str:
        """
        Get a summary of the displayed data for status reporting.

        Returns:
            String summary of what's currently displayed
        """
        if not self.imported_data:
            return "No data displayed"

        if not self.validation_result:
            return f"Displaying {len(self.imported_data)} rows"

        total_rows = self.validation_result.total_rows
        valid_rows = len(self.imported_data)
        error_rows = total_rows - valid_rows

        if error_rows > 0:
            return f"Displaying {valid_rows} valid rows ({error_rows} rows with errors hidden)"
        else:
            return f"Displaying all {valid_rows} rows (no errors)"
