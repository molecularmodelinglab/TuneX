"""
Tests for the ParametersPanel functionality.
"""

import pytest
from PySide6.QtCore import Qt

from app.screens.campaign.panel.parameters_panel import ParametersPanel


@pytest.fixture
def parameters_panel(qtbot):
    """Create a ParametersPanel for testing."""
    panel = ParametersPanel()
    qtbot.addWidget(panel)
    return panel


def test_parameters_panel_creation(parameters_panel):
    """Test that the parameters panel is created correctly."""
    assert parameters_panel is not None


def test_parameters_panel_signal_exists(parameters_panel):
    """Test that the parameters panel has the required signal."""
    assert hasattr(parameters_panel, "parameters_edited")


def test_parameters_signal_emission(qtbot, parameters_panel):
    """Test that the parameters signal can be emitted."""
    with qtbot.waitSignal(parameters_panel.parameters_edited, timeout=1000):
        parameters_panel.parameters_edited.emit()


def test_get_panel_buttons_returns_edit_button(parameters_panel):
    """Test that get_panel_buttons returns the Edit Parameters button."""
    buttons = parameters_panel.get_panel_buttons()

    assert len(buttons) == 1
    assert buttons[0].text() == "Edit Parameters"


def test_edit_button_emits_signal(qtbot, parameters_panel):
    """Test that clicking the edit button emits the signal."""
    buttons = parameters_panel.get_panel_buttons()
    edit_button = buttons[0]

    with qtbot.waitSignal(parameters_panel.parameters_edited, timeout=1000):
        qtbot.mouseClick(edit_button, Qt.LeftButton)
