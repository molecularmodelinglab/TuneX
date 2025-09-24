"""
Data model for a workspace.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class Workspace:
    """Data model for a workspace."""

    path: str = ""
    name: str = ""
    accessed_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Auto-generate name from path if not provided."""
        if not self.name and self.path:
            self.name = os.path.basename(os.path.normpath(self.path)) or "Untitled Workspace"

    def reset(self):
        """Reset all workspace data to its initial state."""

        self.path = ""
        self.name = ""
        self.accessed_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        """Create a Workspace instance from a dictionary."""

        accessed_at = data.get("accessed_at", datetime.now())
        if isinstance(accessed_at, str):
            accessed_at = datetime.fromisoformat(accessed_at)

        return cls(
            path=data.get("path", ""),
            name=data.get("name", ""),
            accessed_at=accessed_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Campaign instance to a dictionary."""
        return {
            "path": self.path,
            "name": self.name,
            "accessed_at": self.accessed_at.isoformat() if isinstance(self.accessed_at, datetime) else self.accessed_at,
        }
