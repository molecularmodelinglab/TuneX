from enum import Enum


class ScreenName(Enum):
    """Screen names for navigation."""

    START = "start"
    CAMPAIGN_WIZARD = "campaign_wizard"
    BROWSE_CAMPAIGNS = "browse_campaigns"
    SELECT_WORKSPACE = "select_workspace"


class WorkspaceConstants:
    """Constants for workspace structure and files."""

    WORKSPACE_CONFIG_FILENAME = "basil_workspace.json"
    CAMPAIGNS_DIRNAME = "campaigns"

    # Workspace config keys
    WORKSPACE_NAME_KEY = "name"
    WORKSPACE_CREATED_KEY = "created"
    WORKSPACE_VERSION_KEY = "version"
    WORKSPACE_VERSION_VALUE = "1.0"
