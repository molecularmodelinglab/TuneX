"""
Parameter conversion utilities for BayBE integration.

This module handles the conversion between BASIL parameter types and BayBE parameter types.
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
    """Converts BASIL parameters to BayBE parameters."""

    @staticmethod
    def convert_parameter(
        basil_param: Any,
    ) -> Union[
        NumericalContinuousParameter,
        NumericalDiscreteParameter,
        CategoricalParameter,
        SubstanceParameter,
    ]:
        """
        Convert a BASIL parameter to a BayBE parameter.

        Args:
            basil_param: BASIL parameter to convert

        Returns:
            Corresponding BayBE parameter

        Raises:
            ValueError: If parameter type is not supported
        """
        param_type = basil_param.TYPE

        if param_type == ParameterType.CONTINUOUS_NUMERICAL:
            return ParameterConverter._convert_continuous_numerical(basil_param)
        elif param_type in [ParameterType.DISCRETE_NUMERICAL_REGULAR, ParameterType.DISCRETE_NUMERICAL_IRREGULAR]:
            return ParameterConverter._convert_discrete_numerical(basil_param)
        elif param_type == ParameterType.CATEGORICAL:
            return ParameterConverter._convert_categorical(basil_param)
        elif param_type == ParameterType.SUBSTANCE:
            return ParameterConverter._convert_substance(basil_param)
        elif param_type == ParameterType.FIXED:
            # Fixed parameters are not used in optimization
            raise ValueError(f"Fixed parameters should not be included in BayBE optimization: {basil_param.name}")
        else:
            raise ValueError(f"Unsupported parameter type: {param_type}")

    @staticmethod
    def _convert_continuous_numerical(basil_param: ContinuousNumerical) -> NumericalContinuousParameter:
        """Convert continuous numerical parameter."""
        return NumericalContinuousParameter(
            name=basil_param.name,
            bounds=(basil_param.min_val, basil_param.max_val),
        )

    @staticmethod
    def _convert_discrete_numerical(
        basil_param: Union[DiscreteNumericalRegular, DiscreteNumericalIrregular],
    ) -> NumericalDiscreteParameter:
        """Convert discrete numerical parameter."""
        if hasattr(basil_param, "values"):
            # Irregular discrete parameter with explicit values
            values = basil_param.values
        else:
            # Regular discrete parameter with min, max, step
            import numpy as np

            values = np.arange(basil_param.min_val, basil_param.max_val + basil_param.step, basil_param.step).tolist()

        return NumericalDiscreteParameter(
            name=basil_param.name,
            values=values,
        )

    @staticmethod
    def _convert_categorical(basil_param: Categorical) -> CategoricalParameter:
        """Convert categorical parameter."""
        return CategoricalParameter(
            name=basil_param.name,
            values=basil_param.values,
        )

    @staticmethod
    def _convert_substance(basil_param: Substance) -> SubstanceParameter:
        """Convert substance parameter (SMILES)."""
        return SubstanceParameter(
            name=basil_param.name, data={f"mol_{i}": smile for i, smile in enumerate(basil_param.smiles)}
        )

    @staticmethod
    def create_search_space(basil_parameters: List[BaseParameter]) -> SearchSpace:
        """
        Create a BayBE SearchSpace from BASIL parameters.

        Args:
            basil_parameters: List of BASIL parameters

        Returns:
            BayBE SearchSpace object

        Raises:
            ValueError: If no valid parameters for optimization
        """
        baybe_parameters = []

        for basil_param in basil_parameters:
            # Skip fixed parameters as they don't participate in optimization
            if basil_param.TYPE == ParameterType.FIXED:
                continue

            try:
                baybe_param = ParameterConverter.convert_parameter(basil_param)
                baybe_parameters.append(baybe_param)
            except ValueError as e:
                print(f"Warning: Skipping parameter {basil_param.name}: {e}")
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
    def validate_parameter_constraints(basil_param: BaseParameter) -> bool:
        """
        Validate that a BASIL parameter has valid constraints for BayBE conversion.

        Args:
            basil_param: BASIL parameter to validate

        Returns:
            bool: True if valid, False otherwise
        """
        param_type = basil_param.TYPE

        if param_type == ParameterType.CONTINUOUS_NUMERICAL:
            if hasattr(basil_param, "min_val") and hasattr(basil_param, "max_val"):
                return basil_param.min_val is not None and basil_param.max_val is not None
            else:
                return False

        elif param_type in [ParameterType.DISCRETE_NUMERICAL_REGULAR, ParameterType.DISCRETE_NUMERICAL_IRREGULAR]:
            if hasattr(basil_param, "values"):
                return len(basil_param.values) > 0
            else:
                return (
                    hasattr(basil_param, "min_val") and hasattr(basil_param, "max_val") and hasattr(basil_param, "step")
                )

        elif param_type == ParameterType.CATEGORICAL:
            return hasattr(basil_param, "values") and len(basil_param.values) > 0

        elif param_type == ParameterType.SUBSTANCE:
            return hasattr(basil_param, "smiles") and len(basil_param.smiles) > 0

        elif param_type == ParameterType.FIXED:
            return True  # Fixed parameters are always valid but won't be used in optimization

        return False
