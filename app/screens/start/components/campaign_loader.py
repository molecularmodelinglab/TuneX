"""
Business logic for loading campaigns.
"""

import json
import logging
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
        self.logger = logging.getLogger(__name__)
        self.campaign_filename_map: dict[str, str] = {}

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
        for campaign in os.listdir(campaigns_dir):
            campaign_path = os.path.join(campaigns_dir, campaign)
            if not os.path.isdir(campaign_path):
                continue

            full_campaign_path = os.path.join(campaign_path, f"{campaign}.json")
            campaign_data = self._load_single_campaign(full_campaign_path)
            if campaign_data:
                campaigns.append(campaign_data)
                self.campaign_filename_map[campaign_data.id] = campaign_data.name
        return campaigns

    def _load_single_campaign(self, campaign_path: str) -> Campaign | None:
        """
        Load a single campaign from a directory.

        Args:
            campaigns_dir: The directory containing campaigns.
            item_name: The name of the campaign file.

        Returns:
            A Campaign object or None if loading fails.
        """
        if not os.path.exists(campaign_path):
            self.logger.warning(f"Campaign path {campaign_path} does not exist")
            return None
        try:
            with open(campaign_path, "r") as f:
                campaign_data = json.load(f)
            return Campaign.from_dict(campaign_data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(f"Skipping invalid campaign in {campaign_path}: {e}")
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
        campaign_path = os.path.join(campaigns_dir, campaign.id)
        os.makedirs(campaign_path, exist_ok=True)

        with open(os.path.join(campaign_path, filename), "w") as f:
            json.dump(campaign.to_dict(), f, indent=4)

        self.logger.info(f"Campaign '{campaign.name}' updated: {campaign_path}")

    def delete_campaign(self, campaign):
        """Delete a campaign from the loader's internal tracking."""
        if hasattr(self, "campaign_filename_map") and campaign.id in self.campaign_filename_map:
            del self.campaign_filename_map[campaign.id]

        self.logger.info(f"Campaign {campaign.name} (ID: {campaign.id}) removed from loader tracking")
