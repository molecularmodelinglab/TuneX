"""
Tests for the DataImportStep functionality.
"""

import os
import shutil
from unittest.mock import patch

import pytest

from app.models.campaign import Campaign, Target
from app.models.parameters.types import ContinuousNumerical, DiscreteNumericalRegular
from app.screens.campaign.setup.components.csv_data_importer import CSVValidationResult
from app.screens.campaign.setup.data_import_step import DataImportStep


@pytest.fixture
def sample_parameters():
    """Create sample parameters for testing."""
    return [
        DiscreteNumericalRegular("temperature", min_val=20.0, max_val=100.0, step=5.0),
        ContinuousNumerical("pressure", min_val=0.1, max_val=10.0),
    ]


@pytest.fixture
def sample_campaign(sample_parameters):
    """Create a sample campaign for testing."""
    campaign = Campaign()
    campaign.name = "Test Campaign"
    campaign.description = "A test campaign"
    campaign.targets = [Target(name="yield")]
    campaign.parameters = sample_parameters
    return campaign


@pytest.fixture
def data_import_step(qtbot, sample_campaign):
    """Create a DataImportStep for testing."""
    step = DataImportStep(sample_campaign)
    qtbot.addWidget(step)
    return step


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
        f.write("temperature,pressure,yield\n")
        f.write("25.0,2.5,85.5\n")
        f.write("30.0,3.0,92.1\n")
    return csv_path


def test_data_import_step_creation(data_import_step, sample_campaign):
    """Test that the data import step is created correctly."""
    assert data_import_step is not None
    assert data_import_step.campaign == sample_campaign
    assert hasattr(data_import_step, "all_imported_data")
    assert hasattr(data_import_step, "valid_imported_data")
    assert hasattr(data_import_step, "parameters")
    # Parameters are loaded in load_data, not in constructor
    assert data_import_step.parameters == []


def test_data_import_step_reset(data_import_step):
    """Test that the reset method clears all data."""
    # Set some sample data
    data_import_step.all_imported_data = [{"test": "data"}]
    data_import_step.valid_imported_data = [{"test": "data"}]
    data_import_step.selected_file_path = "/test/path"
    data_import_step.validation_result = CSVValidationResult()

    # Call reset
    data_import_step.reset()

    # Check that data is cleared
    assert data_import_step.all_imported_data == []
    assert data_import_step.valid_imported_data == []
    assert data_import_step.selected_file_path is None
    assert data_import_step.validation_result is None


def test_data_import_step_validate_without_data(data_import_step):
    """Test validation when no data is imported."""
    # Should pass validation when no data is imported (optional step)
    assert data_import_step.validate() is True


def test_data_import_step_validate_with_valid_data(data_import_step):
    """Test validation with valid imported data."""
    # Set up valid data
    data_import_step.all_imported_data = [{"temperature": 25.0, "pressure": 2.5, "yield": 85.5}]
    data_import_step.valid_imported_data = [{"temperature": 25.0, "pressure": 2.5, "yield": 85.5}]
    data_import_step.validation_result = CSVValidationResult()
    data_import_step.validation_result.is_valid = True
    data_import_step.validation_result.total_rows = 1
    data_import_step.validation_result.valid_rows = 1

    # Should pass validation with valid data
    assert data_import_step.validate() is True


def test_data_import_step_validate_with_no_valid_data(data_import_step):
    """Test validation when no valid data exists."""
    # Set up invalid data
    data_import_step.all_imported_data = [{"temperature": "invalid", "pressure": 2.5, "yield": 85.5}]
    data_import_step.valid_imported_data = []
    data_import_step.validation_result = CSVValidationResult()
    data_import_step.validation_result.is_valid = False
    data_import_step.validation_result.total_rows = 1
    data_import_step.validation_result.valid_rows = 0

    # Should fail validation with no valid data
    with patch("app.shared.components.dialogs.ErrorDialog.show_error") as mock_error:
        result = data_import_step.validate()
        assert result is False
        mock_error.assert_called_once()


def test_data_import_step_save_data(data_import_step):
    """Test saving data to campaign."""
    # Set up valid data
    valid_data = [{"temperature": 25.0, "pressure": 2.5, "yield": 85.5}]
    data_import_step.valid_imported_data = valid_data

    # Save data
    data_import_step.save_data()

    # Check that data was saved to campaign
    assert data_import_step.campaign.initial_dataset == valid_data


def test_data_import_step_load_data(data_import_step, sample_parameters):
    """Test loading data from campaign."""
    # Set up campaign with data
    sample_data = [{"temperature": 25.0, "pressure": 2.5, "yield": 85.5}]
    data_import_step.campaign.parameters = sample_parameters
    data_import_step.campaign.initial_dataset = sample_data

    # Load data
    data_import_step.load_data()

    # Check that data was loaded
    assert data_import_step.parameters == sample_parameters
    assert data_import_step.valid_imported_data == sample_data
    assert data_import_step.all_imported_data == sample_data


def test_data_import_step_load_data_without_parameters(data_import_step):
    """Test loading data when no parameters are configured."""
    # Clear parameters
    data_import_step.campaign.parameters = []
    data_import_step.campaign.initial_dataset = []

    # Load data
    data_import_step.load_data()

    # Check that parameters are loaded correctly
    assert data_import_step.parameters == []


@patch("app.shared.components.dialogs.ErrorDialog.show_error")
def test_data_import_step_validate_without_parameters(mock_error, data_import_step):
    """Test validation when no parameters are configured."""
    # Clear parameters
    data_import_step.parameters = []
    data_import_step.all_imported_data = []

    # Should pass validation (optional step)
    result = data_import_step.validate()
    assert result is True
    mock_error.assert_not_called()


def test_data_import_step_validate_data_method(data_import_step):
    """Test the _validate_data method."""
    # Set up parameters and valid data
    data_import_step.parameters = [DiscreteNumericalRegular("temperature", min_val=20.0, max_val=100.0, step=5.0)]
    data_import_step.valid_imported_data = [{"temperature": 25.0}]

    # Call validate_data method (this should not raise an exception)
    data_import_step._validate_data()

    # The method should complete without error
    assert True


def test_data_import_step_validate_data_without_parameters(data_import_step):
    """Test the _validate_data method when no parameters are configured."""
    # Clear parameters
    data_import_step.parameters = []
    data_import_step.valid_imported_data = []

    # Call validate_data method (this should not raise an exception)
    with patch("builtins.print") as mock_print:
        data_import_step._validate_data()
        mock_print.assert_called_with("No parameters configured - cannot validate CSV data")


if __name__ == "__main__":
    pytest.main([__file__])
