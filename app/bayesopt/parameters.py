"""
Parameter conversion utilities for BayBE integration.

This module handles the conversion between TuneX parameter types and BayBE parameter types.
"""

from typing import Any, Dict, List, Union

from baybe.parameters import (
    CategoricalParameter,
    NumericalContinuousParameter,
    NumericalDiscreteParameter,
    SubstanceParameter,
)
from baybe.searchspace import SearchSpace

from app.models.enums import ParameterType
from app.models.parameters.base import BaseParameter
from app.models.parameters.types import (
    Categorical,
    ContinuousNumerical,
    DiscreteNumericalIrregular,
    DiscreteNumericalRegular,
    Substance,
)


class ParameterConverter:
    """Converts TuneX parameters to BayBE parameters."""

    @staticmethod
    def convert_parameter(
        tunex_param: Any,
    ) -> Union[
        NumericalContinuousParameter,
        NumericalDiscreteParameter,
        CategoricalParameter,
        SubstanceParameter,
    ]:
        """
        Convert a TuneX parameter to a BayBE parameter.

        Args:
            tunex_param: TuneX parameter to convert

        Returns:
            Corresponding BayBE parameter

        Raises:
            ValueError: If parameter type is not supported
        """
        param_type = tunex_param.TYPE

        if param_type == ParameterType.CONTINUOUS_NUMERICAL:
            return ParameterConverter._convert_continuous_numerical(tunex_param)
        elif param_type in [ParameterType.DISCRETE_NUMERICAL_REGULAR, ParameterType.DISCRETE_NUMERICAL_IRREGULAR]:
            return ParameterConverter._convert_discrete_numerical(tunex_param)
        elif param_type == ParameterType.CATEGORICAL:
            return ParameterConverter._convert_categorical(tunex_param)
        elif param_type == ParameterType.SUBSTANCE:
            return ParameterConverter._convert_substance(tunex_param)
        elif param_type == ParameterType.FIXED:
            # Fixed parameters are not used in optimization
            raise ValueError(f"Fixed parameters should not be included in BayBE optimization: {tunex_param.name}")
        else:
            raise ValueError(f"Unsupported parameter type: {param_type}")

    @staticmethod
    def _convert_continuous_numerical(tunex_param: ContinuousNumerical) -> NumericalContinuousParameter:
        """Convert continuous numerical parameter."""
        return NumericalContinuousParameter(
            name=tunex_param.name,
            bounds=(tunex_param.min_val, tunex_param.max_val),
        )

    @staticmethod
    def _convert_discrete_numerical(
        tunex_param: Union[DiscreteNumericalRegular, DiscreteNumericalIrregular],
    ) -> NumericalDiscreteParameter:
        """Convert discrete numerical parameter."""
        if hasattr(tunex_param, "values"):
            # Irregular discrete parameter with explicit values
            values = tunex_param.values
        else:
            # Regular discrete parameter with min, max, step
            import numpy as np

            values = np.arange(tunex_param.min_val, tunex_param.max_val + tunex_param.step, tunex_param.step).tolist()

        return NumericalDiscreteParameter(
            name=tunex_param.name,
            values=values,
        )

    @staticmethod
    def _convert_categorical(tunex_param: Categorical) -> CategoricalParameter:
        """Convert categorical parameter."""
        return CategoricalParameter(
            name=tunex_param.name,
            values=tunex_param.values,
        )

    @staticmethod
    def _convert_substance(tunex_param: Substance) -> SubstanceParameter:
        """Convert substance parameter (SMILES)."""
        return SubstanceParameter(
            name=tunex_param.name, data={f"mol_{i}": smile for i, smile in enumerate(tunex_param.smiles)}
        )

    @staticmethod
    def create_search_space(tunex_parameters: List[BaseParameter]) -> SearchSpace:
        """
        Create a BayBE SearchSpace from TuneX parameters.

        Args:
            tunex_parameters: List of TuneX parameters

        Returns:
            BayBE SearchSpace object

        Raises:
            ValueError: If no valid parameters for optimization
        """
        baybe_parameters = []

        for tunex_param in tunex_parameters:
            # Skip fixed parameters as they don't participate in optimization
            if tunex_param.TYPE == ParameterType.FIXED:
                continue

            try:
                baybe_param = ParameterConverter.convert_parameter(tunex_param)
                baybe_parameters.append(baybe_param)
            except ValueError as e:
                print(f"Warning: Skipping parameter {tunex_param.name}: {e}")
                continue

        if not baybe_parameters:
            raise ValueError("No valid parameters found for optimization")

        return SearchSpace.from_product(parameters=baybe_parameters)

    @staticmethod
    def convert_experiments_to_dataframe(experiments: List[Dict[str, Any]], target_names: List[str]):
        """
        Convert experiment data to pandas DataFrame for BayBE.

        Args:
            experiments: List of experiment dictionaries
            target_names: List of target column names

        Returns:
            pandas.DataFrame: Formatted for BayBE
        """
        import pandas as pd

        if not experiments:
            return pd.DataFrame()

        # Create DataFrame from experiments
        df = pd.DataFrame(experiments)

        # Ensure all target columns exist (fill with NaN if missing)
        for target_name in target_names:
            if target_name not in df.columns:
                df[target_name] = None

        return df

    @staticmethod
    def validate_parameter_constraints(tunex_param: BaseParameter) -> bool:
        """
        Validate that a TuneX parameter has valid constraints for BayBE conversion.

        Args:
            tunex_param: TuneX parameter to validate

        Returns:
            bool: True if valid, False otherwise
        """
        param_type = tunex_param.TYPE

        if param_type == ParameterType.CONTINUOUS_NUMERICAL:
            if hasattr(tunex_param, "min_val") and hasattr(tunex_param, "max_val"):
                return tunex_param.min_val is not None and tunex_param.max_val is not None
            else:
                return False

        elif param_type in [ParameterType.DISCRETE_NUMERICAL_REGULAR, ParameterType.DISCRETE_NUMERICAL_IRREGULAR]:
            if hasattr(tunex_param, "values"):
                return len(tunex_param.values) > 0
            else:
                return (
                    hasattr(tunex_param, "min_val") and hasattr(tunex_param, "max_val") and hasattr(tunex_param, "step")
                )

        elif param_type == ParameterType.CATEGORICAL:
            return hasattr(tunex_param, "values") and len(tunex_param.values) > 0

        elif param_type == ParameterType.SUBSTANCE:
            return hasattr(tunex_param, "smiles") and len(tunex_param.smiles) > 0

        elif param_type == ParameterType.FIXED:
            return True  # Fixed parameters are always valid but won't be used in optimization

        return False
