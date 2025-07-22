"""
Business logic for loading campaigns.
"""

import json
import os
from datetime import datetime
from typing import List

from app.models.campaign import Campaign
from app.shared.constants import WorkspaceConstants


class CampaignLoader:
    """Handles loading campaigns from the workspace."""

    def __init__(self, workspace_path: str):
        """
        Initialize the campaign loader.

        Args:
            workspace_path: The path to the current workspace.
        """
        self.workspace_path = workspace_path
        self.campaign_filename_map = {}

    def load_campaigns(self) -> List[Campaign]:
        """
        Load all valid campaigns from the current workspace.

        Returns:
            A list of loaded campaigns.
        """
        if not self.workspace_path:
            return []

        campaigns_dir = os.path.join(self.workspace_path, WorkspaceConstants.CAMPAIGNS_DIRNAME)
        if not os.path.exists(campaigns_dir):
            return []

        campaigns = []
        self.campaign_filename_map.clear()
        for item_name in os.listdir(campaigns_dir):
            campaign = self._load_single_campaign(campaigns_dir, item_name)
            if campaign:
                campaigns.append(campaign)
                self.campaign_filename_map[campaign.name] = item_name
        return campaigns

    def _load_single_campaign(self, campaigns_dir: str, item_name: str) -> Campaign | None:
        """
        Load a single campaign from a directory.

        Args:
            campaigns_dir: The directory containing campaigns.
            item_name: The name of the campaign file.

        Returns:
            A Campaign object or None if loading fails.
        """
        campaign_path = os.path.join(campaigns_dir, item_name)
        if not os.path.exists(campaign_path):
            print(f"Campaign path {campaign_path} does not exist")
            return None
        try:
            with open(campaign_path, "r") as f:
                campaign_data = json.load(f)
            return Campaign.from_dict(campaign_data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Skipping invalid campaign in {item_name}: {e}")
            return None

    def update_campaign(self, campaign: Campaign) -> None:
        """
        Update an existing campaign in the workspace.

        Args:
            campaign: The Campaign object to update.
        """
        if not self.workspace_path or not campaign.name:
            return

        campaigns_dir = os.path.join(self.workspace_path, WorkspaceConstants.CAMPAIGNS_DIRNAME)
        if not os.path.exists(campaigns_dir):
            os.makedirs(campaigns_dir)

        campaign.updated_at = datetime.now()

        filename = f"{campaign.id}.json"
        campaign_path = os.path.join(campaigns_dir, filename)

        # Save the updated campaign data
        with open(campaign_path, "w") as f:
            json.dump(campaign.to_dict(), f, indent=4)

        print(f"Campaign '{campaign.name}' updated: {campaign_path}")
