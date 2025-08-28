"""
Specialized constraint widgets for parameter configuration.

This module contains Qt widgets that handle the display and synchronization
of parameter constraints. Each widget knows how to:
1. Display the appropriate UI controls for its parameter type
2. Populate itself with data from a parameter object
3. Sync user input back to the parameter object
4. Validate the current state

The widgets follow a common interface defined by BaseConstraintWidget,
making them interchangeable and easy to extend.
"""

from abc import ABC, abstractmethod
from typing import Optional

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QWidget,
)

from app.models.parameters.base import BaseParameter


class BaseConstraintWidget(ABC):
    """
    Abstract base class for all constraint widgets.

    Defines the common interface that all constraint widgets must implement.
    This ensures consistent behavior across different parameter types and
    makes it easy to add new parameter types in the future.

    Each concrete widget is responsible for:
    - Creating appropriate Qt controls for its parameter type
    - Displaying current parameter values in the UI
    - Collecting user input and updating the parameter object
    - Validating user input
    """

    # UI text constants
    MIN_LABEL = "Min:"
    MAX_LABEL = "Max:"
    STEP_LABEL = "Step:"

    NUMERICAL_VALUES_PLACEHOLDER = "Enter numerical values, comma separated (e.g., 1.5, 2.0, 3.5)"
    CATEGORICAL_VALUES_PLACEHOLDER = "Enter categories, comma separated (e.g., Low, Medium, High)"
    FIXED_VALUE_PLACEHOLDER = "Enter fixed value (number or text)"
    SMILES_PLACEHOLDER = "Enter SMILES strings, comma separated\nExample: CCO, CCN, CCC"

    INVALID_NUMERICAL_VALUES_WARNING = "Warning: Invalid numerical values: {}, error: {}"

    # Spinbox constants
    SPINBOX_MIN_RANGE = -999999
    SPINBOX_MAX_RANGE = 999999
    SPINBOX_STEP_MIN_RANGE = 0.001
    DISCRETE_SPINBOX_DECIMALS = 3
    CONTINUOUS_SPINBOX_DECIMALS = 6

    # Default values
    DEFAULT_MIN_VALUE = 0.0
    DEFAULT_MAX_VALUE_MINMAX_STEP = 10.0
    DEFAULT_MAX_VALUE_MINMAX = 1.0
    DEFAULT_STEP_VALUE = 1.0
    DEFAULT_EMPTY_STRING = ""

    # Layout constants
    MINMAX_STEP_LAYOUT_MARGINS = (12, 8, 12, 8)
    MINMAX_STEP_LAYOUT_SPACING = 12
    MINMAX_LAYOUT_MARGINS = (8, 4, 8, 4)
    MINMAX_LAYOUT_SPACING = 8

    # Widget sizing constants
    TEXT_EDIT_MAX_HEIGHT = 80

    # Object names for styling
    OBJECT_NAME_CONSTRAINT_SPINBOX = "ConstraintSpinBox"
    OBJECT_NAME_CONSTRAINT_TEXTEDIT = "ConstraintTextEdit"
    OBJECT_NAME_CONSTRAINT_LINEEDIT = "ConstraintLineEdit"

    def __init__(self, parameter: BaseParameter) -> None:
        """
        Initialize the constraint widget for a specific parameter.

        Args:
            parameter: The parameter object this widget will manage

        Raises:
            TypeError: If parameter is not compatible with this widget
        """
        # Check compatibility before proceeding
        if not self.is_compatible_parameter(parameter):
            raise TypeError(
                f"Parameter '{parameter.name}' of type {type(parameter).__name__} "
                f"is not compatible with {self.__class__.__name__}"
            )

        self.parameter: BaseParameter = parameter
        self.widgetContainer: QWidget = self._create_widget()
        self._load_from_parameter()

    @abstractmethod
    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """
        Check if the given parameter is compatible with this widget.

        Each widget implementation must define what makes a parameter
        compatible (required attributes, types, etc.).

        Args:
            parameter: The parameter to check for compatibility

        Returns:
            bool: True if parameter is compatible, False otherwise
        """
        pass

    @abstractmethod
    def _create_widget(self) -> QWidget:
        """
        Create and return the Qt widget for displaying constraints.

        This method should create all necessary UI controls (spinboxes,
        text fields, etc.) and arrange them in a layout.

        Returns:
            QWidget: The widget containing all UI controls
        """
        pass

    @abstractmethod
    def _load_from_parameter(self) -> None:
        """
        Load data from the parameter object into the widget's controls.

        This method should read the current parameter values and display
        them in the appropriate UI controls. Called once during initialization.
        Direction: parameter → widget
        Note: In the future might throw exception if parameter is incompatible
        """
        pass

    @abstractmethod
    def _save_to_parameter(self) -> None:
        """
        Save user input from UI controls back to the parameter object.

        This method should collect all values from the widget's controls
        and store them back into the parameter object. Called before
        validation or saving.
        Direction: widget → parameter
        """
        pass

    def get_widget(self) -> QWidget:
        """
        Get the Qt widget for embedding in the UI.

        Returns:
            QWidget: The widget that can be added to layouts or tables
        """
        return self.widgetContainer

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the current widget state and parameter values.

        First syncs the UI data to the parameter, then validates the parameter.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
                - is_valid: True if validation passed, False otherwise
                - error_message: Description of validation error, None if valid
        """
        self._save_to_parameter()
        return self.parameter.validate()


class MinMaxStepWidget(BaseConstraintWidget):
    """
    Widget for configuring min/max/step constraints.

    Used for discrete numerical parameters with regular intervals.
    Displays three spinboxes for minimum value, maximum value, and step size.

    Example: A temperature parameter that can range from 20°C to 100°C
    in steps of 5°C would use this widget.
    """

    def __init__(self, parameter: BaseParameter) -> None:
        """Initialize widget with a parameter that has min, max, and step."""
        super().__init__(parameter)

    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """Check if parameter has min_val, max_val, and step attributes."""
        return all(hasattr(parameter, attr) for attr in ["min_val", "max_val", "step"])

    def _create_widget(self) -> QWidget:
        """Create spinboxes for min, max, and step values."""
        container_widget = QWidget()
        main_layout = QHBoxLayout(container_widget)
        main_layout.setContentsMargins(*self.MINMAX_STEP_LAYOUT_MARGINS)
        main_layout.setSpacing(self.MINMAX_STEP_LAYOUT_SPACING)

        # Create min value controls
        min_label = QLabel(self.MIN_LABEL)
        self.minSpinBox = QDoubleSpinBox()
        self.minSpinBox.setObjectName(self.OBJECT_NAME_CONSTRAINT_SPINBOX)
        self.minSpinBox.setRange(self.SPINBOX_MIN_RANGE, self.SPINBOX_MAX_RANGE)
        self.minSpinBox.setDecimals(self.DISCRETE_SPINBOX_DECIMALS)

        # Create max value controls
        max_label = QLabel(self.MAX_LABEL)
        self.maxSpinBox = QDoubleSpinBox()
        self.maxSpinBox.setObjectName(self.OBJECT_NAME_CONSTRAINT_SPINBOX)
        self.maxSpinBox.setRange(self.SPINBOX_MIN_RANGE, self.SPINBOX_MAX_RANGE)
        self.maxSpinBox.setDecimals(self.DISCRETE_SPINBOX_DECIMALS)

        # Create step value controls
        step_label = QLabel(self.STEP_LABEL)
        self.stepSpinBox = QDoubleSpinBox()
        self.stepSpinBox.setObjectName(self.OBJECT_NAME_CONSTRAINT_SPINBOX)
        self.stepSpinBox.setRange(self.SPINBOX_STEP_MIN_RANGE, self.SPINBOX_MAX_RANGE)
        self.stepSpinBox.setDecimals(self.DISCRETE_SPINBOX_DECIMALS)

        # Add widgets to layout
        main_layout.addWidget(min_label)
        main_layout.addWidget(self.minSpinBox)
        main_layout.addWidget(max_label)
        main_layout.addWidget(self.maxSpinBox)
        main_layout.addWidget(step_label)
        main_layout.addWidget(self.stepSpinBox)

        return container_widget

    def _load_from_parameter(self) -> None:
        """Load current parameter values into the spinboxes."""
        self.minSpinBox.setValue(getattr(self.parameter, "min_val", self.DEFAULT_MIN_VALUE))
        self.maxSpinBox.setValue(getattr(self.parameter, "max_val", self.DEFAULT_MAX_VALUE_MINMAX_STEP))
        self.stepSpinBox.setValue(getattr(self.parameter, "step", self.DEFAULT_STEP_VALUE))

    def _save_to_parameter(self) -> None:
        """Save spinbox values back to the parameter object."""
        if hasattr(self.parameter, "min_val"):
            self.parameter.min_val = self.minSpinBox.value()
        if hasattr(self.parameter, "max_val"):
            self.parameter.max_val = self.maxSpinBox.value()
        if hasattr(self.parameter, "step"):
            self.parameter.step = self.stepSpinBox.value()


class MinMaxWidget(BaseConstraintWidget):
    """
    Widget for configuring min/max constraints only.

    Used for continuous numerical parameters where any value within
    a range is valid (no discrete steps).

    Example: A pressure parameter that can be any value between
    1.0 and 10.0 atmospheres would use this widget.
    """

    def __init__(self, parameter: BaseParameter) -> None:
        """Initialize widget with a parameter that has min and max."""
        super().__init__(parameter)

    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """Check if parameter has min_val and max_val attributes."""
        return all(hasattr(parameter, attr) for attr in ["min_val", "max_val"])

    def _create_widget(self) -> QWidget:
        """Create spinboxes for min and max values."""
        container_widget = QWidget()
        main_layout = QHBoxLayout(container_widget)
        main_layout.setContentsMargins(*self.MINMAX_LAYOUT_MARGINS)
        main_layout.setSpacing(self.MINMAX_LAYOUT_SPACING)

        # Create minimum value controls
        min_label = QLabel(self.MIN_LABEL)
        self.minSpinBox = QDoubleSpinBox()
        self.minSpinBox.setObjectName(self.OBJECT_NAME_CONSTRAINT_SPINBOX)
        self.minSpinBox.setRange(self.SPINBOX_MIN_RANGE, self.SPINBOX_MAX_RANGE)
        self.minSpinBox.setDecimals(self.CONTINUOUS_SPINBOX_DECIMALS)

        # Create maximum value controls
        max_label = QLabel(self.MAX_LABEL)
        self.maxSpinBox = QDoubleSpinBox()
        self.maxSpinBox.setObjectName(self.OBJECT_NAME_CONSTRAINT_SPINBOX)
        self.maxSpinBox.setRange(self.SPINBOX_MIN_RANGE, self.SPINBOX_MAX_RANGE)
        self.maxSpinBox.setDecimals(self.CONTINUOUS_SPINBOX_DECIMALS)

        # Add widgets to layout
        main_layout.addWidget(min_label)
        main_layout.addWidget(self.minSpinBox)
        main_layout.addWidget(max_label)
        main_layout.addWidget(self.maxSpinBox)

        return container_widget

    def _load_from_parameter(self) -> None:
        """Load current parameter values into the spinboxes."""
        self.minSpinBox.setValue(getattr(self.parameter, "min_val", self.DEFAULT_MIN_VALUE))
        self.maxSpinBox.setValue(getattr(self.parameter, "max_val", self.DEFAULT_MAX_VALUE_MINMAX))

    def _save_to_parameter(self) -> None:
        """Save spinbox values back to the parameter object."""
        if hasattr(self.parameter, "min_val"):
            self.parameter.min_val = self.minSpinBox.value()
        if hasattr(self.parameter, "max_val"):
            self.parameter.max_val = self.maxSpinBox.value()


class ValuesListWidget(BaseConstraintWidget):
    """
    Widget for configuring a list of discrete values.

    Used for parameters that can only take specific values, either
    numerical (like [1.5, 2.7, 4.2]) or categorical (like ['A', 'B', 'C']).

    The widget displays a text area where users can enter comma-separated
    values. The is_numerical flag determines how the values are parsed.
    """

    def __init__(self, parameter: BaseParameter, is_numerical: bool = True) -> None:
        """
        Initialize the values list widget.

        Args:
            parameter: The parameter object to manage (must have 'values' attribute)
            is_numerical: If True, parse values as numbers; if False, treat as strings
        """
        self.is_numerical: bool = is_numerical
        super().__init__(parameter)

    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """Check if parameter has values attribute."""
        return hasattr(parameter, "values")

    def _create_widget(self) -> QWidget:
        """Create a text area for entering comma-separated values."""
        self.valuesTextEdit = QTextEdit()
        self.valuesTextEdit.setObjectName(self.OBJECT_NAME_CONSTRAINT_TEXTEDIT)
        self.valuesTextEdit.setMaximumHeight(self.TEXT_EDIT_MAX_HEIGHT)

        # Set appropriate placeholder text based on value type
        if self.is_numerical:
            placeholder = self.NUMERICAL_VALUES_PLACEHOLDER
        else:
            placeholder = self.CATEGORICAL_VALUES_PLACEHOLDER

        self.valuesTextEdit.setPlaceholderText(placeholder)
        return self.valuesTextEdit

    def _load_from_parameter(self) -> None:
        """Load current parameter values into the text area."""
        values = getattr(self.parameter, "values", [])
        values_text = ", ".join(str(v) for v in values)
        self.valuesTextEdit.setPlainText(values_text)

    def _save_to_parameter(self) -> None:
        """Parse text area content and save values to the parameter."""
        text = self.valuesTextEdit.toPlainText().strip()

        if not hasattr(self.parameter, "values"):
            return

        if not text:
            self.parameter.values = []
            return

        # Split by commas and clean up whitespace
        raw_values = [v.strip() for v in text.split(",") if v.strip()]

        if self.is_numerical:
            try:
                # Convert to float for numerical parameters
                self.parameter.values = [float(v) for v in raw_values]
            except ValueError as e:
                # Log error but don't crash - validation will catch this
                print(self.INVALID_NUMERICAL_VALUES_WARNING.format(raw_values, e))
                self.parameter.values = []
        else:
            # Keep as strings for categorical parameters
            self.parameter.values = raw_values


class FixedValueWidget(BaseConstraintWidget):
    """
    Widget for configuring a single fixed value.

    Used for parameters that don't vary during the experiment but
    need to be documented. The value can be numerical or textual.

    Example: A fixed catalyst concentration of 0.1M or a fixed
    solvent name like "ethanol".
    """

    def __init__(self, parameter: BaseParameter) -> None:
        """Initialize widget with a parameter that has a fixed value."""
        super().__init__(parameter)

    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """Check if parameter has value attribute."""
        return hasattr(parameter, "value")

    def _create_widget(self) -> QWidget:
        """Create a single line edit for the fixed value."""
        self.fixedValueLineEdit = QLineEdit()
        self.fixedValueLineEdit.setObjectName(self.OBJECT_NAME_CONSTRAINT_LINEEDIT)
        self.fixedValueLineEdit.setPlaceholderText(self.FIXED_VALUE_PLACEHOLDER)
        return self.fixedValueLineEdit

    def _load_from_parameter(self) -> None:
        """Load current parameter value into the line edit."""
        value = getattr(self.parameter, "value", self.DEFAULT_EMPTY_STRING)
        self.fixedValueLineEdit.setText(str(value))

    def _save_to_parameter(self) -> None:
        """Parse line edit content and save to the parameter."""
        if not hasattr(self.parameter, "value"):
            return
        text = self.fixedValueLineEdit.text().strip()

        if not text:
            self.parameter.value = self.DEFAULT_EMPTY_STRING
            return

        try:
            self.parameter.value = float(text)
        except ValueError:
            self.parameter.value = text


class SmilesWidget(BaseConstraintWidget):
    """
    Widget for configuring SMILES strings (chemical structures).

    SMILES (Simplified Molecular Input Line Entry System) strings are
    a way to represent chemical structures as text. This widget allows
    users to enter multiple SMILES strings for different compounds.

    Example: ['CCO', 'CCC', 'CCCC'] for ethanol, propane, and butane.
    """

    def __init__(self, parameter: BaseParameter) -> None:
        """Initialize widget with a parameter that has SMILES strings."""
        super().__init__(parameter)

    def is_compatible_parameter(self, parameter: BaseParameter) -> bool:
        """Check if parameter has smiles attribute."""
        return hasattr(parameter, "smiles")

    def _create_widget(self) -> QWidget:
        """Create a text area for entering SMILES strings."""
        self.smilesTextEdit = QTextEdit()
        self.smilesTextEdit.setObjectName(self.OBJECT_NAME_CONSTRAINT_TEXTEDIT)
        self.smilesTextEdit.setPlaceholderText(self.SMILES_PLACEHOLDER)
        return self.smilesTextEdit

    def _load_from_parameter(self) -> None:
        """Load current SMILES strings into the text area."""
        smiles = getattr(self.parameter, "smiles", [])
        smiles_text = ", ".join(smiles)
        self.smilesTextEdit.setPlainText(smiles_text)

    def _save_to_parameter(self) -> None:
        """Parse text area content and save SMILES strings to the parameter."""
        if not hasattr(self.parameter, "smiles"):
            return

        text = self.smilesTextEdit.toPlainText().strip()

        if not text:
            self.parameter.smiles = []
            return

        # Split by commas and clean up whitespace
        # Note: SMILES strings should not contain commas, so this is safe
        smiles_list = [s.strip() for s in text.split(",") if s.strip()]
        self.parameter.smiles = smiles_list
