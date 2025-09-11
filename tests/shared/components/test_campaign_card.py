"""
Tests for the CampaignCard component.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.models.campaign import Campaign
from app.shared.components.campaign_card import CampaignCard


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_campaign():
    """Create a sample campaign for testing."""
    campaign = Campaign(name="Test Campaign", description="A test campaign")
    campaign.updated_at = datetime(2023, 1, 15, 10, 30, 0)
    return campaign


@pytest.fixture
def campaign_card(qapp, sample_campaign):
    """Create a CampaignCard instance for testing."""
    return CampaignCard(sample_campaign)


def test_campaign_card_initialization(campaign_card, sample_campaign):
    """Test that CampaignCard is initialized correctly."""
    # Assert
    assert campaign_card.campaign == sample_campaign
    assert campaign_card.objectName() == "CampaignCard"
    from PySide6.QtCore import Qt

    assert campaign_card.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_campaign_card_displays_campaign_name(campaign_card, sample_campaign):
    """Test that CampaignCard displays the campaign name."""
    # Assert
    assert campaign_card.name_label.text() == sample_campaign.name


def test_campaign_card_displays_campaign_details(campaign_card, sample_campaign):
    """Test that CampaignCard displays campaign details."""
    # Assert
    # Since our sample campaign has no parameters, it should show "No parameters defined"
    assert campaign_card.details_label.text() == "No parameters defined"


def test_campaign_card_displays_last_modified_date(campaign_card, sample_campaign):
    """Test that CampaignCard displays the last modified date."""
    # Assert
    expected_date = "Modified Jan 15, 2023"
    assert campaign_card.date_label.text() == expected_date


def test_campaign_card_emits_signal_on_click(campaign_card, sample_campaign):
    """Test that CampaignCard emits campaign_selected signal when clicked."""
    # Arrange
    mock_slot = MagicMock()
    campaign_card.campaign_selected.connect(mock_slot)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QMouseEvent

    # Act
    # Create a proper mouse event
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        campaign_card.rect().center(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    campaign_card.mousePressEvent(event)

    # Assert
    mock_slot.assert_called_once_with(sample_campaign)


def test_campaign_card_with_parameters(sample_campaign):
    """Test that CampaignCard displays parameter count correctly."""
    # Arrange
    # Add some mock parameters to the campaign
    sample_campaign.parameters = ["param1", "param2", "param3"]

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = CampaignCard(sample_campaign)

    # Assert
    assert card.details_label.text() == "3 parameters"


def test_campaign_card_with_single_parameter(sample_campaign):
    """Test that CampaignCard displays singular form for single parameter."""
    # Arrange
    # Add one mock parameter to the campaign
    sample_campaign.parameters = ["param1"]

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = CampaignCard(sample_campaign)

    # Assert
    assert card.details_label.text() == "1 parameter"


def test_campaign_card_with_none_updated_at():
    """Test that CampaignCard handles None updated_at correctly."""
    # Arrange
    campaign = Campaign(name="Test Campaign")
    campaign.updated_at = None

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = CampaignCard(campaign)

    # Assert
    assert card.date_label.text() == "Recently created"


def test_campaign_card_with_empty_name():
    """Test that CampaignCard handles empty campaign name."""
    # Arrange
    campaign = Campaign(name="")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = CampaignCard(campaign)

    # Assert
    # Should display empty name
    assert card.name_label.text() == ""

    # Should use 'C' as default initial for avatar
    # We can't easily test the pixmap content, but we can verify the card was created
    assert card.icon_label is not None
