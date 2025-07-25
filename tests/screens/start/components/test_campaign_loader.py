"""
Tests for the CampaignLoader component.
"""

import json
import uuid
from datetime import datetime

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
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    campaign_id = str(uuid.uuid4())
    campaign_data = {
        "id": campaign_id,
        "name": "Test Campaign",
        "description": "A test campaign",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "targets": [],
        "parameters": [],
        "initial_dataset": [],
    }
    campaign_dir = campaigns_dir / campaign_id
    campaign_dir.mkdir()
    with open(campaign_dir / f"{campaign_id}.json", "w") as f:
        json.dump(campaign_data, f)

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 1
    assert isinstance(campaigns[0], Campaign)
    assert campaigns[0].name == "Test Campaign"
    assert campaigns[0].id == campaign_id


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

    invalid_id = str(uuid.uuid4())
    invalid_dir = campaigns_dir / invalid_id
    invalid_dir.mkdir()
    with open(invalid_dir / f"{invalid_id}.json", "w") as f:
        f.write("this is not json")

    valid_id = str(uuid.uuid4())
    valid_dir = campaigns_dir / valid_id
    valid_dir.mkdir()
    valid_campaign_data = {
        "id": valid_id,
        "name": "Valid Campaign",
        "description": "A valid campaign",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "targets": [],
        "parameters": [],
        "initial_dataset": [],
    }
    with open(valid_dir / f"{valid_id}.json", "w") as f:
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


def test_load_campaigns_skips_non_directories(workspace):
    """Test that non-directory items in campaigns folder are skipped."""
    # Arrange
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME

    # Create a file (not directory) in campaigns dir
    with open(campaigns_dir / "not_a_campaign.txt", "w") as f:
        f.write("This is not a campaign")

    # Create valid campaign
    valid_id = str(uuid.uuid4())
    valid_dir = campaigns_dir / valid_id
    valid_dir.mkdir()
    valid_campaign_data = {
        "id": valid_id,
        "name": "Valid Campaign",
        "description": "A valid campaign",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "targets": [],
        "parameters": [],
        "initial_dataset": [],
    }
    with open(valid_dir / f"{valid_id}.json", "w") as f:
        json.dump(valid_campaign_data, f)

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 1
    assert campaigns[0].name == "Valid Campaign"


def test_update_campaign_creates_directory_structure(workspace):
    """Test that update_campaign creates proper directory structure."""
    # Arrange
    loader = CampaignLoader(str(workspace))
    campaign = Campaign(name="Test Campaign", description="Test description")

    # Act
    loader.update_campaign(campaign)

    # Assert
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    campaign_dir = campaigns_dir / campaign.id
    campaign_file = campaign_dir / f"{campaign.id}.json"

    assert campaign_dir.exists()
    assert campaign_file.exists()

    # Verify file content
    with open(campaign_file, "r") as f:
        saved_data = json.load(f)

    assert saved_data["name"] == "Test Campaign"
    assert saved_data["description"] == "Test description"
    assert saved_data["id"] == campaign.id


def test_update_campaign_updates_timestamp(workspace):
    """Test that update_campaign updates the updated_at timestamp."""
    import time

    # Arrange
    loader = CampaignLoader(str(workspace))
    campaign = Campaign(name="Test Campaign")
    original_updated_at = campaign.updated_at

    time.sleep(0.001)  # 1ms delay

    # Act
    loader.update_campaign(campaign)

    # Assert
    assert campaign.updated_at > original_updated_at


def test_update_campaign_with_no_workspace_path():
    """Test that update_campaign handles missing workspace path gracefully."""
    # Arrange
    loader = CampaignLoader("")  # Empty workspace path
    campaign = Campaign(name="Test Campaign")

    # Act & Assert (should not raise exception)
    loader.update_campaign(campaign)


def test_update_campaign_with_no_campaign_name(workspace):
    """Test that update_campaign handles missing campaign name gracefully."""
    # Arrange
    loader = CampaignLoader(str(workspace))
    campaign = Campaign(name="")  # Empty name

    # Act & Assert (should not raise exception)
    loader.update_campaign(campaign)

    # Verify no files were created
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    assert len(list(campaigns_dir.iterdir())) == 0


def test_load_single_campaign_with_missing_file(workspace):
    """Test loading a campaign when the JSON file doesn't exist."""
    # Arrange
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME
    campaign_id = str(uuid.uuid4())
    campaign_dir = campaigns_dir / campaign_id
    campaign_dir.mkdir()
    # Note: Not creating the JSON file

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 0


def test_load_campaigns_with_multiple_valid_campaigns(workspace):
    """Test loading multiple valid campaigns."""
    # Arrange
    campaigns_dir = workspace / WorkspaceConstants.CAMPAIGNS_DIRNAME

    # Create first campaign
    campaign1_id = str(uuid.uuid4())
    campaign1_dir = campaigns_dir / campaign1_id
    campaign1_dir.mkdir()
    campaign1_data = {
        "id": campaign1_id,
        "name": "Campaign 1",
        "description": "First campaign",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "targets": [],
        "parameters": [],
        "initial_dataset": [],
    }
    with open(campaign1_dir / f"{campaign1_id}.json", "w") as f:
        json.dump(campaign1_data, f)

    # Create second campaign
    campaign2_id = str(uuid.uuid4())
    campaign2_dir = campaigns_dir / campaign2_id
    campaign2_dir.mkdir()
    campaign2_data = {
        "id": campaign2_id,
        "name": "Campaign 2",
        "description": "Second campaign",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "targets": [],
        "parameters": [],
        "initial_dataset": [],
    }
    with open(campaign2_dir / f"{campaign2_id}.json", "w") as f:
        json.dump(campaign2_data, f)

    loader = CampaignLoader(str(workspace))

    # Act
    campaigns = loader.load_campaigns()

    # Assert
    assert len(campaigns) == 2
    campaign_names = [c.name for c in campaigns]
    assert "Campaign 1" in campaign_names
    assert "Campaign 2" in campaign_names
