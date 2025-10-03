"""
Centralized About/credits information for TuneX.

"""

from __future__ import annotations

import os
from typing import List


# Default values; update as needed
PROGRAMMERS_DEFAULT: List[str] = [
    "Kelvin P. Idanwekhai",
    "Valeria Kaneva",
]

INSTITUTION_DEFAULT = "Laboratory for Molecular Modelling, \
Eshelman School of Pharmacy, \
University of North Carolina at Chapel Hill, USA"


def get_programmers() -> List[str]:
    """Return list of programmer names.

    Honors env var TUNEX_PROGRAMMERS (comma-separated) if set.
    """
    env_val = os.getenv("TUNEX_PROGRAMMERS")
    if env_val:
        parsed = [p.strip() for p in env_val.split(",") if p.strip()]
        if parsed:
            return parsed
    return PROGRAMMERS_DEFAULT


def get_institution() -> str:
    """Return institution name.

    Honors env var TUNEX_INSTITUTION if set.
    """
    return os.getenv("TUNEX_INSTITUTION", INSTITUTION_DEFAULT)


def build_about_text(app_name: str = "BASIL", version: str | None = None) -> str:
    """Compose a simple About message string for display."""
    lines: List[str] = [f"{app_name} : Bayesian Approach to Scientific Iteration and Learning"]
    if version:
        lines[0] += f" v{version}"
    lines += [
        "",
        f"Developed By: {', '.join(get_programmers())}",
        f"Scientific Software from {get_institution()}",
    ]
    return "\n".join(lines)
