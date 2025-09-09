"""
Managers for handling parameter-related responsibilities.

This module separates concerns in parameter management by providing
specialized classes for different aspects:
- ParameterRowManager: Manages table rows and UI widgets
- Parameter validation is handled by the constraint widgets themselves
"""

import logging
from typing import List, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QWidget,
)

from app.models.enums import ParameterType
from app.models.parameters import BaseParameter

from .constraint_widgets import BaseConstraintWidget
from .widget_factory import create_constraint_widget


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

    # UI Geometry Constants
    CONSTRAINTS_MIN_WIDTH = 400
    COLUMN_WIDTH_NAME = 250
    COLUMN_WIDTH_TYPE = 250
    COLUMN_WIDTH_ACTIONS = 60

    TABLE_MIN_HEIGHT = 500
    DEFAULT_ROW_HEIGHT = 50

    # Button Constants
    REMOVE_BUTTON_MAX_WIDTH = 10
    REMOVE_BUTTON_MAX_HEIGHT = 10
    REMOVE_BUTTON_TEXT = "✕"
    REMOVE_BUTTON_FONT_SIZE = "16px"
    REMOVE_BUTTON_TOOLTIP = "Remove this parameter"

    # Layout Constants
    BUTTON_LAYOUT_MARGINS = (0, 0, 0, 0)

    # UI Text Constants
    DEFAULT_PARAMETER_NAME_PREFIX = "Parameter_"
    PARAMETER_NAME_PLACEHOLDER = "Enter parameter name..."
    PARAMETER_TYPE_PLACEHOLDER = "Select parameter type..."

    # Validation Error Messages
    NO_PARAMETERS_MESSAGE = "No parameters configured"
    PARAMETER_TYPE_REQUIRED_MESSAGE = "Parameter {0} must have a type"
    PARAMETER_NAME_REQUIRED_MESSAGE = "Parameter {0} must have a name"
    PARAMETER_VALIDATION_ERROR_MESSAGE = "Parameter {0}: {1}"
    DUPLICATE_NAMES_MESSAGE = "Parameter names must be unique"

    # Object Names for Styling
    OBJECT_NAME_PARAMETER_INPUT = "ParameterNameInput"
    OBJECT_NAME_TYPE_COMBO = "ParameterTypeCombo"
    OBJECT_NAME_REMOVE_BUTTON = "ParameterRemoveButton"

    def __init__(self, parameters: List[Optional[BaseParameter]]) -> None:
        """
        Initialize the row manager.

        Args:
            parameters: List of parameter objects (will be modified)
        """
        self.parameters: List[Optional[BaseParameter]] = parameters
        self.constraint_widgets: List[Optional[BaseConstraintWidget]] = []
        self.logger = logging.getLogger(__name__)

        # Create and setup the table
        self.parameters_table: QTableWidget = self._create_table()

    def get_table_widget(self) -> QTableWidget:
        """
        Get the table widget managed by this class.

        Returns:
            QTableWidget: The configured parameters table
        """
        return self.parameters_table

    def _create_table(self) -> QTableWidget:
        """
        Create and configure the parameters table.

        Returns:
            QTableWidget: Fully configured table ready for use
        """
        parameters_table = QTableWidget()
        parameters_table.setColumnCount(len(self.COLUMN_HEADERS))
        parameters_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)

        # Configure table appearance and behavior
        parameters_table.setAlternatingRowColors(True)
        parameters_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = parameters_table.horizontalHeader()
        header.setSectionResizeMode(self.COLUMN_NAME, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COLUMN_TYPE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COLUMN_CONSTRAINTS, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COLUMN_ACTIONS, QHeaderView.ResizeMode.ResizeToContents)

        parameters_table.setColumnWidth(self.COLUMN_NAME, self.COLUMN_WIDTH_NAME)
        parameters_table.setColumnWidth(self.COLUMN_TYPE, self.COLUMN_WIDTH_TYPE)
        parameters_table.setColumnWidth(self.COLUMN_ACTIONS, self.COLUMN_WIDTH_ACTIONS)

        # Set minimum table size
        parameters_table.setMinimumHeight(self.TABLE_MIN_HEIGHT)

        # Set default row height to be taller
        parameters_table.verticalHeader().setDefaultSectionSize(self.DEFAULT_ROW_HEIGHT)

        return parameters_table

    def add_new_parameter_row(self) -> None:
        """Add a new parameter row to the table."""
        row_count = self.parameters_table.rowCount()
        self.parameters_table.insertRow(row_count)

        # Create UI components for the row
        name_edit = self._create_name_widget(row_count)
        type_combo_box = self._create_type_combo(row_count)
        remove_button = self._create_remove_button()

        self.parameters_table.setCellWidget(row_count, self.COLUMN_NAME, name_edit)
        self.parameters_table.setCellWidget(row_count, self.COLUMN_TYPE, type_combo_box)
        self.parameters_table.setCellWidget(row_count, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())
        self.parameters_table.setCellWidget(
            row_count, self.COLUMN_ACTIONS, self._create_button_container(remove_button)
        )

        self.parameters.append(None)
        self.constraint_widgets.append(None)

    def remove_parameter_row(self, row: int) -> None:
        """Remove the specified parameter row from the table."""
        if row < 0 or row >= self.parameters_table.rowCount():
            return

        self.parameters_table.removeRow(row)

        if row < len(self.parameters):
            removed_param = self.parameters.pop(row)
            self.logger.info(f"Removed parameter: {removed_param}")

        if row < len(self.constraint_widgets):
            self.constraint_widgets.pop(row)

    def update_parameter_type(self, row: int, param_type: ParameterType) -> None:
        """Update parameter type and create corresponding constraint widget."""
        if row >= len(self.parameters):
            return

        parameter_name = self._get_parameter_name_from_ui(row)

        # Create new parameter object
        parameter = BaseParameter.create_from_type(param_type, parameter_name)
        self.parameters[row] = parameter

        # Create constraint widget using factory
        constraint_widget = create_constraint_widget(parameter)
        self.constraint_widgets[row] = constraint_widget

        # Set constraint widget in table using column constant
        if constraint_widget:
            self.parameters_table.setCellWidget(row, self.COLUMN_CONSTRAINTS, constraint_widget.get_widget())
        else:
            self.parameters_table.setCellWidget(row, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())

        self.logger.info(f"Updated parameter {row}: {parameter}")

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
            return False, self.NO_PARAMETERS_MESSAGE

        # Check for incomplete parameters (missing type or name)
        for i, constraint_widget in enumerate(self.constraint_widgets):
            if constraint_widget is None:
                return False, self.PARAMETER_TYPE_REQUIRED_MESSAGE.format(i + 1)

            self._sync_parameter_name(i)

            is_valid, error_message = constraint_widget.validate()
            if not is_valid:
                return False, self.PARAMETER_VALIDATION_ERROR_MESSAGE.format(i + 1, error_message)

            param = self.parameters[i]
            if not param or not param.name:
                return False, self.PARAMETER_NAME_REQUIRED_MESSAGE.format(i + 1)

        # Check for duplicate parameter names
        names = [param.name for param in self.parameters if param is not None and param.name]
        if len(names) != len(set(names)):
            return False, self.DUPLICATE_NAMES_MESSAGE

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
        self.parameters_table.setRowCount(0)
        self.parameters.clear()
        self.constraint_widgets.clear()

        # Add each parameter
        for parameter in parameters:
            self._add_loaded_parameter_to_table(parameter)

    def clear_table(self) -> None:
        """Clear all parameters from the table."""
        self.parameters_table.setRowCount(0)
        self.parameters.clear()
        self.constraint_widgets.clear()

    def _sync_parameter_name(self, row: int) -> None:
        """Sync parameter name from UI to parameter object."""
        if row >= len(self.parameters) or self.parameters[row] is None:
            return
        parameter = self.parameters[row]
        if parameter is None:
            return
        parameter.name = self._get_parameter_name_from_ui(row)

    def _get_parameter_name_from_ui(self, row: int) -> str:
        """
        Get parameter name from UI widget, with fallback to default name.

        Args:
            row: Table row index

        Returns:
            Parameter name from UI.
        """
        name_widget = self.parameters_table.cellWidget(row, self.COLUMN_NAME)
        if isinstance(name_widget, QLineEdit) and name_widget.text().strip():
            return name_widget.text().strip()
        return ""

    def _get_parameter_type_from_ui(self, row: int) -> Optional[ParameterType]:
        """
        Get selected parameter type from UI combo box.

        Args:
            row: Table row index

        Returns:
            Selected parameter type, or None if no type selected or widget invalid
        """
        type_combo_box = self.parameters_table.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(type_combo_box, QComboBox):
            current_index = type_combo_box.currentIndex()
            if current_index > 0:  # Skip placeholder (index 0)
                return type_combo_box.itemData(current_index)
        return None

    def _set_parameter_name_in_ui(self, row: int, name: str) -> None:
        """
        Set parameter name in UI widget.

        Args:
            row: Table row index
            name: Parameter name to set
        """
        name_widget = self.parameters_table.cellWidget(row, self.COLUMN_NAME)
        if isinstance(name_widget, QLineEdit):
            name_widget.setText(name)

    def _set_parameter_type_in_ui(self, row: int, param_type: ParameterType) -> None:
        """
        Set parameter type selection in UI combo box.

        Args:
            row: Table row index
            param_type: Parameter type to select
        """
        type_combo_box = self.parameters_table.cellWidget(row, self.COLUMN_TYPE)
        if isinstance(type_combo_box, QComboBox):
            # Find the index for this parameter type
            for i in range(type_combo_box.count()):
                if type_combo_box.itemData(i) == param_type:
                    type_combo_box.setCurrentIndex(i)
                    break

    def _create_name_widget(self, row: int) -> QLineEdit:
        """Create a line edit widget for parameter name."""
        name_edit = QLineEdit(f"{self.DEFAULT_PARAMETER_NAME_PREFIX}{row + 1}")
        name_edit.setObjectName(self.OBJECT_NAME_PARAMETER_INPUT)
        name_edit.setPlaceholderText(self.PARAMETER_NAME_PLACEHOLDER)
        # Connect to handler
        name_edit.textChanged.connect(lambda: self._on_name_changed_by_widget(name_edit))
        return name_edit

    def _create_type_combo(self, row: int) -> QComboBox:
        """Create a combo box for parameter type selection."""
        type_combo_box = QComboBox()
        type_combo_box.setObjectName(self.OBJECT_NAME_TYPE_COMBO)
        type_combo_box.addItem(self.PARAMETER_TYPE_PLACEHOLDER, None)

        for param_type in ParameterType:
            type_combo_box.addItem(param_type.display_name, param_type)

        # Connect to handler
        type_combo_box.currentIndexChanged.connect(lambda: self._on_type_changed_by_widget(type_combo_box))

        return type_combo_box

    def _create_remove_button(self) -> QPushButton:
        """Create a remove button for the parameter row."""
        remove_button = QPushButton(self.REMOVE_BUTTON_TEXT)
        remove_button.setObjectName(self.OBJECT_NAME_REMOVE_BUTTON)
        remove_button.setMaximumWidth(self.REMOVE_BUTTON_MAX_WIDTH)
        remove_button.setMaximumHeight(self.REMOVE_BUTTON_MAX_HEIGHT)
        remove_button.setStyleSheet(f"font-size: {self.REMOVE_BUTTON_FONT_SIZE};")
        remove_button.setToolTip(self.REMOVE_BUTTON_TOOLTIP)
        return remove_button

    def _create_button_container(self, button: QPushButton) -> QWidget:
        """Create a centered container for the remove button."""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addStretch()
        button_layout.addWidget(button)
        button_layout.addStretch()
        button_layout.setContentsMargins(*self.BUTTON_LAYOUT_MARGINS)

        # Connect remove functionality
        button.clicked.connect(lambda: self._remove_by_button(button))

        return button_widget

    def _create_empty_constraints_widget(self) -> QWidget:
        """Create an empty placeholder widget for the constraints column."""
        empty_widget = QWidget()
        empty_widget.setEnabled(False)
        return empty_widget

    def _find_row_by_widget(self, widget: QWidget, column: int) -> int:
        """Find which row contains the given widget in the specified column."""
        for row in range(self.parameters_table.rowCount()):
            if self.parameters_table.cellWidget(row, column) == widget:
                return row
        return -1

    def _on_type_changed(self, row: int, index: int) -> None:
        """Handle parameter type selection change."""
        parameter_type = self._get_parameter_type_from_ui(row)

        if parameter_type is None:
            self.parameters[row] = None
            self.constraint_widgets[row] = None
            self.parameters_table.setCellWidget(row, self.COLUMN_CONSTRAINTS, self._create_empty_constraints_widget())
            self.logger.info(f"Cleared parameter type for row {row}")
        else:
            self.update_parameter_type(row, parameter_type)

    def _on_name_changed(self, row: int) -> None:
        """Handle parameter name change - recreate parameter if type is selected."""
        parameter_type = self._get_parameter_type_from_ui(row)
        if parameter_type:
            self.update_parameter_type(row, parameter_type)

    def _on_type_changed_by_widget(self, type_widget: QComboBox) -> None:
        """Handle type change by finding current row of the widget."""
        row = self._find_row_by_widget(type_widget, self.COLUMN_TYPE)
        if row >= 0:
            index = type_widget.currentIndex()
            self._on_type_changed(row, index)

    def _on_name_changed_by_widget(self, name_widget: QLineEdit) -> None:
        """Handle name change by finding current row of the widget."""
        row = self._find_row_by_widget(name_widget, self.COLUMN_NAME)
        if row >= 0:
            self._on_name_changed(row)

    def _remove_by_button(self, button: QPushButton) -> None:
        """Find row by button and remove it."""
        for row in range(self.parameters_table.rowCount()):
            widget = self.parameters_table.cellWidget(row, self.COLUMN_ACTIONS)
            if widget and widget.findChild(QPushButton) == button:
                self.remove_parameter_row(row)
                break

    def _add_loaded_parameter_to_table(self, parameter: BaseParameter) -> None:
        """Add a loaded parameter to the table."""
        row_count = self.parameters_table.rowCount()
        self.parameters_table.insertRow(row_count)

        name_edit = QLineEdit()
        self.parameters_table.setCellWidget(row_count, self.COLUMN_NAME, name_edit)
        self._set_parameter_name_in_ui(row_count, parameter.name)

        # Type combo with pre-selected value using helper method
        type_combo_box = self._create_type_combo(row_count)
        self.parameters_table.setCellWidget(row_count, self.COLUMN_TYPE, type_combo_box)
        self._set_parameter_type_in_ui(row_count, parameter.parameter_type)

        # Constraint widget
        constraint_widget = create_constraint_widget(parameter)
        if constraint_widget:
            self.parameters_table.setCellWidget(row_count, self.COLUMN_CONSTRAINTS, constraint_widget.get_widget())
        else:
            self.parameters_table.setCellWidget(
                row_count,
                self.COLUMN_CONSTRAINTS,
                self._create_empty_constraints_widget(),
            )

        # Remove button
        remove_button = self._create_remove_button()
        self.parameters_table.setCellWidget(
            row_count, self.COLUMN_ACTIONS, self._create_button_container(remove_button)
        )

        # Store parameter and widget
        self.parameters.append(parameter)
        self.constraint_widgets.append(constraint_widget)
