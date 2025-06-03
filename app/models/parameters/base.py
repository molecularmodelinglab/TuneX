from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type

from app.models.enums import ParameterType


class BaseParameter(ABC):
    """Abstract base class for all parameter types."""

    _registry: Dict[ParameterType, Type['BaseParameter']] = {}

    # Each subclass must define its parameter type
    TYPE: ParameterType = None

    def __init_subclass__(cls, **kwargs) -> None:
        """Auto-register parameter classes when they are defined."""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'TYPE'):
            raise AttributeError(f"{cls.__name__} must define TYPE class attribute")
        cls._registry[cls.TYPE] = cls
    
    def __init__(self, name: str) -> None:
        """
        Initialize base parameter.
        
        Args:
            name: Parameter name (must be unique within a campaign)
        """
        if not name or not name.strip():
            raise ValueError("Parameter name cannot be empty")
        self.name = name.strip()

    @classmethod
    def create_from_type(cls, param_type: ParameterType, name: str) -> 'BaseParameter':
        """Create parameter instance from type enum."""
        if param_type not in cls._registry:
            raise ValueError(f"No parameter class registered for type: {param_type}")
        parameter_class = cls._registry[param_type]
        return parameter_class.create_default(name)

    @classmethod
    def from_dict(cls, param_dict: Dict[str, Any]) -> 'BaseParameter':
        """
        Create parameter instance from dictionary representation.
        
        This method handles the deserialization logic, so UI code doesn't
        need to know about internal parameter formats.
        
        Args:
            param_dict: Dictionary containing parameter data (from to_dict())
            
        Returns:
            BaseParameter: The appropriate parameter instance
            
        Raises:
            ValueError: If parameter type is unknown or data is invalid
            
        Example:
            >>> data = {
            ...     'name': 'temperature',
            ...     'type': 'discrete_numerical_regular',
            ...     'constraints': {'min': 20, 'max': 100, 'step': 5}
            ... }
            >>> param = BaseParameter.from_dict(data)
            >>> isinstance(param, DiscreteNumericalRegular)
            True
        """
        param_type_str = param_dict.get('type', '')
        if not param_type_str:
            raise ValueError("Parameter dictionary must contain 'type' field")

        param_type = None
        for pt in ParameterType:
            if pt.value == param_type_str:
                param_type = pt
                break
        
        if param_type is None:
            raise ValueError(f"Unknown parameter type: {param_type_str}")
        
        # Get parameter class from registry
        if param_type not in cls._registry:
            raise ValueError(f"No parameter class registered for type: {param_type}")
        
        parameter_class = cls._registry[param_type]
        
        # Extract parameter name
        param_name = param_dict.get('name', 'Unknown')
        if not param_name:
            raise ValueError("Parameter dictionary must contain non-empty 'name' field")
        
        # Create parameter instance with default values
        parameter = parameter_class.create_default(param_name)
        
        # Load constraints using the parameter's own method
        constraints = param_dict.get('constraints', {})
        parameter.load_constraints(constraints)
        
        return parameter

    @classmethod
    @abstractmethod
    def create_default(cls, name: str) -> 'BaseParameter':
        """Create parameter with default values."""
        pass

    @property
    def parameter_type(self) -> ParameterType:
        """Get the parameter type enum value."""
        if self.TYPE is None:
            raise NotImplementedError(f"{self.__class__.__name__} must define TYPE class attribute")
        return self.TYPE
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert parameter to dictionary for serialization.
        
        Returns:
            Dictionary representation including type, name, and constraints
        """
        pass

    @abstractmethod
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate parameter configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
            error_message is None if valid
        """
        pass

    def __str__(self) -> str:
        """String representation of parameter."""
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', type={self.parameter_type.value})"