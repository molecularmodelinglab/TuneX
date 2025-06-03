"""
Managers for handling parameter-related responsibilities.

This module separates concerns in parameter management by providing
specialized classes for different aspects:
- ParameterRowManager: Manages table rows and UI widgets
- ParameterSerializer: Handles save/load operations
- Parameter validation is handled by the constraint widgets themselves
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QTableWidget, QLineEdit, QComboBox, QPushButton, QWidget, QHBoxLayout

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
    
    COLUMN_HEADERS = ["Parameter Name", "Type", "Constraints", "Actions"]
    
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
        self.constraint_widgets: List[Optional[BaseConstraintWidget]] = []
        
        # Create and setup the table
        self.table: QTableWidget = self._create_table()
    
    def get_table_widget(self) -> QTableWidget:
        """
        Get the table widget managed by this class.
        
        Returns:
            QTableWidget: The configured parameters table
        """
        return self.table
    
    def _create_table(self) -> QTableWidget:
        """
        Create and configure the parameters table.
        
        Returns:
            QTableWidget: Fully configured table ready for use
        """
        table = QTableWidget()
        table.setColumnCount(len(self.COLUMN_HEADERS))
        table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        
        # Configure table appearance and behavior
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def add_new_parameter_row(self) -> None:
        """Add a new parameter row to the table."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        # Create UI components for the row
        name_edit = self._create_name_widget(row_count)
        type_combo = self._create_type_combo(row_count)
        remove_button = self._create_remove_button()

        self.table.setCellWidget(row_count, self.COLUMN_NAME, name_edit)
        self.table.setCellWidget(row_count, self.COLUMN_TYPE, type_combo)
        self.table.setCellWidget(row_count, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())
        self.table.setCellWidget(row_count, self.COLUMN_ACTIONS, self._create_button_container(remove_button))

        self.parameters.append(None)
        self.constraint_widgets.append(None)
    
    def remove_parameter_row(self, row: int) -> None:
        """Remove the specified parameter row from the table."""
        if row < 0 or row >= self.table.rowCount():
            return

        self.table.removeRow(row)

        if row < len(self.parameters):
            removed_param = self.parameters.pop(row)
            print(f"Removed parameter: {removed_param}")
        
        if row < len(self.constraint_widgets):
            self.constraint_widgets.pop(row)
    
    def update_parameter_type(self, row: int, param_type: ParameterType) -> None:
        """Update parameter type and create corresponding constraint widget."""
        if row >= len(self.parameters):
            return

        param_name = self._get_parameter_name_from_ui(row)
        
        # Create new parameter object
        parameter = BaseParameter.create_from_type(param_type, param_name)
        self.parameters[row] = parameter
        
        # Create constraint widget using factory
        constraint_widget = create_constraint_widget(parameter)
        self.constraint_widgets[row] = constraint_widget
        
        # Set constraint widget in table using column constant
        if constraint_widget:
            self.table.setCellWidget(row, self.COLUMN_CONSTRAINTS, constraint_widget.get_widget())
        else:
            self.table.setCellWidget(row, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())
        
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
        if not self.constraint_widgets:
            return False, "No parameters configured"
        
        # Check that all parameters have been created (no None values)
        none_indices = []
        for i, widget in enumerate(self.constraint_widgets):
            if widget is None:
                none_indices.append(i + 1)
        
        if none_indices:
            indices_str = ", ".join(str(i) for i in none_indices)
            return False, f"Parameters {indices_str} have no type selected"
        
        # Validate each widget (which validates its parameter)
        for i, constraint_widget in enumerate(self.constraint_widgets):
            if constraint_widget is None:
                continue
                
            # Update parameter name from UI first using helper method
            self._sync_parameter_name(i)
            
            # Let the widget validate itself
            is_valid, error_msg = constraint_widget.validate()
            if not is_valid:
                param_name = self.parameters[i].name if self.parameters[i] else f"Parameter {i+1}"
                return False, f"Parameter '{param_name}' validation error: {error_msg}"
        
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
        for i in range(len(self.constraint_widgets)):
            # Update parameter name using helper method
            self._sync_parameter_name(i)
            
            # Let constraint widget sync its data
            constraint_widget = self.constraint_widgets[i]
            if constraint_widget:
                constraint_widget._save_to_parameter()
    
    def load_parameters_to_table(self, parameters: List[BaseParameter]) -> None:
        """Load parameters into the table UI."""
        # Clear existing data
        self.table.setRowCount(0)
        self.parameters.clear()
        self.constraint_widgets.clear()
        
        # Add each parameter
        for parameter in parameters:
            self._add_loaded_parameter_to_table(parameter)
    
    def _sync_parameter_name(self, row: int) -> None:
        """Sync parameter name from UI to parameter object."""
        if row >= len(self.parameters) or self.parameters[row] is None:
            return
            
        param_name = self._get_parameter_name_from_ui(row)
        self.parameters[row].name = param_name
    
    def _get_parameter_name_from_ui(self, row: int) -> str:
        """
        Get parameter name from UI widget, with fallback to default name.
        
        Args:
            row: Table row index
            
        Returns:
            Parameter name from UI, or default name if widget is invalid/empty
        """
        name_widget = self.table.cellWidget(row, self.COLUMN_NAME)
        if isinstance(name_widget, QLineEdit) and name_widget.text().strip():
            return name_widget.text().strip()
        return f"Parameter_{row + 1}"
    
    def _get_parameter_type_from_ui(self, row: int) -> Optional[ParameterType]:
        """
        Get selected parameter type from UI combo box.
        
        Args:
            row: Table row index
            
        Returns:
            Selected parameter type, or None if no type selected or widget invalid
        """
        type_combo = self.table.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(type_combo, QComboBox):
            current_index = type_combo.currentIndex()
            if current_index > 0:  # Skip placeholder (index 0)
                return type_combo.itemData(current_index)
        return None
    
    def _set_parameter_name_in_ui(self, row: int, name: str) -> None:
        """
        Set parameter name in UI widget.
        
        Args:
            row: Table row index
            name: Parameter name to set
        """
        name_widget = self.table.cellWidget(row, self.COLUMN_NAME)
        if isinstance(name_widget, QLineEdit):
            name_widget.setText(name)
    
    def _set_parameter_type_in_ui(self, row: int, param_type: ParameterType) -> None:
        """
        Set parameter type selection in UI combo box.
        
        Args:
            row: Table row index
            param_type: Parameter type to select
        """
        type_combo = self.table.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(type_combo, QComboBox):
            # Find the index for this parameter type
            for i in range(type_combo.count()):
                if type_combo.itemData(i) == param_type:
                    type_combo.setCurrentIndex(i)
                    break
    
    def _create_name_widget(self, row: int) -> QLineEdit:
        """Create a line edit widget for parameter name."""
        name_edit = QLineEdit(f"Parameter_{row + 1}")
        return name_edit
    
    def _create_type_combo(self, row: int) -> QComboBox:
        """Create a combo box for parameter type selection."""
        type_combo = QComboBox()
        type_combo.addItem("Select parameter type...", None)
        
        for param_type, display_name in self.TYPE_DISPLAY_NAMES.items():
            type_combo.addItem(display_name, param_type)
        
        # Connect to handler
        type_combo.currentIndexChanged.connect(
            lambda index: self._on_type_changed(row, index)
        )
        
        return type_combo
    
    def _create_remove_button(self) -> QPushButton:
        """Create a remove button for the parameter row."""
        remove_button = QPushButton("❌")
        remove_button.setMaximumWidth(40)
        remove_button.setToolTip("Remove this parameter")
        return remove_button
    
    def _create_button_container(self, button: QPushButton) -> QWidget:
        """Create a centered container for the remove button."""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addStretch()
        button_layout.addWidget(button)
        button_layout.addStretch()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect remove functionality
        button.clicked.connect(lambda: self._remove_by_button(button))
        
        return button_widget
    
    def _create_empty_constraints_widget(self) -> QWidget:
        """Create an empty placeholder widget for the constraints column."""
        empty_widget = QWidget()
        empty_widget.setEnabled(False)
        return empty_widget
    
    def _on_type_changed(self, row: int, index: int) -> None:
        """Handle parameter type selection change."""
        if index == 0:  # Placeholder selected
            return
        
        param_type = self._get_parameter_type_from_ui(row)
        if param_type is not None:
            self.update_parameter_type(row, param_type)
    
    def _remove_by_button(self, button: QPushButton) -> None:
        """Find row by button and remove it."""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, self.COLUMN_ACTIONS)
            if widget and widget.findChild(QPushButton) == button:
                self.remove_parameter_row(row)
                break
    
    def _add_loaded_parameter_to_table(self, parameter: BaseParameter) -> None:
        """Add a loaded parameter to the table."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        # Name widget - set using helper method
        name_edit = QLineEdit()
        self.table.setCellWidget(row_count, self.COLUMN_NAME, name_edit)
        self._set_parameter_name_in_ui(row_count, parameter.name)
        
        # Type combo with pre-selected value using helper method
        type_combo = self._create_type_combo(row_count)
        self.table.setCellWidget(row_count, self.COLUMN_TYPE, type_combo)
        self._set_parameter_type_in_ui(row_count, parameter.parameter_type)
        
        # Constraint widget
        constraint_widget = create_constraint_widget(parameter)
        if constraint_widget:
            self.table.setCellWidget(row_count, self.COLUMN_CONSTRAINTS, constraint_widget.get_widget())
        else:
            self.table.setCellWidget(row_count, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())
        
        # Remove button
        remove_button = self._create_remove_button()
        self.table.setCellWidget(row_count, self.COLUMN_ACTIONS, self._create_button_container(remove_button))
        
        # Store parameter and widget
        self.parameters.append(parameter)
        self.constraint_widgets.append(constraint_widget)
    
    def _create_type_combo_with_selection(self, row: int, parameter: BaseParameter) -> QComboBox:
        """Create type combo with pre-selected parameter type."""
        type_combo = QComboBox()
        type_combo.addItem("Select parameter type...", None)
        
        selected_index = 0
        for i, (param_type, display_name) in enumerate(self.TYPE_DISPLAY_NAMES.items(), 1):
            type_combo.addItem(display_name, param_type)
            
            # Check if this matches our parameter type
            if param_type == parameter.parameter_type:
                selected_index = i
        
        type_combo.setCurrentIndex(selected_index)
        type_combo.currentIndexChanged.connect(
            lambda index: self._on_type_changed(row, index)
        )
        
        return type_combo


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
        parameters_data = []
        for param in parameters:
            if param is not None:
                parameters_data.append(param.to_dict())
        return parameters_data
    
    @staticmethod 
    def deserialize_parameters(parameters_data: List[Dict[str, Any]]) -> List[BaseParameter]:
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
        
        for param_dict in parameters_data:
            try:
                # Let the parameter classes handle their own deserialization
                parameter = BaseParameter.from_dict(param_dict)
                parameters.append(parameter)
            except Exception as e:
                print(f"Error loading parameter: {e}")
                # Continue loading other parameters even if one fails
                
        return parameters