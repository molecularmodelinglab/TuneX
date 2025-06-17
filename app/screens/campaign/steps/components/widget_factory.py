"""
Factory function for creating constraint widgets based on parameter types.

This module provides a simple factory function that creates the appropriate
constraint widget for different parameter types. It centralizes the widget
creation logic and makes it easy to add support for new parameter types.
"""

from typing import Optional

from app.models.parameters.base import BaseParameter
from app.models.parameters.types import (
    DiscreteNumericalRegular, DiscreteNumericalIrregular,
    ContinuousNumerical, Categorical, Fixed, Substance
)
from .constraint_widgets import (
    BaseConstraintWidget, 
    MinMaxStepWidget, 
    MinMaxWidget, 
    ValuesListWidget, 
    FixedValueWidget, 
    SmilesWidget
)


def create_constraint_widget(parameter: BaseParameter) -> Optional[BaseConstraintWidget]:
    """
    Create the appropriate constraint widget for a given parameter.
    
    This function determines which widget class to instantiate based on the
    parameter type. It handles all supported parameter types and returns None
    for unsupported types.
    
    Args:
        parameter: The parameter object for which to create a widget
        
    Returns:
        BaseConstraintWidget: The appropriate widget instance, or None if
                            the parameter type is not supported
        
    Example:
        >>> param = DiscreteNumericalRegular("temperature", 20, 100, 5)
        >>> widget = create_constraint_widget(param)
        >>> isinstance(widget, MinMaxStepWidget)
        True
    """
    return _create_widget_by_type(parameter)


def _create_widget_by_type(parameter: BaseParameter) -> Optional[BaseConstraintWidget]:
    """
    Private method to create widgets based on parameter type.
    
    Args:
        parameter: The parameter object for which to create a widget
        
    Returns:
        BaseConstraintWidget: The appropriate widget instance, or None if unsupported
    """
    if isinstance(parameter, DiscreteNumericalRegular):
        return MinMaxStepWidget(parameter)
    elif isinstance(parameter, ContinuousNumerical):
        return MinMaxWidget(parameter)
    elif isinstance(parameter, DiscreteNumericalIrregular):
        return ValuesListWidget(parameter, is_numerical=True)
    elif isinstance(parameter, Categorical):
        return ValuesListWidget(parameter, is_numerical=False)
    elif isinstance(parameter, Fixed):
        return FixedValueWidget(parameter)
    elif isinstance(parameter, Substance):
        return SmilesWidget(parameter)
    else:
        print(f"Warning: Unsupported parameter type '{type(parameter).__name__}' "
              f"for parameter '{parameter.name}'. No widget created.")
        return None