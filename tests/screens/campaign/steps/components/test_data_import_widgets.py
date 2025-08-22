"""
Tests for the data import widgets functionality.
"""

import os
import shutil
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QMimeData, Qt, QUrl

from app.screens.campaign.setup.components.data_import_widgets import (
    DataPreviewWidget,
    DragDropArea,
    FileValidator,
    PageHeaderWidget,
    TemplateSectionWidget,
    UploadSectionWidget,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    test_dir = "test_temp_data"
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_csv_file(temp_dir):
    """Create a sample CSV file for testing."""
    csv_path = os.path.join(temp_dir, "sample.csv")
    with open(csv_path, "w") as f:
        f.write("param1,param2,target\n")
        f.write("1.0,2.0,85.5\n")
    return csv_path


@pytest.fixture
def invalid_file(temp_dir):
    """Create an invalid file for testing."""
    file_path = os.path.join(temp_dir, "invalid.txt")
    with open(file_path, "w") as f:
        f.write("This is not a CSV file")
    return file_path


def test_page_header_widget_creation(qtbot):
    """Test that the PageHeaderWidget is created correctly."""
    widget = PageHeaderWidget()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "title_label")
    assert hasattr(widget, "description_label")
    assert widget.title_label.text() == PageHeaderWidget.TITLE_TEXT
    assert widget.description_label.text() == PageHeaderWidget.DESCRIPTION_TEXT


def test_file_validator_valid_file(sample_csv_file):
    """Test FileValidator with a valid CSV file."""
    is_valid, error_msg = FileValidator.validate_file(sample_csv_file)

    assert is_valid is True
    assert error_msg == ""


def test_file_validator_nonexistent_file():
    """Test FileValidator with a non-existent file."""
    is_valid, error_msg = FileValidator.validate_file("/non/existent/file.csv")

    assert is_valid is False
    assert FileValidator.FILE_NOT_EXIST_MESSAGE.format("/non/existent/file.csv") in error_msg


def test_file_validator_non_file_path(temp_dir):
    """Test FileValidator with a path that is not a file."""
    is_valid, error_msg = FileValidator.validate_file(temp_dir)

    assert is_valid is False
    assert FileValidator.NOT_A_FILE_MESSAGE.format(temp_dir) in error_msg


def test_file_validator_non_csv_file(invalid_file):
    """Test FileValidator with a non-CSV file."""
    is_valid, error_msg = FileValidator.validate_file(invalid_file)

    assert is_valid is False
    assert FileValidator.NOT_CSV_MESSAGE.format(invalid_file) in error_msg


def test_file_validator_unreadable_file(temp_dir):
    """Test FileValidator with an unreadable file."""
    # Create a file and then remove read permissions
    file_path = os.path.join(temp_dir, "unreadable.csv")
    with open(file_path, "w") as f:
        f.write("test")

    # On Windows, we can't easily test permission errors, so we'll mock it
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        is_valid, error_msg = FileValidator.validate_file(file_path)

        assert is_valid is False
        assert "Cannot read file" in error_msg


def test_drag_drop_area_creation(qtbot):
    """Test that the DragDropArea is created correctly."""
    widget = DragDropArea()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "drop_text")
    assert hasattr(widget, "browse_button")
    assert widget.drop_text.text() == DragDropArea.DROP_AREA_TEXT
    assert widget.browse_button.text() == DragDropArea.BROWSE_BUTTON_TEXT


def test_drag_drop_area_drag_enter_event(qtbot):
    """Test drag enter event handling."""
    widget = DragDropArea()
    qtbot.addWidget(widget)

    # Create a mock drag event with a CSV file
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("test.csv")])

    # Mock the event
    event = MagicMock()
    event.mimeData.return_value = mime_data
    with patch.object(event, "accept") as mock_accept:
        widget.dragEnterEvent(event)
        mock_accept.assert_called_once()


def test_drag_drop_area_drag_enter_event_invalid(qtbot):
    """Test drag enter event handling with invalid file."""
    widget = DragDropArea()
    qtbot.addWidget(widget)

    # Create a mock drag event with a non-CSV file
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("test.txt")])

    # Mock the event
    event = MagicMock()
    event.mimeData.return_value = mime_data
    with patch.object(event, "ignore") as mock_ignore:
        widget.dragEnterEvent(event)
        mock_ignore.assert_called_once()


def test_upload_section_widget_creation(qtbot):
    """Test that the UploadSectionWidget is created correctly."""
    widget = UploadSectionWidget()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "section_title")
    assert hasattr(widget, "drop_area")
    assert widget.section_title.text() == UploadSectionWidget.SECTION_TITLE


def test_template_section_widget_creation(qtbot):
    """Test that the TemplateSectionWidget is created correctly."""
    widget = TemplateSectionWidget()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "section_title")
    assert hasattr(widget, "download_csv_button")
    assert widget.section_title.text() == TemplateSectionWidget.SECTION_TITLE
    assert widget.download_csv_button.text() == TemplateSectionWidget.DOWNLOAD_CSV_BUTTON_TEXT


def test_template_section_widget_button_click(qtbot):
    """Test that clicking the download button emits the signal."""
    widget = TemplateSectionWidget()
    qtbot.addWidget(widget)

    # Connect to the signal
    with qtbot.waitSignal(widget.template_requested) as blocker:
        qtbot.mouseClick(widget.download_csv_button, Qt.LeftButton)

    assert blocker.signal_triggered
    assert blocker.args == ["csv"]


def test_data_preview_widget_creation(qtbot):
    """Test that the DataPreviewWidget is created correctly."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "section_title")
    assert hasattr(widget, "status_label")
    assert hasattr(widget, "table")
    assert widget.section_title.text() == DataPreviewWidget.SECTION_TITLE


def test_data_preview_widget_clear_data(qtbot):
    """Test that clear_data method works correctly."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    # Set some data
    widget.all_data = [{"test": "data"}]
    widget.valid_data = [{"test": "data"}]

    # Clear data
    widget.clear_data()

    # Check that data is cleared
    assert widget.all_data == []
    assert widget.valid_data == []
    assert widget.validation_result is None


def test_data_preview_widget_display_data(qtbot):
    """Test displaying data in the preview widget."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    # Sample data
    all_data = [{"param1": 1.0, "param2": 2.0, "target": 85.5}, {"param1": 1.5, "param2": 2.5, "target": 92.1}]
    valid_data = all_data

    # Mock validation result
    validation_result = MagicMock()
    validation_result.errors = []
    validation_result.missing_columns = []
    validation_result.warnings = []
    validation_result.cell_errors = {}
    validation_result.is_valid = True
    validation_result.total_rows = 2
    validation_result.valid_rows = 2

    # Display data
    widget.display_data(all_data, valid_data, validation_result)

    # Check that data is stored
    assert widget.all_data == all_data
    assert widget.valid_data == valid_data
    assert widget.validation_result == validation_result


def test_data_preview_widget_get_display_summary_empty(qtbot):
    """Test get_display_summary method with no data."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    summary = widget.get_display_summary()
    assert summary == DataPreviewWidget.NO_DATA_DISPLAYED


def test_data_preview_widget_get_display_summary_with_data(qtbot):
    """Test get_display_summary method with valid data."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    # Set up data
    widget.all_data = [{"param1": 1.0}, {"param1": 2.0}]
    widget.valid_data = widget.all_data

    summary = widget.get_display_summary()
    assert summary == widget.DISPLAYING_ALL_ROWS_MESSAGE.format(2)


def test_data_preview_widget_get_display_summary_with_invalid_data(qtbot):
    """Test get_display_summary method with invalid data."""
    widget = DataPreviewWidget()
    qtbot.addWidget(widget)

    # Set up data with some invalid rows
    widget.all_data = [{"param1": 1.0}, {"param1": 2.0}, {"param1": 3.0}]
    widget.valid_data = [{"param1": 1.0}, {"param1": 2.0}]  # One invalid row

    summary = widget.get_display_summary()
    assert summary == widget.DISPLAYING_ROWS_WITH_ERRORS_MESSAGE.format(3, 2, 1)


if __name__ == "__main__":
    pytest.main([__file__])
