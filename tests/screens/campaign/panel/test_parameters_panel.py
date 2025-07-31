"""
Tests for the ParametersPanel functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock

from app.screens.campaign.panel.parameters_panel import ParametersPanel
from app.models.enums import ParameterType


@pytest.fixture
def mock_campaign():
    """Create a mock campaign with parameters."""
    campaign = Mock()
    
    param1 = Mock()
    param1.name = "temperature"
    param1.parameter_type = ParameterType.DISCRETE_NUMERICAL_REGULAR
    param1.min_val = 20
    param1.max_val = 100
    param1.step = 5
    
    param2 = Mock()
    param2.name = "catalyst"
    param2.parameter_type = ParameterType.CATEGORICAL
    param2.values = ["A", "B", "C"]
    
    campaign.parameters = [param1, param2]
    return campaign

@pytest.fixture
def parameters_panel(qtbot):
    """Create a ParametersPanel for testing."""
    panel = ParametersPanel()
    qtbot.addWidget(panel)
    return panel

@pytest.fixture
def parameters_panel_with_campaign(qtbot, mock_campaign):
    """Create a ParametersPanel with campaign data for testing."""
    panel = ParametersPanel(campaign=mock_campaign)
    qtbot.addWidget(panel)
    return panel

def test_parameters_panel_creation(parameters_panel):
    """Test that the parameters panel is created correctly."""
    assert parameters_panel is not None
    assert hasattr(parameters_panel, 'parameters_table')
    assert hasattr(parameters_panel, 'info_label')


def test_parameters_panel_signal_exists(parameters_panel):
    """Test that the parameters panel has the required signal."""
    assert hasattr(parameters_panel, "data_exported")


def test_parameters_signal_emission(qtbot, parameters_panel):
    """Test that the parameters signal can be emitted."""
    with qtbot.waitSignal(parameters_panel.data_exported, timeout=1000):
        parameters_panel.data_exported.emit()


def test_get_panel_buttons_returns_export_button(parameters_panel):
    """Test that get_panel_buttons returns the Export Data button."""
    buttons = parameters_panel.get_panel_buttons()

    assert len(buttons) == 1
    assert buttons[0].text() == "Export Data"

def test_no_parameters_state(parameters_panel):
    """Test the panel shows correct state when no parameters are defined."""
    assert parameters_panel.info_label.text() == "No parameters defined for this campaign."
    assert parameters_panel.parameters_table.rowCount() == 0

def test_parameters_table_creation(parameters_panel):
    """Test that the parameters table is created with correct structure."""
    table = parameters_panel.parameters_table
    
    assert table.columnCount() == 3
    assert table.horizontalHeaderItem(0).text() == "Parameter"
    assert table.horizontalHeaderItem(1).text() == "Type"
    assert table.horizontalHeaderItem(2).text() == "Values"

def test_load_parameters_data(parameters_panel_with_campaign):
    """Test loading parameters data into the table."""
    panel = parameters_panel_with_campaign
    
    assert panel.parameters_table.rowCount() == 2
    assert "Parameters (2)" in panel.info_label.text()
    
    assert panel.parameters_table.item(0, 0).text() == "temperature"
    assert panel.parameters_table.item(0, 1).text() == "Discrete Numerical Regular"
    
    assert panel.parameters_table.item(1, 0).text() == "catalyst"
    assert panel.parameters_table.item(1, 1).text() == "Categorical"

def test_format_parameter_type(parameters_panel):
    """Test parameter type formatting."""
    panel = parameters_panel
    
    param = Mock()
    param.parameter_type = ParameterType.DISCRETE_NUMERICAL_REGULAR
    result = panel._format_parameter_type(param)
    assert result == "Discrete Numerical Regular"
    
    param.parameter_type = ParameterType.CATEGORICAL
    result = panel._format_parameter_type(param)
    assert result == "Categorical"
    
    param.parameter_type = None
    result = panel._format_parameter_type(param)
    assert result == "Unknown"

def test_format_parameter_values_discrete_regular(parameters_panel):
    """Test parameter values formatting for discrete numerical regular."""
    panel = parameters_panel
    
    param = Mock()
    param.parameter_type = Mock()
    param.parameter_type.value = "discrete_numerical_regular"
    param.min_val = 10
    param.max_val = 50
    param.step = 2
    
    result = panel._format_parameter_values(param)
    assert "start: 10" in result
    assert "stop: 50" in result
    assert "step: 2" in result

def test_format_parameter_values_categorical(parameters_panel):
    """Test parameter values formatting for categorical."""
    panel = parameters_panel
    
    param = Mock()
    param.parameter_type = Mock()
    param.parameter_type.value = "categorical"
    param.values = ["option1", "option2", "option3"]
    
    result = panel._format_parameter_values(param)
    assert result == "option1, option2, option3"

def test_update_campaign_data(parameters_panel, mock_campaign):
    """Test updating campaign data."""
    panel = parameters_panel
    
    assert panel.parameters_table.rowCount() == 0

    panel.update_campaign_data(mock_campaign)
    
    assert panel.parameters_table.rowCount() == 2
    assert "Parameters (2)" in panel.info_label.text()

def test_set_campaign(parameters_panel, mock_campaign):
    """Test setting campaign."""
    panel = parameters_panel
    
    panel.set_campaign(mock_campaign)
    
    assert panel.campaign == mock_campaign
    assert panel.parameters_table.rowCount() == 2

def test_set_workspace_path(parameters_panel):
    """Test setting workspace path."""
    panel = parameters_panel
    workspace_path = "/test/path"
    
    panel.set_workspace_path(workspace_path)
    
    assert panel.workspace_path == workspace_path
    assert panel.campaign_loader is not None