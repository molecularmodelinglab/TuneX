from typing import Dict, Any, Optional, List, Union

from app.models.parameters.base import BaseParameter
from app.models.enums import ParameterType


class DiscreteNumericalRegular(BaseParameter):
    """Discrete numerical parameter with regular spacing (min, max, step)."""
    
    TYPE = ParameterType.DISCRETE_NUMERICAL_REGULAR
    
    def __init__(self, name: str, min_val: float, max_val: float, step: float) -> None:
        super().__init__(name)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
    
    @classmethod
    def create_default(cls, name: str) -> 'DiscreteNumericalRegular':
        """Create parameter with default values."""
        return cls(name, 0.0, 10.0, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'min': self.min_val,
                'max': self.max_val,
                'step': self.step
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        self.min_val = constraints.get('min', 0.0)
        self.max_val = constraints.get('max', 10.0)
        self.step = constraints.get('step', 1.0)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if self.min_val >= self.max_val:
            return False, "Minimum value must be less than maximum value"
        
        if self.step <= 0:
            return False, "Step size must be positive"
        
        if self.step > (self.max_val - self.min_val):
            return False, "Step size cannot be larger than the range"
        
        return True, None


class DiscreteNumericalIrregular(BaseParameter):
    """Discrete numerical parameter with irregular spacing (list of values)."""
    
    TYPE = ParameterType.DISCRETE_NUMERICAL_IRREGULAR
    
    def __init__(self, name: str, values: List[Union[int, float]]) -> None:
        super().__init__(name)
        self.values = list(values)  # Create copy to avoid mutations
    
    @classmethod
    def create_default(cls, name: str) -> 'DiscreteNumericalIrregular':
        """Create parameter with default values."""
        return cls(name, [1, 2, 5])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'values': self.values
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        self.values = constraints.get('values', [])

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if not self.values:
            return False, "At least one value is required"

        for i, value in enumerate(self.values):
            if not isinstance(value, (int, float)):
                return False, f"Value at index {i} ({value}) is not a number"

        if len(self.values) != len(set(self.values)):
            return False, "Duplicate values are not allowed"
        
        return True, None


class ContinuousNumerical(BaseParameter):
    """Continuous numerical parameter with range (min, max)."""
    
    TYPE = ParameterType.CONTINUOUS_NUMERICAL
    
    def __init__(self, name: str, min_val: float, max_val: float) -> None:
        super().__init__(name)
        self.min_val = min_val
        self.max_val = max_val
    
    @classmethod
    def create_default(cls, name: str) -> 'ContinuousNumerical':
        """Create parameter with default values."""
        return cls(name, 0.0, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'min': self.min_val,
                'max': self.max_val
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        self.min_val = constraints.get('min', 0.0)
        self.max_val = constraints.get('max', 1.0)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if self.min_val >= self.max_val:
            return False, "Minimum value must be less than maximum value"
        
        return True, None


class Categorical(BaseParameter):
    """Categorical parameter with string values."""
    
    TYPE = ParameterType.CATEGORICAL
    
    def __init__(self, name: str, values: List[str]) -> None:
        super().__init__(name)
        self.values = [str(v).strip() for v in values]  # Ensure strings and strip whitespace
    
    @classmethod
    def create_default(cls, name: str) -> 'Categorical':
        """Create parameter with default values."""
        return cls(name, ["A", "B", "C"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'values': self.values
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        values = constraints.get('values', [])
        self.values = [str(v).strip() for v in values]

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if not self.values:
            return False, "At least one category is required"

        for i, value in enumerate(self.values):
            if not value:
                return False, f"Category at index {i} cannot be empty"
        
        # Check for duplicates
        if len(self.values) != len(set(self.values)):
            return False, "Duplicate categories are not allowed"
        
        return True, None


class Fixed(BaseParameter):
    """Fixed parameter with a single value."""
    
    TYPE = ParameterType.FIXED
    
    def __init__(self, name: str, value: Union[int, float, str]) -> None:
        super().__init__(name)
        self.value = value
    
    @classmethod
    def create_default(cls, name: str) -> 'Fixed':
        """Create parameter with default values."""
        return cls(name, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'value': self.value
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        self.value = constraints.get('value', 1.0)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if self.value is None:
            return False, "Fixed value cannot be None"
        
        return True, None


class Substance(BaseParameter):
    """Substance parameter with SMILES strings."""
    
    TYPE = ParameterType.SUBSTANCE
    
    def __init__(self, name: str, smiles: List[str]) -> None:
        super().__init__(name)
        self.smiles = [str(s).strip() for s in smiles]  # Ensure strings and strip whitespace
    
    @classmethod
    def create_default(cls, name: str) -> 'Substance':
        """Create parameter with default values."""
        return cls(name, ["CCO", "CCCCO"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.parameter_type.value,
            'constraints': {
                'values': self.smiles
            }
        }

    def load_constraints(self, constraints: Dict[str, Any]) -> None:
        """Load constraints from dictionary."""
        values = constraints.get('values', [])
        self.smiles = [str(s).strip() for s in values]

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate parameter configuration."""
        if not self.smiles:
            return False, "At least one SMILES string is required"

        for i, smiles in enumerate(self.smiles):
            if not smiles:
                return False, f"SMILES at index {i} cannot be empty"

        if len(self.smiles) != len(set(self.smiles)):
            return False, "Duplicate SMILES strings are not allowed"
        
        # Basic SMILES validation (just check for obviously invalid characters)
        invalid_chars = set(' \t\n\r')
        for i, smiles in enumerate(self.smiles):
            if any(char in invalid_chars for char in smiles):
                return False, f"SMILES at index {i} contains invalid whitespace characters"
        
        return True, None