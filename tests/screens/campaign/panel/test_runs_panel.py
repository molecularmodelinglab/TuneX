"""
Tests for the RunsPanel functionality.
"""

import pytest
from PySide6.QtCore import Qt

from app.screens.campaign.panel.runs_panel import RunsPanel


@pytest.fixture
def runs_panel(qtbot):
    """Create a RunsPanel for testing."""
    panel = RunsPanel()
    qtbot.addWidget(panel)
    return panel


def test_runs_panel_creation(runs_panel):
    """Test that the runs panel is created correctly."""
    assert runs_panel is not None
    assert hasattr(runs_panel, "main_layout")


def test_runs_panel_has_empty_state(runs_panel):
    """Test that the runs panel displays an empty state initially."""
    # The panel should have widgets (empty state card)
    assert runs_panel.main_layout.count() > 0


def test_runs_panel_signal_exists(runs_panel):
    """Test that the runs panel has the required signal."""
    assert hasattr(runs_panel, "new_run_requested")


def test_new_run_signal_emission(qtbot, runs_panel):
    """Test that the new run signal can be emitted."""
    with qtbot.waitSignal(runs_panel.new_run_requested, timeout=1000):
        runs_panel.new_run_requested.emit()


def test_get_panel_buttons_returns_generate_button(runs_panel):
    """Test that get_panel_buttons returns the Generate New Run button."""
    buttons = runs_panel.get_panel_buttons()

    assert len(buttons) == 1
    assert buttons[0].text() == "Generate New Run"


def test_generate_button_emits_signal(qtbot, runs_panel):
    """Test that clicking the generate button emits the signal."""
    buttons = runs_panel.get_panel_buttons()
    generate_button = buttons[0]

    with qtbot.waitSignal(runs_panel.new_run_requested, timeout=1000):
        qtbot.mouseClick(generate_button, Qt.LeftButton)


def test_clock_icon_creation(runs_panel):
    """Test that the clock icon is created properly."""
    pixmap = runs_panel._get_clock_icon_pixmap()

    assert pixmap is not None
    assert pixmap.width() == 48
    assert pixmap.height() == 48
