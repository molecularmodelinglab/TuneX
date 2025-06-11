"""
Managers for handling parameter-related responsibilities.

This module separates concerns in parameter management by providing
specialized classes for different aspects:
- ParameterRowManager: Manages table rows and UI widgets
- ParameterSerializer: Handles save/load operations
- Parameter validation is handled by the constraint widgets themselves
"""

from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QTableWidget,
    QLineEdit,
    QComboBox,
    QPushButton,
    QWidget,
    QHBoxLayout,
)

from app.models.parameters import BaseParameter
from app.models.enums import ParameterType
from .widget_factory import create_constraint_widget
from .constraint_widgets import BaseConstraintWidget


class ParameterRowManager:
    """
    Manages table rows and constraint widgets for parameters.

    This class has full ownership of the parameters table, including:
    - Table structure and column definitions
    - Adding/removing parameter rows
    - Creating appropriate UI widgets for each parameter type
    - Managing the relationship between UI widgets and parameter objects
    - Validating all widgets (which in turn validate their parameters)

    By centralizing all table-related logic here, we avoid magic numbers
    and ensure consistency when the table structure changes.
    """

    # Column definitions - single source of truth for table structure
    COLUMN_NAME = 0
    COLUMN_TYPE = 1
    COLUMN_CONSTRAINTS = 2
    COLUMN_ACTIONS = 3

    COLUMN_HEADERS = ["Param. Name", "Param. Type", "Values", "Del."]

    CONSTRAINTS_MIN_WIDTH = 400

    # Parameter type display names for the UI dropdown
    TYPE_DISPLAY_NAMES = {
        ParameterType.DISCRETE_NUMERICAL_REGULAR: "Discrete Numerical (Regular)",
        ParameterType.DISCRETE_NUMERICAL_IRREGULAR: "Discrete Numerical (Irregular)",
        ParameterType.CONTINUOUS_NUMERICAL: "Continuous Numerical",
        ParameterType.CATEGORICAL: "Categorical",
        ParameterType.FIXED: "Fixed Value",
        ParameterType.SUBSTANCE: "Substance (SMILES)",
    }

    def __init__(self, parameters: List[BaseParameter]) -> None:
        """
        Initialize the row manager.

        Args:
            parameters: List of parameter objects (will be modified)
        """
        self.parameters: List[BaseParameter] = parameters
        self.constraintWidgets: List[Optional[BaseConstraintWidget]] = []

        # Create and setup the table
        self.parametersTable: QTableWidget = self._create_table()

    def get_table_widget(self) -> QTableWidget:
        """
        Get the table widget managed by this class.

        Returns:
            QTableWidget: The configured parameters table
        """
        return self.parametersTable

    def _create_table(self) -> QTableWidget:
        """
        Create and configure the parameters table.

        Returns:
            QTableWidget: Fully configured table ready for use
        """
        parametersTable = QTableWidget()
        parametersTable.setColumnCount(len(self.COLUMN_HEADERS))
        parametersTable.setHorizontalHeaderLabels(self.COLUMN_HEADERS)

        # Configure table appearance and behavior
        parametersTable.setAlternatingRowColors(True)
        parametersTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set specific column widths for better proportions (wider overall)
        parametersTable.setColumnWidth(self.COLUMN_NAME, 250)      # Parameter Name (wider)
        parametersTable.setColumnWidth(self.COLUMN_TYPE, 250)      # Type dropdown (wider)
        parametersTable.setColumnWidth(self.COLUMN_CONSTRAINTS, 600)  # Constraints (much wider)
        parametersTable.setColumnWidth(self.COLUMN_ACTIONS, 60)    # Actions (slightly wider)
        
        # Set minimum table size
        parametersTable.setMinimumWidth(1200)  # Total width for all columns
        parametersTable.setMinimumHeight(500)   # Minimum height
        
        # Disable stretch to maintain fixed widths
        parametersTable.horizontalHeader().setStretchLastSection(False)
        
        # Set default row height to be taller
        parametersTable.verticalHeader().setDefaultSectionSize(50)

        return parametersTable

    def add_new_parameter_row(self) -> None:
        """Add a new parameter row to the table."""
        row_count = self.parametersTable.rowCount()
        self.parametersTable.insertRow(row_count)

        # Create UI components for the row
        nameEdit = self._create_name_widget(row_count)
        typeComboBox = self._create_type_combo(row_count)
        removeButton = self._create_remove_button()

        self.parametersTable.setCellWidget(row_count, self.COLUMN_NAME, nameEdit)
        self.parametersTable.setCellWidget(row_count, self.COLUMN_TYPE, typeComboBox)
        self.parametersTable.setCellWidget(
            row_count, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget()
        )
        self.parametersTable.setCellWidget(
            row_count, self.COLUMN_ACTIONS, self._create_button_container(removeButton)
        )

        self.parameters.append(None)
        self.constraintWidgets.append(None)

    def remove_parameter_row(self, row: int) -> None:
        """Remove the specified parameter row from the table."""
        if row < 0 or row >= self.parametersTable.rowCount():
            return

        self.parametersTable.removeRow(row)

        if row < len(self.parameters):
            removed_param = self.parameters.pop(row)
            print(f"Removed parameter: {removed_param}")

        if row < len(self.constraintWidgets):
            self.constraintWidgets.pop(row)

    def update_parameter_type(self, row: int, param_type: ParameterType) -> None:
        """Update parameter type and create corresponding constraint widget."""
        if row >= len(self.parameters):
            return

        parameterName = self._get_parameter_name_from_ui(row)

        # Create new parameter object
        parameter = BaseParameter.create_from_type(param_type, parameterName)
        self.parameters[row] = parameter

        # Create constraint widget using factory
        constraintWidget = create_constraint_widget(parameter)
        self.constraintWidgets[row] = constraintWidget

        # Set constraint widget in table using column constant
        if constraintWidget:
            self.parametersTable.setCellWidget(
                row, self.COLUMN_CONSTRAINTS, constraintWidget.get_widget()
            )
        else:
            self.parametersTable.setCellWidget(
                row, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget()
            )

        print(f"Updated parameter {row}: {parameter}")

    def validate_all_widgets(self) -> tuple[bool, Optional[str]]:
        """
        Validate all constraint widgets.

        This method asks each constraint widget to validate itself.
        Each widget will:
        1. Sync its UI data to the parameter object
        2. Validate the parameter object
        3. Return validation result

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not self.constraintWidgets:
            return False, "No parameters configured"

        # Check that all parameters have been created (no None values)
        noneIndices = []
        for i, widget in enumerate(self.constraintWidgets):
            if widget is None:
                noneIndices.append(i + 1)

        if noneIndices:
            indicesString = ", ".join(str(i) for i in noneIndices)
            return False, f"Parameters {indicesString} have no type selected"

        # Validate each widget (which validates its parameter)
        for i, constraintWidget in enumerate(self.constraintWidgets):
            if constraintWidget is None:
                continue

            # Update parameter name from UI first using helper method
            self._sync_parameter_name(i)

            # Let the widget validate itself
            isValid, errorMessage = constraintWidget.validate()
            if not isValid:
                parameterName = (
                    self.parameters[i].name
                    if self.parameters[i]
                    else f"Parameter {i + 1}"
                )
                return False, f"Parameter '{parameterName}' validation error: {errorMessage}"

        # Check for duplicate parameter names
        names = [param.name for param in self.parameters if param is not None]
        if len(names) != len(set(names)):
            return False, "Parameter names must be unique"

        return True, None

    def sync_ui_to_parameters(self) -> None:
        """
        Sync UI data to parameter objects.

        This method updates parameter names from the UI and asks each
        constraint widget to sync its data to its parameter.
        """
        for i in range(len(self.constraintWidgets)):
            # Update parameter name using helper method
            self._sync_parameter_name(i)

            # Let constraint widget sync its data
            constraintWidget = self.constraintWidgets[i]
            if constraintWidget:
                constraintWidget._save_to_parameter()

    def load_parameters_to_table(self, parameters: List[BaseParameter]) -> None:
        """Load parameters into the table UI."""
        # Clear existing data
        self.parametersTable.setRowCount(0)
        self.parameters.clear()
        self.constraintWidgets.clear()

        # Add each parameter
        for parameter in parameters:
            self._add_loaded_parameter_to_table(parameter)

    def clear_table(self) -> None:
        """Clear all parameters from the table."""
        self.parametersTable.setRowCount(0)
        self.parameters.clear()
        self.constraintWidgets.clear()

    def _sync_parameter_name(self, row: int) -> None:
        """Sync parameter name from UI to parameter object."""
        if row >= len(self.parameters) or self.parameters[row] is None:
            return

        parameterName = self._get_parameter_name_from_ui(row)
        self.parameters[row].name = parameterName

    def _get_parameter_name_from_ui(self, row: int) -> str:
        """
        Get parameter name from UI widget, with fallback to default name.

        Args:
            row: Table row index

        Returns:
            Parameter name from UI, or default name if widget is invalid/empty
        """
        nameWidget = self.parametersTable.cellWidget(row, self.COLUMN_NAME)
        if isinstance(nameWidget, QLineEdit) and nameWidget.text().strip():
            return nameWidget.text().strip()
        return f"Parameter_{row + 1}"

    def _get_parameter_type_from_ui(self, row: int) -> Optional[ParameterType]:
        """
        Get selected parameter type from UI combo box.

        Args:
            row: Table row index

        Returns:
            Selected parameter type, or None if no type selected or widget invalid
        """
        typeComboBox = self.parametersTable.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(typeComboBox, QComboBox):
            currentIndex = typeComboBox.currentIndex()
            if currentIndex > 0:  # Skip placeholder (index 0)
                return typeComboBox.itemData(currentIndex)
        return None

    def _set_parameter_name_in_ui(self, row: int, name: str) -> None:
        """
        Set parameter name in UI widget.

        Args:
            row: Table row index
            name: Parameter name to set
        """
        nameWidget = self.parametersTable.cellWidget(row, self.COLUMN_NAME)
        if isinstance(nameWidget, QLineEdit):
            nameWidget.setText(name)

    def _set_parameter_type_in_ui(self, row: int, param_type: ParameterType) -> None:
        """
        Set parameter type selection in UI combo box.

        Args:
            row: Table row index
            param_type: Parameter type to select
        """
        typeComboBox = self.parametersTable.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(typeComboBox, QComboBox):
            # Find the index for this parameter type
            for i in range(typeComboBox.count()):
                if typeComboBox.itemData(i) == param_type:
                    typeComboBox.setCurrentIndex(i)
                    break

    def _create_name_widget(self, row: int) -> QLineEdit:
        """Create a line edit widget for parameter name."""
        nameEdit = QLineEdit(f"Parameter_{row + 1}")
        nameEdit.setObjectName("ParameterNameInput")
        nameEdit.setPlaceholderText("Enter parameter name...")
        return nameEdit

    def _create_type_combo(self, row: int) -> QComboBox:
        """Create a combo box for parameter type selection."""
        typeComboBox = QComboBox()
        typeComboBox.setObjectName("ParameterTypeCombo")
        typeComboBox.addItem("Select parameter type...", None)

        for paramType, displayName in self.TYPE_DISPLAY_NAMES.items():
            typeComboBox.addItem(displayName, paramType)

        # Connect to handler
        typeComboBox.currentIndexChanged.connect(
            lambda index: self._on_type_changed(row, index)
        )

        return typeComboBox

    def _create_remove_button(self) -> QPushButton:
        """Create a remove button for the parameter row."""
        removeButton = QPushButton("✕") 
        removeButton.setObjectName("ParameterRemoveButton")
        removeButton.setMaximumWidth(10)
        removeButton.setMaximumHeight(10)
        removeButton.setStyleSheet("font-size: 16px;")
        removeButton.setToolTip("Remove this parameter")
        return removeButton

    def _create_button_container(self, button: QPushButton) -> QWidget:
        """Create a centered container for the remove button."""
        buttonWidget = QWidget()
        buttonLayout = QHBoxLayout(buttonWidget)
        buttonLayout.addStretch()
        buttonLayout.addWidget(button)
        buttonLayout.addStretch()
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        # Connect remove functionality
        button.clicked.connect(lambda: self._remove_by_button(button))

        return buttonWidget

    def _create_empty_constraints_widget(self) -> QWidget:
        """Create an empty placeholder widget for the constraints column."""
        emptyWidget = QWidget()
        emptyWidget.setEnabled(False)
        return emptyWidget

    def _on_type_changed(self, row: int, index: int) -> None:
        """Handle parameter type selection change."""
        if index == 0:  # Placeholder selected
            return

        parameterType = self._get_parameter_type_from_ui(row)
        if parameterType is not None:
            self.update_parameter_type(row, parameterType)

    def _remove_by_button(self, button: QPushButton) -> None:
        """Find row by button and remove it."""
        for row in range(self.parametersTable.rowCount()):
            widget = self.parametersTable.cellWidget(row, self.COLUMN_ACTIONS)
            if widget and widget.findChild(QPushButton) == button:
                self.remove_parameter_row(row)
                break

    def _add_loaded_parameter_to_table(self, parameter: BaseParameter) -> None:
        """Add a loaded parameter to the table."""
        rowCount = self.parametersTable.rowCount()
        self.parametersTable.insertRow(rowCount)

        nameEdit = QLineEdit()
        self.parametersTable.setCellWidget(rowCount, self.COLUMN_NAME, nameEdit)
        self._set_parameter_name_in_ui(rowCount, parameter.name)

        # Type combo with pre-selected value using helper method
        typeComboBox = self._create_type_combo(rowCount)
        self.parametersTable.setCellWidget(rowCount, self.COLUMN_TYPE, typeComboBox)
        self._set_parameter_type_in_ui(rowCount, parameter.parameter_type)

        # Constraint widget
        constraintWidget = create_constraint_widget(parameter)
        if constraintWidget:
            self.parametersTable.setCellWidget(
                rowCount, self.COLUMN_CONSTRAINTS, constraintWidget.get_widget()
            )
        else:
            self.parametersTable.setCellWidget(
                rowCount,
                self.COLUMN_CONSTRAINTS,
                self._create_empty_constraints_widget(),
            )

        # Remove button
        removeButton = self._create_remove_button()
        self.parametersTable.setCellWidget(
            rowCount, self.COLUMN_ACTIONS, self._create_button_container(removeButton)
        )

        # Store parameter and widget
        self.parameters.append(parameter)
        self.constraintWidgets.append(constraintWidget)


class ParameterSerializer:
    """
    Handles serialization and deserialization of parameters.

    This class provides a simple interface for converting parameters to/from
    dictionary format. The actual serialization logic is handled by the
    parameter classes themselves, keeping this class simple and focused.
    """

    @staticmethod
    def serialize_parameters(parameters: List[BaseParameter]) -> List[Dict[str, Any]]:
        """
        Convert parameter objects to dictionary format for saving.

        Args:
            parameters: List of parameter objects to serialize

        Returns:
            List of dictionaries representing the parameters
        """
        parametersData = []
        for param in parameters:
            if param is not None:
                parametersData.append(param.to_dict())
        return parametersData

    @staticmethod
    def deserialize_parameters(
        parameters_data: List[Dict[str, Any]],
    ) -> List[BaseParameter]:
        """
        Convert dictionary data back to parameter objects.

        Args:
            parameters_data: List of parameter dictionaries (from serialize_parameters)

        Returns:
            List of parameter objects

        Note:
            Uses BaseParameter.from_dict() so this class doesn't need to know
            about internal parameter formats or types.
        """
        parameters = []

        for paramDict in parameters_data:
            try:
                # Let the parameter classes handle their own deserialization
                parameter = BaseParameter.from_dict(paramDict)
                parameters.append(parameter)
            except Exception as e:
                print(f"Error loading parameter: {e}")
                # Continue loading other parameters even if one fails

        return parameters
