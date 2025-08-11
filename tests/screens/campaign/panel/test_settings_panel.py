"""
Tests for the SettingsPanel functionality.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt

from app.models.campaign import Campaign, Target
from app.screens.campaign.panel.settings_panel import SettingsPanel


@pytest.fixture
def sample_campaign():
    """Create a sample campaign for testing."""
    campaign = Campaign()
    campaign.name = "Test Campaign"
    campaign.description = "A test campaign for unit testing"
    campaign.targets = [Target(name="Yield", mode="Max"), Target(name="Purity", mode="Min")]
    return campaign


@pytest.fixture
def settings_panel(qtbot, sample_campaign):
    """Create a SettingsPanel for testing."""
    panel = SettingsPanel(sample_campaign, workspace_path="test_workspace")
    qtbot.addWidget(panel)
    return panel


def test_settings_panel_creation(settings_panel, sample_campaign):
    """Test that the settings panel is created correctly."""
    assert settings_panel.campaign == sample_campaign
    assert settings_panel.workspace_path == "test_workspace"
    assert hasattr(settings_panel, "name_input")
    assert hasattr(settings_panel, "description_input")


def test_campaign_data_loaded_correctly(settings_panel, sample_campaign):
    """Test that campaign data is loaded into the form fields."""
    assert settings_panel.name_input.text() == sample_campaign.name
    assert settings_panel.description_input.toPlainText() == sample_campaign.description


def test_initial_form_state_is_readonly(settings_panel):
    """Test that form fields are initially read-only."""
    assert settings_panel.name_input.isReadOnly() is True
    assert settings_panel.description_input.isReadOnly() is True
    assert settings_panel.rename_button.text() == "Rename"
    assert settings_panel.edit_button.text() == "Edit"


def test_name_edit_mode_toggle(qtbot, settings_panel):
    """Test toggling name field edit mode."""
    # Initially read-only
    assert settings_panel.name_input.isReadOnly() is True

    # Click rename button to enter edit mode
    qtbot.mouseClick(settings_panel.rename_button, Qt.LeftButton)

    # Should now be editable
    assert settings_panel.name_input.isReadOnly() is False
    assert settings_panel.rename_button.text() == "Save"


def test_description_edit_mode_toggle(qtbot, settings_panel):
    """Test toggling description field edit mode."""
    # Initially read-only
    assert settings_panel.description_input.isReadOnly() is True

    # Click edit button to enter edit mode
    qtbot.mouseClick(settings_panel.edit_button, Qt.LeftButton)

    # Should now be editable
    assert settings_panel.description_input.isReadOnly() is False
    assert settings_panel.edit_button.text() == "Save"


@patch("app.screens.campaign.panel.settings_panel.CampaignLoader")
def test_successful_name_save(mock_campaign_loader, qtbot, settings_panel, sample_campaign):
    """Test successful campaign name saving."""
    # Mock the campaign loader
    mock_loader_instance = Mock()
    mock_campaign_loader.return_value = mock_loader_instance
    settings_panel.campaign_loader = mock_loader_instance

    # Enter edit mode
    qtbot.mouseClick(settings_panel.rename_button, Qt.LeftButton)

    # Change the name
    settings_panel.name_input.clear()
    qtbot.keyClicks(settings_panel.name_input, "New Campaign Name")

    # Save the changes
    with qtbot.waitSignal(settings_panel.campaign_renamed, timeout=1000):
        qtbot.mouseClick(settings_panel.rename_button, Qt.LeftButton)

    # Verify the campaign was updated
    assert settings_panel.campaign.name == "New Campaign Name"
    assert settings_panel.name_input.isReadOnly() is True
    assert settings_panel.rename_button.text() == "Rename"

    # Verify the loader was called
    mock_loader_instance.update_campaign.assert_called_once()


@patch("app.screens.campaign.panel.settings_panel.CampaignLoader")
def test_successful_description_save(mock_campaign_loader, qtbot, settings_panel, sample_campaign):
    """Test successful campaign description saving."""
    # Mock the campaign loader
    mock_loader_instance = Mock()
    mock_campaign_loader.return_value = mock_loader_instance
    settings_panel.campaign_loader = mock_loader_instance

    # Enter edit mode
    qtbot.mouseClick(settings_panel.edit_button, Qt.LeftButton)

    # Change the description
    settings_panel.description_input.clear()
    qtbot.keyClicks(settings_panel.description_input, "New campaign description")

    # Save the changes
    with qtbot.waitSignal(settings_panel.campaign_description_updated, timeout=1000):
        qtbot.mouseClick(settings_panel.edit_button, Qt.LeftButton)

    # Verify the campaign was updated
    assert settings_panel.campaign.description == "New campaign description"
    assert settings_panel.description_input.isReadOnly() is True
    assert settings_panel.edit_button.text() == "Edit"

    # Verify the loader was called
    mock_loader_instance.update_campaign.assert_called_once()


@patch("app.screens.campaign.panel.settings_panel.CampaignLoader")
def test_save_failure_reverts_changes(mock_campaign_loader, qtbot, settings_panel, sample_campaign):
    """Test that save failure reverts changes."""
    # Mock the campaign loader to fail
    mock_loader_instance = Mock()
    mock_loader_instance.update_campaign.side_effect = Exception("Save failed")
    mock_campaign_loader.return_value = mock_loader_instance
    settings_panel.campaign_loader = mock_loader_instance

    original_name = sample_campaign.name

    # Enter edit mode
    qtbot.mouseClick(settings_panel.rename_button, Qt.LeftButton)

    # Change the name
    settings_panel.name_input.clear()
    qtbot.keyClicks(settings_panel.name_input, "Failed Name Change")

    # Try to save (should fail)
    qtbot.mouseClick(settings_panel.rename_button, Qt.LeftButton)

    # Verify the campaign name was reverted
    assert settings_panel.campaign.name == original_name
    assert settings_panel.name_input.text() == original_name
    assert settings_panel.name_input.isReadOnly() is True


def test_get_panel_buttons_returns_correct_buttons(settings_panel):
    """Test that get_panel_buttons returns the expected buttons."""
    buttons = settings_panel.get_panel_buttons()

    # Should return delete and export buttons
    assert len(buttons) == 2

    button_texts = [button.text() for button in buttons]
    assert "Delete Campaign" in button_texts
    assert "Export Data" in button_texts


def test_campaign_data_update(settings_panel):
    """Test updating campaign data programmatically."""
    new_campaign = Campaign()
    new_campaign.name = "Updated Campaign"
    new_campaign.description = "Updated description"

    settings_panel.update_campaign_data(new_campaign)

    assert settings_panel.campaign == new_campaign
    assert settings_panel.name_input.text() == "Updated Campaign"
    assert settings_panel.description_input.toPlainText() == "Updated description"


def test_workspace_path_update(settings_panel):
    """Test updating workspace path."""
    new_workspace_path = "new_test_workspace"
    settings_panel.set_workspace_path(new_workspace_path)

    assert settings_panel.workspace_path == new_workspace_path
    assert settings_panel.campaign_loader is not None


def test_panel_without_campaign_loader():
    """Test panel behavior when no campaign loader is available."""
    panel = SettingsPanel()

    # Should not crash
    result = panel._save_campaign_changes()
    assert result is False


def test_save_without_campaign(settings_panel):
    """Test save behavior when no campaign is set."""
    settings_panel.campaign = None

    result = settings_panel._save_campaign_changes()
    assert result is False


@patch("app.screens.campaign.panel.settings_panel.CampaignExporter")
def test_export_button_functionality(mock_exporter, qtbot, settings_panel):
    """Test that the export button calls the exporter correctly."""
    mock_exporter.export_campaign_to_csv.return_value = True

    buttons = settings_panel.get_panel_buttons()
    export_button = next(btn for btn in buttons if btn.text() == "Export Data")

    qtbot.mouseClick(export_button, Qt.LeftButton)

    mock_exporter.export_campaign_to_csv.assert_called_once_with(settings_panel.campaign, settings_panel)


@patch("app.screens.campaign.panel.settings_panel.ConfirmationDialog")
def test_delete_button_shows_confirmation_dialog(mock_dialog, qtbot, settings_panel):
    """Test that the delete button shows confirmation dialog."""
    mock_dialog.show_confirmation.return_value = False

    buttons = settings_panel.get_panel_buttons()
    delete_button = next(btn for btn in buttons if btn.text() == "Delete Campaign")

    qtbot.mouseClick(delete_button, Qt.LeftButton)

    mock_dialog.show_confirmation.assert_called_once()

    # Verify campaign_deleted signal was NOT emitted (user cancelled)
    # This is implicit - if the signal was emitted, the test would need to handle it


@patch("app.screens.campaign.panel.settings_panel.ConfirmationDialog")
@patch("app.screens.campaign.panel.settings_panel.InfoDialog")
def test_delete_campaign_success_emits_signal(mock_info_dialog, mock_confirmation, qtbot, settings_panel):
    """Test that successful campaign deletion emits the signal."""
    mock_confirmation.show_confirmation.return_value = True

    settings_panel._delete_campaign_files = lambda: True

    buttons = settings_panel.get_panel_buttons()
    delete_button = next(btn for btn in buttons if btn.text() == "Delete Campaign")

    with qtbot.waitSignal(settings_panel.campaign_deleted, timeout=1000):
        qtbot.mouseClick(delete_button, Qt.LeftButton)

    mock_info_dialog.show_info.assert_called_once()


@patch("app.screens.campaign.panel.settings_panel.ConfirmationDialog")
@patch("app.screens.campaign.panel.settings_panel.ErrorDialog")
def test_delete_campaign_failure_shows_error(mock_error_dialog, mock_confirmation, qtbot, settings_panel):
    """Test that failed campaign deletion shows error dialog."""
    mock_confirmation.show_confirmation.return_value = True

    settings_panel._delete_campaign_files = lambda: False

    buttons = settings_panel.get_panel_buttons()
    delete_button = next(btn for btn in buttons if btn.text() == "Delete Campaign")

    qtbot.mouseClick(delete_button, Qt.LeftButton)

    mock_error_dialog.show_error.assert_called_once()
