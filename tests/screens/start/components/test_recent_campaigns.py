"""
Tests for the RecentCampaignsWidget component.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.models.campaign import Campaign
from app.screens.start.components.recent_campaigns import RecentCampaignsWidget
from app.shared.components.campaign_card import CampaignCard


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def recent_campaigns_widget(qapp):
    """Create a RecentCampaignsWidget instance for testing."""
    return RecentCampaignsWidget()


def test_update_campaigns_updates_internal_list(recent_campaigns_widget):
    """Test that update_campaigns updates the internal campaigns list."""
    # Arrange
    campaigns = [Campaign(name="Test Campaign 1"), Campaign(name="Test Campaign 2")]

    # Act
    recent_campaigns_widget.update_campaigns(campaigns)

    # Assert
    assert recent_campaigns_widget.campaigns == campaigns


def test_show_empty_state_when_no_campaigns(recent_campaigns_widget):
    """Test that empty state is shown when there are no campaigns."""
    # Act
    recent_campaigns_widget.update_campaigns([])

    # Assert
    # Should have one widget (the empty state card)
    assert recent_campaigns_widget.main_layout.count() == 1

    # Get the widget and check it's an empty state card
    widget = recent_campaigns_widget.main_layout.itemAt(0).widget()
    assert widget is not None
    # Check that it's an EmptyStateCard by checking its object name
    assert widget.objectName() == "EmptyStateCard"


def test_show_campaigns_when_campaigns_exist(recent_campaigns_widget):
    """Test that campaigns are shown when they exist."""
    # Arrange
    campaigns = [Campaign(name="Test Campaign 1"), Campaign(name="Test Campaign 2")]

    # Act
    recent_campaigns_widget.update_campaigns(campaigns)

    # Assert
    # Should have 2 widgets (campaign cards)
    assert recent_campaigns_widget.main_layout.count() == 2

    # Check that each widget is a CampaignCard
    for i in range(recent_campaigns_widget.main_layout.count()):
        widget = recent_campaigns_widget.main_layout.itemAt(i).widget()
        assert isinstance(widget, CampaignCard)


def test_sort_campaigns_by_updated_at_descending(recent_campaigns_widget):
    """Test that campaigns are sorted by updated_at in descending order."""
    # Arrange
    # Create campaigns with different updated_at times
    now = datetime.now()
    campaign1 = Campaign(name="Campaign 1")
    campaign1.updated_at = now - timedelta(days=3)  # Oldest

    campaign2 = Campaign(name="Campaign 2")
    campaign2.updated_at = now - timedelta(days=1)  # Newest

    campaign3 = Campaign(name="Campaign 3")
    campaign3.updated_at = now - timedelta(days=2)  # Middle

    campaigns = [campaign1, campaign2, campaign3]

    # Act
    recent_campaigns_widget.update_campaigns(campaigns)

    # Assert
    # Check that we have 3 campaign cards
    assert recent_campaigns_widget.main_layout.count() == 3

    # Check that they are displayed in the correct order (newest first)
    first_card = recent_campaigns_widget.main_layout.itemAt(0).widget()
    second_card = recent_campaigns_widget.main_layout.itemAt(1).widget()
    third_card = recent_campaigns_widget.main_layout.itemAt(2).widget()

    assert first_card.campaign.name == "Campaign 2"  # Newest
    assert second_card.campaign.name == "Campaign 3"  # Middle
    assert third_card.campaign.name == "Campaign 1"  # Oldest


def test_limit_to_5_most_recent_campaigns(recent_campaigns_widget):
    """Test that only the 5 most recent campaigns are displayed."""
    # Arrange
    now = datetime.now()
    campaigns = []
    for i in range(7):  # Create 7 campaigns
        campaign = Campaign(name=f"Campaign {i}")
        campaign.updated_at = now - timedelta(days=7 - i)  # Campaign 0 is oldest, Campaign 6 is newest
        campaigns.append(campaign)

    # Act
    recent_campaigns_widget.update_campaigns(campaigns)

    # Assert
    # Should only show 5 campaigns (the most recent ones)
    assert recent_campaigns_widget.main_layout.count() == 5

    # Check that they are the 5 most recent (Campaigns 2-6)
    for i in range(5):
        card = recent_campaigns_widget.main_layout.itemAt(i).widget()
        expected_campaign_index = 6 - i  # Campaign 6, 5, 4, 3, 2
        assert card.campaign.name == f"Campaign {expected_campaign_index}"


def test_campaign_selection_signal_emitted(recent_campaigns_widget):
    """Test that campaign selection signal is emitted when a campaign card is clicked."""
    # Arrange
    campaign = Campaign(name="Test Campaign")
    recent_campaigns_widget.update_campaigns([campaign])

    # Create a mock slot to receive the signal
    mock_slot = MagicMock()
    recent_campaigns_widget.campaign_selected.connect(mock_slot)

    # Get the campaign card
    card = recent_campaigns_widget.main_layout.itemAt(0).widget()

    # Act
    # Simulate clicking on the campaign card
    card.campaign_selected.emit(campaign)

    # Assert
    # Check that the signal was emitted with the correct campaign
    mock_slot.assert_called_once_with(campaign)


def test_handle_none_updated_at_values(recent_campaigns_widget):
    """Test that campaigns with None updated_at values are handled correctly."""
    # Arrange
    campaign1 = Campaign(name="Campaign 1")
    campaign1.updated_at = None  # No updated time

    campaign2 = Campaign(name="Campaign 2")
    campaign2.updated_at = datetime.now()  # Has updated time

    campaigns = [campaign1, campaign2]

    # Act
    recent_campaigns_widget.update_campaigns(campaigns)

    # Assert
    # Should show both campaigns, with the one with updated_at appearing first
    assert recent_campaigns_widget.main_layout.count() == 2

    # The campaign with updated_at should be first
    first_card = recent_campaigns_widget.main_layout.itemAt(0).widget()
    assert first_card.campaign.name == "Campaign 2"

    # The campaign without updated_at should be second
    second_card = recent_campaigns_widget.main_layout.itemAt(1).widget()
    assert second_card.campaign.name == "Campaign 1"


def test_clear_layout_before_updating(recent_campaigns_widget):
    """Test that the layout is cleared before updating with new campaigns."""
    # Arrange
    # First set of campaigns
    campaigns1 = [Campaign(name="Campaign 1"), Campaign(name="Campaign 2")]
    recent_campaigns_widget.update_campaigns(campaigns1)

    # Verify initial state
    assert recent_campaigns_widget.main_layout.count() == 2

    # New set of campaigns
    campaigns2 = [Campaign(name="Campaign 3")]

    # Act
    recent_campaigns_widget.update_campaigns(campaigns2)

    # Assert
    # Should only show the new campaign
    assert recent_campaigns_widget.main_layout.count() == 1
    card = recent_campaigns_widget.main_layout.itemAt(0).widget()
    assert card.campaign.name == "Campaign 3"
