"""
Tests for the CampaignLoader component.
"""

import json

import pytest

from app.models.campaign import Campaign
from app.screens.start.components.campaign_loader import CampaignLoader
from app.shared.constants import WorkspaceConstants


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace with a campaigns directory."""
    workspace_path = tmp_path / "test_workspace"
    workspace_path.mkdir()
    (workspace_path / WorkspaceConstants.CAMPAIGNS_DIRNAME).mkdir()
    return workspace_path


def test_load_campaigns_successfully(workspace):
    """Test that campaigns are loaded successfully from a valid workspace."""
    # Arrange
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    campaign_data = {"name": "Test Campaign", "description": "A test campaign"}

    with open(campaigns_dir / "campaign1.json", "w") as f:
        json.dump(campaign_data, f)

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 1
    assert isinstance(campaigns[0], Campaign)
    assert campaigns[0].name == "Test Campaign"


def test_load_campaigns_with_no_campaigns(workspace):
    """Test loading from a workspace with an empty campaigns directory."""
    # Arrange
    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 0


def test_load_campaigns_with_invalid_json(workspace):
    """Test that invalid campaign files are skipped."""
    # Arrange
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    with open(campaigns_dir / "invalid.json", "w") as f:
        f.write("this is not json")

    valid_campaign_data = {"name": "Valid Campaign", "description": "A valid campaign"}
    with open(campaigns_dir / "valid.json", "w") as f:
        json.dump(valid_campaign_data, f)

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 1
    assert campaigns[0].name == "Valid Campaign"


def test_load_campaigns_with_missing_campaigns_dir(tmp_path):
    """Test loading from a workspace where the campaigns directory is missing."""
    # Arrange
    workspace_path = tmp_path / "empty_workspace"
    workspace_path.mkdir()
    loader = CampaignLoader(str(workspace_path))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 0
