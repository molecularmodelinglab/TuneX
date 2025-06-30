"""
Data models for the campaign.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models.parameters import ParameterSerializer
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

    def reset(self):
        """Reset all campaign data to its initial state."""
        self.name = ""
        self.description = ""
        self.target = Target()
        self.parameters.clear()
        self.initial_dataset.clear()

    def get_parameter_data(self) -> List[Dict[str, Any]]:
        """Serialize parameters to a list of dictionaries."""
        serializer = ParameterSerializer()
        return serializer.serialize_parameters(self.parameters)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        """Create a Campaign instance from a dictionary."""
        serializer = ParameterSerializer()
        parameters = serializer.deserialize_parameters(data.get("parameters", []))

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            target=Target(**data.get("target", {})),
            parameters=parameters,
            initial_dataset=data.get("initial_dataset", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Campaign instance to a dictionary."""
        serializer = ParameterSerializer()
        return {
            "name": self.name,
            "description": self.description,
            "target": {
                "name": self.target.name,
                "mode": self.target.mode,
            },
            "parameters": serializer.serialize_parameters(self.parameters),
            "initial_dataset": self.initial_dataset,
        }
