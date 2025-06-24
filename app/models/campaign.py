"""
Data models for the campaign.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models.parameters.base import BaseParameter


@dataclass
class Target:
    """Data model for the campaign target."""

    name: str = ""
    mode: str = "Max"


@dataclass
class Campaign:
    """Data model for a campaign."""

    name: str = ""
    description: str = ""
    target: Target = field(default_factory=Target)
    parameters: List[BaseParameter] = field(default_factory=list)
    initial_dataset: List[Dict[str, Any]] = field(default_factory=list)

    def get_parameter_data(self) -> List[Dict[str, Any]]:
        """Serialize parameters to a list of dictionaries."""
        from app.screens.campaign.steps.components.parameter_managers import (
            ParameterSerializer,
        )

        serializer = ParameterSerializer()
        return serializer.serialize_parameters(self.parameters)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        """Create a Campaign instance from a dictionary."""
        from app.screens.campaign.steps.components.parameter_managers import (
            ParameterSerializer,
        )

        serializer = ParameterSerializer()
        parameters = serializer.deserialize_parameters(data.get("parameters", []))

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            target=Target(**data.get("target", {})),
            parameters=parameters,
            initial_dataset=data.get("initial_dataset", []),
        )
