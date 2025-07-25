import unittest
import uuid
from datetime import datetime

from app.models.campaign import Campaign, Target
from app.models.parameters.types import ContinuousNumerical, Fixed


class TestCampaignModel(unittest.TestCase):
    def test_campaign_default_initialization(self):
        """Test that a Campaign object can be created with default values."""
        campaign = Campaign()
        self.assertIsInstance(campaign.id, str)
        self.assertTrue(len(campaign.id) > 0)
        self.assertEqual(campaign.name, "")
        self.assertEqual(campaign.description, "")
        self.assertEqual(campaign.targets, [])
        self.assertEqual(campaign.parameters, [])
        self.assertEqual(campaign.initial_dataset, [])
        self.assertIsInstance(campaign.created_at, datetime)
        self.assertIsInstance(campaign.updated_at, datetime)

    def test_get_parameter_data_serialization(self):
        """Test serialization of parameters."""
        parameters = [
            ContinuousNumerical(name="temp", min_val=0, max_val=100),
            Fixed(name="catalyst", value="Pt"),
        ]
        campaign = Campaign(parameters=parameters)
        parameter_data = campaign.get_parameter_data()

        self.assertEqual(len(parameter_data), 2)
        self.assertEqual(parameter_data[0]["name"], "temp")
        self.assertEqual(parameter_data[0]["type"], "continuous_numerical")
        self.assertEqual(parameter_data[1]["name"], "catalyst")
        self.assertEqual(parameter_data[1]["type"], "fixed")

    def test_from_dict_deserialization(self):
        """Test deserialization from a dictionary."""
        test_id = str(uuid.uuid4())
        test_time_iso = "2024-01-01T12:00:00"

        campaign_data = {
            "id": test_id,
            "name": "Test Campaign",
            "description": "A test campaign.",
            "targets": [{"name": "yield", "mode": "Max"}],
            "parameters": [
                {
                    "name": "temp",
                    "type": "continuous_numerical",
                    "min_val": 0,
                    "max_val": 100,
                }
            ],
            "initial_dataset": [{"temp": 50, "yield": 0.85}],
            "created_at": test_time_iso,
            "updated_at": test_time_iso,
        }

        campaign = Campaign.from_dict(campaign_data)

        self.assertEqual(campaign.id, test_id)
        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.description, "A test campaign.")
        self.assertEqual(campaign.targets[0].name, "yield")
        self.assertEqual(campaign.targets[0].mode, "Max")
        self.assertEqual(len(campaign.parameters), 1)
        self.assertIsInstance(campaign.parameters[0], ContinuousNumerical)
        self.assertEqual(campaign.parameters[0].name, "temp")
        self.assertEqual(len(campaign.initial_dataset), 1)
        self.assertIsInstance(campaign.created_at, datetime)
        self.assertIsInstance(campaign.updated_at, datetime)

    def test_target_model(self):
        """Test the Target model functionality."""
        # Test default initialization
        target = Target()
        self.assertEqual(target.name, "")
        self.assertEqual(target.mode, "Max")

        # Test with values
        target = Target(name="yield", mode="Min")
        self.assertEqual(target.name, "yield")
        self.assertEqual(target.mode, "Min")


if __name__ == "__main__":
    unittest.main()
