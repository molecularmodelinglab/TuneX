import unittest
from typing import List, Optional
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QWidget

from app.models.enums import ParameterType
from app.models.parameters import BaseParameter
from app.screens.campaign.setup.components.parameter_managers import ParameterRowManager


class TestParameterRowManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for Qt widgets."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parameters: List[Optional[BaseParameter]] = []
        self.manager = ParameterRowManager(self.parameters)

        # Create a real QWidget for the constraint widget mock
        self.mock_widget = QWidget()

        # Mock the constraint widget factory to avoid UI dependencies
        self.constraint_widget_mock = Mock()
        self.constraint_widget_mock.get_widget.return_value = self.mock_widget
        self.constraint_widget_mock.validate.return_value = (True, None)
        self.constraint_widget_mock._save_to_parameter.return_value = None

    def tearDown(self):
        """Clean up after each test."""
        self.manager.clear_table()

    def test_initialization(self):
        """Test that manager initializes correctly."""
        self.assertIsNotNone(self.manager.parameters_table)
        self.assertEqual(self.manager.parameters_table.columnCount(), 4)
        self.assertEqual(self.manager.parameters_table.rowCount(), 0)
        self.assertEqual(len(self.parameters), 0)
        self.assertEqual(len(self.manager.constraint_widgets), 0)

    def test_add_new_parameter_row(self):
        """Test adding a new parameter row."""
        initial_row_count = self.manager.parameters_table.rowCount()

        self.manager.add_new_parameter_row()

        # Check table structure
        self.assertEqual(self.manager.parameters_table.rowCount(), initial_row_count + 1)

        # Check widgets are created
        name_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        type_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_TYPE)
        action_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_ACTIONS)

        self.assertIsInstance(name_widget, QLineEdit)
        self.assertIsInstance(type_widget, QComboBox)
        self.assertIsNotNone(action_widget)

        # Check data structures
        self.assertEqual(len(self.parameters), 1)
        self.assertEqual(len(self.manager.constraint_widgets), 1)
        self.assertIsNone(self.parameters[0])
        self.assertIsNone(self.manager.constraint_widgets[0])

    def test_remove_parameter_row_valid_index(self):
        """Test removing a parameter row with valid index."""
        # Add two rows
        self.manager.add_new_parameter_row()
        self.manager.add_new_parameter_row()

        # Remove first row
        self.manager.remove_parameter_row(0)

        # Check table structure
        self.assertEqual(self.manager.parameters_table.rowCount(), 1)
        self.assertEqual(len(self.parameters), 1)
        self.assertEqual(len(self.manager.constraint_widgets), 1)

    def test_remove_parameter_row_invalid_index(self):
        """Test removing a parameter row with invalid index."""
        self.manager.add_new_parameter_row()
        initial_count = self.manager.parameters_table.rowCount()

        # Try to remove invalid indices
        self.manager.remove_parameter_row(-1)
        self.manager.remove_parameter_row(10)

        # Nothing should change
        self.assertEqual(self.manager.parameters_table.rowCount(), initial_count)
        self.assertEqual(len(self.parameters), 1)

    def test_remove_middle_parameter_maintains_order(self):
        """Test that removing middle parameter maintains correct order."""
        # Add three rows and set parameter names to track order
        for _ in range(3):
            self.manager.add_new_parameter_row()

        # Simulate setting parameter names to track order
        name_widgets = []
        for row in range(3):
            name_widget = self.manager.parameters_table.cellWidget(row, self.manager.COLUMN_NAME)
            name_widget.setText(f"param_{row}")
            name_widgets.append(name_widget)

        # Remove middle row (index 1)
        self.manager.remove_parameter_row(1)

        # Check that we have 2 rows remaining
        self.assertEqual(self.manager.parameters_table.rowCount(), 2)

        # Check that the remaining rows have correct names
        remaining_name_0 = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        remaining_name_1 = self.manager.parameters_table.cellWidget(1, self.manager.COLUMN_NAME)

        self.assertEqual(remaining_name_0.text(), "param_0")
        self.assertEqual(remaining_name_1.text(), "param_2")

    def test_find_row_by_widget_name_column(self):
        """Test finding row by widget in name column."""
        self.manager.add_new_parameter_row()
        self.manager.add_new_parameter_row()

        # Get name widget from second row
        name_widget = self.manager.parameters_table.cellWidget(1, self.manager.COLUMN_NAME)

        # Find its row
        found_row = self.manager._find_row_by_widget(name_widget, self.manager.COLUMN_NAME)
        self.assertEqual(found_row, 1)

    def test_find_row_by_widget_type_column(self):
        """Test finding row by widget in type column."""
        self.manager.add_new_parameter_row()

        # Get type widget from first row
        type_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_TYPE)

        # Find its row
        found_row = self.manager._find_row_by_widget(type_widget, self.manager.COLUMN_TYPE)
        self.assertEqual(found_row, 0)

    def test_find_row_by_widget_not_found(self):
        """Test finding row by widget that doesn't exist."""
        self.manager.add_new_parameter_row()

        # Create a widget that's not in the table
        orphan_widget = QLineEdit()

        # Should return -1
        found_row = self.manager._find_row_by_widget(orphan_widget, self.manager.COLUMN_NAME)
        self.assertEqual(found_row, -1)

    def test_on_name_changed_by_widget_valid_widget(self):
        """Test name change handler with valid widget."""
        self.manager.add_new_parameter_row()

        name_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)

        # This should not raise an exception
        self.manager._on_name_changed_by_widget(name_widget)

    def test_on_name_changed_by_widget_invalid_widget(self):
        """Test name change handler with invalid widget."""
        orphan_widget = QLineEdit()

        # This should not raise an exception even with invalid widget
        self.manager._on_name_changed_by_widget(orphan_widget)

    def test_on_type_changed_by_widget_valid_widget(self):
        """Test type change handler with valid widget."""
        self.manager.add_new_parameter_row()

        type_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_TYPE)

        # This should not raise an exception
        self.manager._on_type_changed_by_widget(type_widget)

    def test_on_type_changed_by_widget_invalid_widget(self):
        """Test type change handler with invalid widget."""
        orphan_widget = QComboBox()

        # This should not raise an exception even with invalid widget
        self.manager._on_type_changed_by_widget(orphan_widget)

    def test_stale_closure_bug_simulation(self):
        """Test that demonstrates the stale closure bug is fixed."""
        # Add two parameters
        self.manager.add_new_parameter_row()
        self.manager.add_new_parameter_row()

        # Set names for tracking
        name_widget_0 = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        name_widget_1 = self.manager.parameters_table.cellWidget(1, self.manager.COLUMN_NAME)
        name_widget_0.setText("param_0")
        name_widget_1.setText("param_1")

        # Set type for second parameter to create a parameter object
        type_widget_1 = self.manager.parameters_table.cellWidget(1, self.manager.COLUMN_TYPE)
        type_widget_1.setCurrentIndex(1)  # Select first real parameter type

        # Delete first row - this shifts the second row up
        self.manager.remove_parameter_row(0)

        # Now the widget that was originally in row 1 is in row 0
        # The bug would occur here if we tried to change the type
        remaining_type_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_TYPE)

        # This should NOT raise IndexError: list assignment index out of range
        # because the dynamic widget lookup should find the current row (0)
        try:
            self.manager._on_type_changed_by_widget(remaining_type_widget)
            test_passed = True
        except IndexError:
            test_passed = False

        self.assertTrue(test_passed, "Stale closure bug still exists")

    def test_validate_all_widgets_no_parameters(self):
        """Test validation with no parameters."""
        is_valid, error_message = self.manager.validate_all_widgets()

        self.assertFalse(is_valid)
        self.assertEqual(error_message, self.manager.NO_PARAMETERS_MESSAGE)

    def test_validate_all_widgets_missing_type(self):
        """Test validation with parameter missing type."""
        self.manager.add_new_parameter_row()

        is_valid, error_message = self.manager.validate_all_widgets()

        self.assertFalse(is_valid)
        self.assertEqual(error_message, self.manager.PARAMETER_TYPE_REQUIRED_MESSAGE.format(1))

    def test_clear_table(self):
        """Test clearing the table."""
        # Add some parameters
        self.manager.add_new_parameter_row()
        self.manager.add_new_parameter_row()

        # Clear table
        self.manager.clear_table()

        # Check everything is cleared
        self.assertEqual(self.manager.parameters_table.rowCount(), 0)
        self.assertEqual(len(self.parameters), 0)
        self.assertEqual(len(self.manager.constraint_widgets), 0)

    def test_get_parameter_name_from_ui(self):
        """Test getting parameter name from UI widget."""
        self.manager.add_new_parameter_row()

        # Set name
        name_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        name_widget.setText("  test_name  ")  # Include whitespace to test trimming

        # Get name
        name = self.manager._get_parameter_name_from_ui(0)
        self.assertEqual(name, "test_name")

    def test_get_parameter_name_from_ui_empty(self):
        """Test getting empty parameter name from UI widget."""
        self.manager.add_new_parameter_row()

        # Clear name
        name_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        name_widget.setText("")

        # Get name
        name = self.manager._get_parameter_name_from_ui(0)
        self.assertEqual(name, "")

    def test_get_parameter_type_from_ui_placeholder(self):
        """Test getting parameter type when placeholder is selected."""
        self.manager.add_new_parameter_row()

        # Type combo should start with placeholder selected (index 0)
        param_type = self.manager._get_parameter_type_from_ui(0)
        self.assertIsNone(param_type)

    def test_get_parameter_type_from_ui_valid_selection(self):
        """Test getting parameter type with valid selection."""
        self.manager.add_new_parameter_row()

        # Select first real parameter type (index 1)
        type_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_TYPE)
        type_widget.setCurrentIndex(1)

        param_type = self.manager._get_parameter_type_from_ui(0)
        self.assertIsNotNone(param_type)

        # Handle both enum instances and string values that Qt might return
        if isinstance(param_type, str):
            # If it's a string, verify it's a valid ParameterType value
            valid_values = [pt.value for pt in ParameterType]
            self.assertIn(param_type, valid_values, f"'{param_type}' is not a valid ParameterType value")
        else:
            self.assertIsInstance(param_type, ParameterType)

    # Tests that require mocking setCellWidget to avoid Qt issues
    @patch("app.screens.campaign.setup.components.parameter_managers.create_constraint_widget")
    def test_update_parameter_type_with_mock(self, mock_create_widget):
        """Test updating parameter type with mocked constraint widget creation."""
        mock_create_widget.return_value = self.constraint_widget_mock

        self.manager.add_new_parameter_row()

        # Set a name first
        name_widget = self.manager.parameters_table.cellWidget(0, self.manager.COLUMN_NAME)
        name_widget.setText("test_param")

        # Mock the problematic setCellWidget call
        with patch.object(self.manager.parameters_table, "setCellWidget"):
            self.manager.update_parameter_type(0, ParameterType.CONTINUOUS_NUMERICAL)

        # Check parameter was created
        self.assertIsNotNone(self.parameters[0])
        self.assertEqual(self.parameters[0].parameter_type, ParameterType.CONTINUOUS_NUMERICAL)
        self.assertEqual(self.parameters[0].name, "test_param")

        # Check constraint widget was created
        mock_create_widget.assert_called_once()
        self.assertEqual(self.manager.constraint_widgets[0], self.constraint_widget_mock)

    @patch("app.screens.campaign.setup.components.parameter_managers.create_constraint_widget")
    def test_validate_all_widgets_duplicate_names_with_mock(self, mock_create_widget):
        """Test validation with duplicate parameter names using mocked widgets."""
        mock_create_widget.return_value = self.constraint_widget_mock

        # Add two parameters
        self.manager.add_new_parameter_row()
        self.manager.add_new_parameter_row()

        # Manually set up parameters with duplicate names to avoid setCellWidget issues
        for row in range(2):
            name_widget = self.manager.parameters_table.cellWidget(row, self.manager.COLUMN_NAME)
            name_widget.setText("duplicate_name")

            # Create mock parameters directly
            mock_param = Mock()
            mock_param.name = "duplicate_name"
            mock_param.parameter_type = ParameterType.CONTINUOUS_NUMERICAL
            self.parameters[row] = mock_param
            self.manager.constraint_widgets[row] = self.constraint_widget_mock

        is_valid, error_message = self.manager.validate_all_widgets()

        self.assertFalse(is_valid)
        self.assertEqual(error_message, self.manager.DUPLICATE_NAMES_MESSAGE)

    @patch("app.screens.campaign.setup.components.parameter_managers.create_constraint_widget")
    def test_load_parameters_to_table_with_mock(self, mock_create_widget):
        """Test loading existing parameters into table with mocked widgets."""
        mock_create_widget.return_value = self.constraint_widget_mock

        # Create mock parameters
        mock_param1 = Mock()
        mock_param1.name = "param1"
        mock_param1.parameter_type = ParameterType.CONTINUOUS_NUMERICAL

        mock_param2 = Mock()
        mock_param2.name = "param2"
        mock_param2.parameter_type = ParameterType.CATEGORICAL

        parameters_to_load = [mock_param1, mock_param2]

        # Mock setCellWidget to avoid Qt widget issues
        with patch.object(self.manager.parameters_table, "setCellWidget"):
            self.manager.load_parameters_to_table(parameters_to_load)

        # Check table structure
        self.assertEqual(self.manager.parameters_table.rowCount(), 2)
        self.assertEqual(len(self.parameters), 2)
        self.assertEqual(len(self.manager.constraint_widgets), 2)

        # Check that parameters are loaded correctly
        self.assertEqual(self.parameters[0], mock_param1)
        self.assertEqual(self.parameters[1], mock_param2)


if __name__ == "__main__":
    unittest.main()
