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

    def update_campaign(self, campaign: Campaign, old_name: str = None) -> None:
        """
        Update an existing campaign in the workspace.

        Args:
            campaign: The Campaign object to update.
            old_name: The previous name of the campaign (for renaming).
        """
        if not self.workspace_path or not campaign.name:
            return

        campaigns_dir = os.path.join(self.workspace_path, WorkspaceConstants.CAMPAIGNS_DIRNAME)
        if not os.path.exists(campaigns_dir):
            os.makedirs(campaigns_dir)

        campaign.updated_at = datetime.now()

        if old_name and old_name != campaign.name:
            old_filename = self.campaign_filename_map.get(old_name)
            if old_filename:
                old_campaign_path = os.path.join(campaigns_dir, old_filename)

                if os.path.exists(old_campaign_path):
                    with open(old_campaign_path, "w") as f:
                        json.dump(campaign.to_dict(), f, indent=4)

                    self.campaign_filename_map[campaign.name] = old_filename
                    del self.campaign_filename_map[old_name]

                    print(f"Updated campaign '{old_name}' to '{campaign.name}' in file: {old_filename}")
                else:
                    print(f"Warning: Campaign file for '{old_name}' not found")
                    self._create_new_campaign_file(campaign, campaigns_dir)
            else:
                print(f"Warning: No filename mapping found for campaign '{old_name}'")
                self._create_new_campaign_file(campaign, campaigns_dir)
        else:
            existing_filename = self.campaign_filename_map.get(campaign.name)
            if existing_filename:
                campaign_path = os.path.join(campaigns_dir, existing_filename)
                with open(campaign_path, "w") as f:
                    json.dump(campaign.to_dict(), f, indent=4)
                print(f"Campaign updated: {campaign_path}")
            else:
                self._create_new_campaign_file(campaign, campaigns_dir)

    def _create_new_campaign_file(self, campaign: Campaign, campaigns_dir: str):
        """Create a new campaign file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{campaign.name}_{timestamp}.json"
        campaign_path = os.path.join(campaigns_dir, filename)

        with open(campaign_path, "w") as f:
            json.dump(campaign.to_dict(), f, indent=4)

        self.campaign_filename_map[campaign.name] = filename
        print(f"Created new campaign file: {campaign_path}")

    def save_campaign(self, campaign: Campaign) -> None:
        """
        Save a campaign (for newly created campaigns).

        Args:
            campaign: The Campaign object to save.
        """
        if not self.workspace_path:
            return

        campaigns_dir = os.path.join(self.workspace_path, WorkspaceConstants.CAMPAIGNS_DIRNAME)
        if not os.path.exists(campaigns_dir):
            os.makedirs(campaigns_dir)

        self._create_new_campaign_file(campaign, campaigns_dir)
