from PySide6.QtCore import Qt

from app.main_application import MainApplication
from app.screens.campaign.campaign_wizard import CampaignWizard
from app.screens.start.start_screen import StartScreen


def test_main_application_creation(qapp):
    """Test if the main application window is created."""
    window = MainApplication()
    assert window is not None
    assert window.isVisible() is False  # Should not be visible until .show() is called


def test_initial_screen_is_start_screen(qapp):
    """Test if the initial screen is the StartScreen."""
    window = MainApplication()
    assert isinstance(window.stacked_widget.currentWidget(), StartScreen)


def test_navigation_to_campaign_wizard(qtbot):
    """Test navigation from StartScreen to CampaignWizard."""
    window = MainApplication()
    qtbot.addWidget(window)
    window.show()

    # Initially, we are on the start screen
    assert isinstance(window.stacked_widget.currentWidget(), StartScreen)

    # Simulate clicking the 'New Campaign' button
    start_screen = window.start_screen
    qtbot.mouseClick(start_screen.new_campaign_btn, Qt.LeftButton)

    # Now, we should be on the campaign wizard
    assert isinstance(window.stacked_widget.currentWidget(), CampaignWizard)


def test_navigation_back_to_start_screen(qtbot):
    """Test navigation from CampaignWizard back to StartScreen."""
    window = MainApplication()
    qtbot.addWidget(window)
    window.show()

    # Go to campaign wizard first
    window.show_campaign_wizard()
    assert isinstance(window.stacked_widget.currentWidget(), CampaignWizard)

    # Simulate clicking the 'Back' button
    campaign_wizard = window.campaign_wizard
    campaign_wizard.back_to_start_requested.emit()

    # Now, we should be back on the start screen
    assert isinstance(window.stacked_widget.currentWidget(), StartScreen)
