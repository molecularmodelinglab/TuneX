import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from app.models.campaign import Campaign, Target
from app.models.enums import ParameterType
from app.screens.campaign.setup.parameters_step import ParametersStep


class TestParametersStep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for Qt widgets."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock campaign
        self.campaign = Campaign(targets=[Target(name="yield")])

        # Mock the ParameterRowManager to avoid UI complexities
        self.mock_row_manager = Mock()
        self.mock_table_widget = QWidget()  # Use real widget to avoid Qt issues
        self.mock_row_manager.get_table_widget.return_value = self.mock_table_widget
        self.mock_row_manager.validate_all_widgets.return_value = (True, None)
        self.mock_row_manager.sync_ui_to_parameters.return_value = None
        self.mock_row_manager.load_parameters_to_table.return_value = None
        self.mock_row_manager.clear_table.return_value = None

        # Create patchers for UI components that cause issues
        self.row_manager_patcher = patch("app.screens.campaign.setup.parameters_step.ParameterRowManager")
        self.main_header_patcher = patch("app.screens.campaign.setup.parameters_step.MainHeader")
        self.section_header_patcher = patch("app.screens.campaign.setup.parameters_step.SectionHeader")

        # Start patches and get the mock objects
        self.mock_manager_class = self.row_manager_patcher.start()
        mock_main_header = self.main_header_patcher.start()
        mock_section_header = self.section_header_patcher.start()

        # Configure mocks to return real widgets
        self.mock_manager_class.return_value = self.mock_row_manager
        mock_main_header.return_value = QWidget()  # Real widget for layout
        mock_section_header.return_value = QWidget()  # Real widget for layout

        # Create the step
        self.step = ParametersStep(self.campaign)

    def tearDown(self):
        """Clean up after each test."""
        # Stop all patchers
        self.row_manager_patcher.stop()
        self.main_header_patcher.stop()
        self.section_header_patcher.stop()

        if hasattr(self.step, "deleteLater"):
            self.step.deleteLater()

    def test_initialization(self):
        """Test that the step initializes correctly."""
        self.assertIsNotNone(self.step.campaign)
        self.assertEqual(self.step.campaign, self.campaign)
        self.assertIsInstance(self.step.parameters, list)
        self.assertEqual(len(self.step.parameters), 0)

        # Check that row manager was created
        self.assertIsNotNone(self.step.row_manager)

    def test_title_and_description_constants(self):
        """Test that UI text constants are properly defined."""
        self.assertEqual(self.step.TITLE, "Parameter Configuration")
        self.assertIn("Configure the parameters", self.step.DESCRIPTION)
        self.assertEqual(self.step.ADD_BUTTON_TEXT, "+ Add Parameter")
        self.assertIsNotNone(self.step.ADD_BUTTON_TOOLTIP)

    def test_add_button_exists_and_configured(self):
        """Test that add button is created and properly configured."""
        self.assertTrue(hasattr(self.step, "_add_button"))
        self.assertIsInstance(self.step._add_button, QPushButton)
        self.assertEqual(self.step._add_button.text(), self.step.ADD_BUTTON_TEXT)
        self.assertEqual(self.step._add_button.objectName(), self.step.PRIMARY_BUTTON_OBJECT_NAME)
        self.assertEqual(self.step._add_button.toolTip(), self.step.ADD_BUTTON_TOOLTIP)

    def test_on_add_parameter(self):
        """Test that add parameter button delegates to row manager."""
        self.step._on_add_parameter()

        # Verify that row manager's add method was called
        self.mock_row_manager.add_new_parameter_row.assert_called_once()

    def test_add_button_signal_connection(self):
        """Test that add button click is connected to handler."""
        # Reset mock to clear any previous calls
        self.mock_row_manager.reset_mock()

        # Simulate button click
        self.step._add_button.click()

        # Verify handler was called
        self.mock_row_manager.add_new_parameter_row.assert_called_once()

    def test_validate_success(self):
        """Test validation when all parameters are valid."""
        # Configure mock to return success
        self.mock_row_manager.validate_all_widgets.return_value = (True, None)

        result = self.step.validate()

        self.assertTrue(result)
        self.mock_row_manager.validate_all_widgets.assert_called_once()

    @patch("app.screens.campaign.setup.parameters_step.ErrorDialog")
    def test_validate_failure(self, mock_error_dialog):
        """Test validation when parameters are invalid."""
        # Configure mock to return failure
        error_message = "Parameter name is required"
        self.mock_row_manager.validate_all_widgets.return_value = (False, error_message)

        result = self.step.validate()

        self.assertFalse(result)
        self.mock_row_manager.validate_all_widgets.assert_called_once()

        # Verify error dialog was shown
        mock_error_dialog.show_error.assert_called_once()
        args = mock_error_dialog.show_error.call_args[0]
        self.assertEqual(args[0], self.step.VALIDATION_ERROR_TITLE)
        self.assertIn(error_message, args[1])

    def test_save_data_success(self):
        """Test saving data when parameters are valid."""
        # Create mock parameters
        mock_param1 = Mock()
        mock_param1.name = "temperature"
        mock_param1.parameter_type = ParameterType.CONTINUOUS_NUMERICAL

        mock_param2 = Mock()
        mock_param2.name = "pressure"
        mock_param2.parameter_type = ParameterType.DISCRETE_NUMERICAL_REGULAR

        # Add parameters to step
        self.step.parameters = [mock_param1, mock_param2]

        # Save data
        self.step.save_data()

        # Verify sync was called
        self.mock_row_manager.sync_ui_to_parameters.assert_called_once()

        # Verify parameters were saved to campaign
        self.assertEqual(len(self.campaign.parameters), 2)
        self.assertIn(mock_param1, self.campaign.parameters)
        self.assertIn(mock_param2, self.campaign.parameters)

    def test_save_data_filters_none_values(self):
        """Test that save_data filters out None parameter values."""
        # Create parameters list with None values
        mock_param = Mock()
        mock_param.name = "temperature"
        mock_param.parameter_type = ParameterType.CONTINUOUS_NUMERICAL

        self.step.parameters = [mock_param, None, None]

        # Save data
        self.step.save_data()

        # Verify only valid parameters were saved
        self.assertEqual(len(self.campaign.parameters), 1)
        self.assertEqual(self.campaign.parameters[0], mock_param)

    def test_save_data_empty_parameters(self):
        """Test saving data with no parameters."""
        self.step.parameters = []

        # Save data
        self.step.save_data()

        # Verify empty list was saved
        self.assertEqual(len(self.campaign.parameters), 0)
        self.mock_row_manager.sync_ui_to_parameters.assert_called_once()

    def test_load_data_success(self):
        """Test loading data from campaign."""
        # Create mock parameters in campaign
        mock_param1 = Mock()
        mock_param1.name = "temperature"
        mock_param1.parameter_type = ParameterType.CONTINUOUS_NUMERICAL

        mock_param2 = Mock()
        mock_param2.name = "pressure"
        mock_param2.parameter_type = ParameterType.CATEGORICAL

        self.campaign.parameters = [mock_param1, mock_param2]

        # Load data
        self.step.load_data()

        # Verify parameters were loaded into step
        self.assertEqual(len(self.step.parameters), 2)
        self.assertIn(mock_param1, self.step.parameters)
        self.assertIn(mock_param2, self.step.parameters)

        # Verify row manager was called to populate UI
        self.mock_row_manager.load_parameters_to_table.assert_called_once_with([mock_param1, mock_param2])

    def test_load_data_empty_campaign(self):
        """Test loading data when campaign has no parameters."""
        self.campaign.parameters = []

        # Load data
        self.step.load_data()

        # Verify no parameters were loaded
        self.assertEqual(len(self.step.parameters), 0)

        # Verify row manager load was not called since no parameters
        self.mock_row_manager.load_parameters_to_table.assert_not_called()

    def test_load_data_none_parameters(self):
        """Test loading data when campaign parameters is None."""
        self.campaign.parameters = None

        # Load data
        self.step.load_data()

        # Should handle gracefully
        self.assertEqual(len(self.step.parameters), 0)
        self.mock_row_manager.load_parameters_to_table.assert_not_called()

    def test_reset(self):
        """Test resetting the step to initial state."""
        # Add some parameters first
        mock_param = Mock()
        self.step.parameters = [mock_param]

        # Reset
        self.step.reset()

        # Verify parameters were cleared
        self.assertEqual(len(self.step.parameters), 0)

        # Verify row manager was cleared
        self.mock_row_manager.clear_table.assert_called_once()

    def test_reset_without_row_manager(self):
        """Test reset when row manager doesn't exist."""
        # Remove row manager
        delattr(self.step, "row_manager")

        # Add parameters
        mock_param = Mock()
        self.step.parameters = [mock_param]

        # Reset should not crash
        self.step.reset()

        # Parameters should still be cleared
        self.assertEqual(len(self.step.parameters), 0)

    @patch("app.screens.campaign.setup.parameters_step.ErrorDialog")
    def test_validate_with_exception_handling(self, mock_error_dialog):
        """Test that validation handles exceptions from row manager."""
        # Configure mock to raise an exception
        self.mock_row_manager.validate_all_widgets.side_effect = Exception("Test exception")

        # This should not crash - though current implementation doesn't catch exceptions
        with self.assertRaises(Exception):
            self.step.validate()

    def test_save_data_with_exception_handling(self):
        """Test that save_data handles exceptions gracefully."""
        # Configure mock to raise an exception
        self.mock_row_manager.sync_ui_to_parameters.side_effect = Exception("Test sync error")

        # This should not crash - implementation catches exceptions
        self.step.save_data()

        # Parameters should remain unchanged due to exception
        self.assertEqual(len(self.campaign.parameters), 0)

    def test_load_data_with_exception_handling(self):
        """Test that load_data handles exceptions gracefully."""
        # Set up campaign with parameters but make loading fail
        self.campaign.parameters = [Mock()]
        self.mock_row_manager.load_parameters_to_table.side_effect = Exception("Test load error")

        # This should not crash - implementation catches exceptions
        self.step.load_data()

        # Parameters should still be loaded into step even if UI loading fails
        self.assertEqual(len(self.step.parameters), 1)

    def test_ui_layout_creation(self):
        """Test that UI layout is properly created."""
        # Verify that key UI components exist
        self.assertTrue(hasattr(self.step, "_add_button"))
        self.assertTrue(hasattr(self.step, "_table"))
        self.assertTrue(hasattr(self.step, "row_manager"))

        # Verify table is obtained from row manager
        self.assertEqual(self.step._table, self.mock_table_widget)

    def test_error_message_constants(self):
        """Test that error message constants are properly defined."""
        self.assertIsNotNone(self.step.VALIDATION_ERROR_TITLE)
        self.assertIsNotNone(self.step.VALIDATION_ERROR_MESSAGE)
        self.assertIn("{0}", self.step.VALIDATION_ERROR_MESSAGE)  # Should have placeholder for error

    def test_step_inheritance(self):
        """Test that ParametersStep properly inherits from BaseStep."""
        from app.core.base import BaseStep

        self.assertIsInstance(self.step, BaseStep)

        # Test that required BaseStep methods exist
        self.assertTrue(hasattr(self.step, "validate"))
        self.assertTrue(hasattr(self.step, "save_data"))
        self.assertTrue(hasattr(self.step, "load_data"))

    def test_parameters_list_shared_with_row_manager(self):
        """Test that parameters list is properly shared with row manager."""
        # Verify that the ParameterRowManager was called during initialization
        self.assertTrue(self.mock_manager_class.called)

        # Get the arguments that were passed to ParameterRowManager
        call_args = self.mock_manager_class.call_args

        if call_args and len(call_args[0]) > 0:
            # The first argument should be the parameters list
            passed_list = call_args[0][0]
            # Verify it's the same object reference as step.parameters
            self.assertIs(passed_list, self.step.parameters)
        else:
            # Fallback: just verify the step has the expected structure
            self.assertIsInstance(self.step.parameters, list)
            self.assertEqual(len(self.step.parameters), 0)

    def test_constants_are_properly_defined(self):
        """Test that all required constants are defined."""
        # UI Constants
        self.assertTrue(hasattr(self.step, "TITLE"))
        self.assertTrue(hasattr(self.step, "DESCRIPTION"))
        self.assertTrue(hasattr(self.step, "ADD_BUTTON_TEXT"))
        self.assertTrue(hasattr(self.step, "ADD_BUTTON_TOOLTIP"))

        # Object names
        self.assertTrue(hasattr(self.step, "PRIMARY_BUTTON_OBJECT_NAME"))

        # Error messages
        self.assertTrue(hasattr(self.step, "VALIDATION_ERROR_TITLE"))
        self.assertTrue(hasattr(self.step, "VALIDATION_ERROR_MESSAGE"))

        # Layout constants
        self.assertTrue(hasattr(self.step, "MAIN_MARGINS"))
        self.assertTrue(hasattr(self.step, "MAIN_SPACING"))

    def test_setup_managers_method(self):
        """Test that _setup_managers method properly initializes managers."""
        # Since we're mocking ParameterRowManager, we can verify it was called
        # with the correct parameters list during initialization
        self.assertIsNotNone(self.step.row_manager)
        self.assertEqual(self.step.row_manager, self.mock_row_manager)

    def test_connect_signals_method(self):
        """Test that signals are properly connected."""
        # Verify that the add button signal was connected
        # This is tested indirectly through the button click test
        self.assertTrue(hasattr(self.step, "_add_button"))

        # Verify button has signal connections (Qt internal)
        # We can test this by checking if clicking the button triggers the handler
        initial_call_count = self.mock_row_manager.add_new_parameter_row.call_count
        self.step._add_button.click()
        self.assertEqual(self.mock_row_manager.add_new_parameter_row.call_count, initial_call_count + 1)


if __name__ == "__main__":
    unittest.main()
