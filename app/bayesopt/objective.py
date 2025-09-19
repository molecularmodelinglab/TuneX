"""
Objective and target conversion utilities for BayBE integration.

This module handles the conversion between TuneX targets and BayBE objectives.
"""

from typing import Dict, List, Optional

from baybe.objectives import DesirabilityObjective, SingleTargetObjective
from baybe.targets import NumericalTarget

from app.models.campaign import Target


class ObjectiveConverter:
    """Converts TuneX targets to BayBE objectives."""

    @staticmethod
    def convert_target(tunex_target: Target) -> NumericalTarget:
        """
        Convert a TuneX target to a BayBE target.

        Args:
            tunex_target: TuneX target to convert

        Returns:
            BayBE NumericalTarget

        Raises:
            ValueError: If target configuration is invalid
        """
        # Determine the mode
        if tunex_target.mode.upper() == "MAX":
            minimize = False
        elif tunex_target.mode.upper() == "MIN":
            minimize = True
        elif tunex_target.mode.upper() == "MATCH":
            minimize = None
        else:
            raise ValueError(f"Unsupported target mode: {tunex_target.mode}")

        # Create the target
        target_kwargs = {
            "name": tunex_target.name,
            "minimize": minimize,
        }

        if tunex_target.mode.upper() == "MATCH":
            if tunex_target.min_value is None or tunex_target.max_value is None:
                raise ValueError("MATCH mode requires both min_value and max_value")
            match_value = (tunex_target.min_value + tunex_target.max_value) / 2
            return NumericalTarget.match_triangular(
                name=tunex_target.name,
                match_value=match_value,
                cutoffs=(tunex_target.min_value, tunex_target.max_value),
            )

        if tunex_target.min_value is None or tunex_target.max_value is None:
            return NumericalTarget(**target_kwargs, _enforce_modern_interface=True)
        else:
            return NumericalTarget.normalized_ramp(
                name=tunex_target.name, descending=minimize, cutoffs=(tunex_target.min_value, tunex_target.max_value)
            )

    @staticmethod
    def create_objective(tunex_targets: List[Target]):
        """
        Create a BayBE objective from TuneX targets.

        For single targets, creates a SingleTargetObjective.
        For multiple targets, creates a DesirabilityObjective that combines all targets.

        Args:
            tunex_targets: List of TuneX targets

        Returns:
            BayBE SingleTargetObjective or DesirabilityObjective

        Raises:
            ValueError: If no valid targets found
        """
        if not tunex_targets:
            raise ValueError("No targets provided for optimization")

        if len(tunex_targets) == 1:
            baybe_target = ObjectiveConverter.convert_target(tunex_targets[0])
            return SingleTargetObjective(target=baybe_target)
        else:
            return ObjectiveConverter._create_desirability_objective(tunex_targets)

    @staticmethod
    def _create_desirability_objective(tunex_targets: List[Target]) -> DesirabilityObjective:
        """
        Create a DesirabilityObjective for multi-target optimization.

        The desirability function combines multiple targets into a single score
        where each target contributes based on its weight (default weight = 1.0).

        Args:
            tunex_targets: List of TuneX targets

        Returns:
            BayBE DesirabilityObjective

        Raises:
            ValueError: If target configuration is invalid
        """
        baybe_targets = []
        weights = []

        for target in tunex_targets:
            # Convert target
            baybe_target = ObjectiveConverter.convert_target(target)
            baybe_targets.append(baybe_target)

            # Use specified weight or default to 1.0
            weight = target.weight if target.weight is not None else 1.0
            weights.append(weight)

        return DesirabilityObjective(targets=baybe_targets, weights=weights)

    @staticmethod
    def validate_targets(tunex_targets: List[Target]) -> List[str]:
        """
        Validate TuneX targets for BayBE conversion.

        Args:
            tunex_targets: List of TuneX targets to validate

        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []

        if not tunex_targets:
            errors.append("At least one target must be specified")
            return errors

        for i, target in enumerate(tunex_targets):
            target_errors = ObjectiveConverter._validate_single_target(target, i)
            errors.extend(target_errors)

        # Check for duplicate target names
        target_names = [t.name for t in tunex_targets]
        duplicates = set([name for name in target_names if target_names.count(name) > 1])
        if duplicates:
            errors.append(f"Duplicate target names found: {', '.join(duplicates)}")

        return errors

    @staticmethod
    def _validate_single_target(target: Target, index: int) -> List[str]:
        """
        Validate a single target.

        Args:
            target: Target to validate
            index: Index of target in list (for error messages)

        Returns:
            List of validation error messages
        """
        errors = []
        target_id = f"Target {index + 1} ({target.name})" if target.name else f"Target {index + 1}"

        # Check target name
        if not target.name or not target.name.strip():
            errors.append(f"{target_id}: Target name cannot be empty")

        # Check mode
        valid_modes = ["MAX", "MIN", "MATCH"]
        if target.mode.upper() not in valid_modes:
            errors.append(f"{target_id}: Invalid mode '{target.mode}'. Must be one of: {', '.join(valid_modes)}")

        # Check bounds for MATCH mode- TODO for Me (Kelvin) - PROPER MATCHING
        if target.mode.upper() == "MATCH":
            if target.min_value is None or target.max_value is None:
                errors.append(f"{target_id}: MATCH mode requires both min_value and max_value")
            elif target.min_value >= target.max_value:
                errors.append(f"{target_id}: min_value must be less than max_value")

        if target.min_value is not None and target.max_value is not None:
            if target.min_value >= target.max_value:
                errors.append(
                    f"{target_id}: min_value ({target.min_value}) must be less than max_value ({target.max_value})"
                )

        if target.weight is not None and target.weight <= 0:
            errors.append(f"{target_id}: Weight must be positive")

        return errors

    @staticmethod
    def get_target_names(tunex_targets: List[Target]) -> List[str]:
        """
        Get list of target names for DataFrame column creation.

        Args:
            tunex_targets: List of TuneX targets

        Returns:
            List of target names
        """
        return [target.name for target in tunex_targets]

    @staticmethod
    def create_multi_objective_note(targets: List[Target]) -> Optional[str]:
        """
        Create a note about multi-objective handling.

        Args:
            targets: List of targets

        Returns:
            Note string explaining optimization approach, None if single target
        """
        if len(targets) <= 1:
            return None

        total_weight = sum(t.weight if t.weight is not None else 1.0 for t in targets)
        target_info = []

        for target in targets:
            weight = target.weight if target.weight is not None else 1.0
            weight_pct = (weight / total_weight) * 100
            target_info.append(f"'{target.name}' ({weight_pct:.1f}%)")

        note = "Multi-objective optimization using desirability function. "
        note += f"Targets and weights: {', '.join(target_info)}. "
        note += "All targets are simultaneously optimized based on their relative weights."

        return note

    @staticmethod
    def calculate_desirability_weights(targets: List[Target]) -> Dict[str, float]:
        """
        Calculate normalized weights for desirability function.

        Args:
            targets: List of targets

        Returns:
            Dictionary mapping target names to normalized weights
        """
        if not targets:
            return {}

        # Get raw weights (default to 1.0 if not specified)
        raw_weights = {}
        for target in targets:
            weight = target.weight if target.weight is not None else 1.0
            raw_weights[target.name] = weight

        # Normalize weights to sum to 1.0
        total_weight = sum(raw_weights.values())
        if total_weight == 0:
            # All weights are zero, distribute equally
            equal_weight = 1.0 / len(targets)
            return {name: equal_weight for name in raw_weights.keys()}

        return {name: weight / total_weight for name, weight in raw_weights.items()}

    @staticmethod
    def explain_desirability_function(targets: List[Target]) -> str:
        """
        Generate an explanation of how the desirability function works.

        Args:
            targets: List of targets

        Returns:
            Detailed explanation string
        """
        if len(targets) <= 1:
            return "Single target optimization - no desirability function needed."

        explanation = "Desirability Function Explanation:\n\n"
        explanation += "The desirability function combines multiple targets into a single optimization score. "
        explanation += "Each target is transformed to a 0-1 scale where:\n"
        explanation += "- 1.0 = perfect achievement of the target\n"
        explanation += "- 0.0 = worst possible value for the target\n\n"

        explanation += "Target Details:\n"
        weights = ObjectiveConverter.calculate_desirability_weights(targets)

        for target in targets:
            weight_pct = weights[target.name] * 100
            explanation += f"• {target.name} ({target.mode}, weight: {weight_pct:.1f}%)\n"

            if target.mode.upper() == "MAX":
                explanation += "  Higher values are better\n"
            elif target.mode.upper() == "MIN":
                explanation += "  Lower values are better\n"
            elif target.mode.upper() == "MATCH":
                if target.min_value is not None and target.max_value is not None:
                    explanation += f"  Target range: {target.min_value} - {target.max_value}\n"
                else:
                    explanation += "  Target specific value\n"

        explanation += "\nFinal Score = Weighted geometric mean of individual desirabilities\n"
        explanation += "The optimizer maximizes this combined desirability score."

        return explanation
