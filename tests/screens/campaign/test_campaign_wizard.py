import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QWidget

from app.screens.campaign.campaign_wizard import CampaignWizard


# Create a mock class that inherits from QWidget and has mock methods
class MockStepWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_data = MagicMock()
        self.validate = MagicMock()
        self.save_data = MagicMock()
        self.reset = MagicMock()


class TestCampaignWizard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        # Mock the step widgets to isolate the wizard's logic
        self.mock_step1 = MockStepWidget()
        self.mock_step2 = MockStepWidget()
        self.mock_step3 = MockStepWidget()

        # Patch the step classes
        patcher1 = patch(
            "app.screens.campaign.campaign_wizard.CampaignInfoStep",
            return_value=self.mock_step1,
        )
        patcher2 = patch(
            "app.screens.campaign.campaign_wizard.ParametersStep",
            return_value=self.mock_step2,
        )
        patcher3 = patch(
            "app.screens.campaign.campaign_wizard.DataImportStep",
            return_value=self.mock_step3,
        )

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)

        patcher1.start()
        patcher2.start()
        patcher3.start()

        self.wizard = CampaignWizard()

    def test_initial_state(self):
        self.assertEqual(self.wizard.current_step, 0)
        self.assertEqual(self.wizard.stacked_widget.currentIndex(), 0)
        self.assertEqual(self.wizard.next_button.text(), "Next →")

    def test_go_next_successful(self):
        # Step 1 is valid
        self.mock_step1.validate.return_value = True
        self.wizard._go_next()

        self.assertEqual(self.wizard.current_step, 1)
        self.mock_step1.save_data.assert_called_once()
        self.assertEqual(self.wizard.stacked_widget.currentIndex(), 1)

    def test_go_next_validation_fails(self):
        # Step 1 is invalid
        self.mock_step1.validate.return_value = False
        self.wizard._go_next()

        self.assertEqual(self.wizard.current_step, 0)
        self.mock_step1.save_data.assert_not_called()
        self.assertEqual(self.wizard.stacked_widget.currentIndex(), 0)

    def test_go_back(self):
        # Go to step 2
        self.mock_step1.validate.return_value = True
        self.wizard._go_next()
        self.assertEqual(self.wizard.current_step, 1)

        # Go back to step 1
        self.wizard._go_back()
        self.assertEqual(self.wizard.current_step, 0)
        self.assertEqual(self.wizard.stacked_widget.currentIndex(), 0)

    def test_go_back_to_start_screen(self):
        mock_slot = MagicMock()
        self.wizard.back_to_start_requested.connect(mock_slot)
        self.wizard._go_back()
        mock_slot.assert_called_once()

    def test_create_campaign(self):
        # Go to the final step
        self.wizard.current_step = self.wizard.total_steps - 1
        self.wizard._update_step_display()
        self.assertEqual(self.wizard.next_button.text(), "Create Campaign")

        # Final step is valid
        self.mock_step3.validate.return_value = True

        mock_slot = MagicMock()
        self.wizard.campaign_created.connect(mock_slot)
        self.wizard._go_next()
        self.mock_step3.save_data.assert_called_once()
        mock_slot.assert_called_once_with(self.wizard.campaign)

    def test_reset_wizard(self):
        # Change some data and move to the next step
        self.wizard.campaign.name = "Test Campaign"
        self.wizard.current_step = 1
        self.wizard.reset_wizard()

        self.assertEqual(self.wizard.current_step, 0)
        self.assertEqual(self.wizard.campaign.name, "")
        self.mock_step1.reset.assert_called_once()
        self.mock_step2.reset.assert_called_once()
        self.mock_step3.reset.assert_called_once()


if __name__ == "__main__":
    unittest.main()
