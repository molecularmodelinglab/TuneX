import csv
import os
import shutil
import unittest
from typing import List

from app.models.campaign import Campaign, Target
from app.models.parameters.base import BaseParameter
from app.models.parameters.types import (
    Categorical,
    ContinuousNumerical,
    DiscreteNumericalIrregular,
    DiscreteNumericalRegular,
    Fixed,
    Substance,
)
from app.screens.campaign.steps.components.csv_template_generator import (
    CSVTemplateGenerator,
)


class TestCSVTemplateGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_data"
        os.makedirs(self.test_dir, exist_ok=True)
        self.parameters: List[BaseParameter] = [
            DiscreteNumericalRegular("temp", min_val=0.0, max_val=100.0, step=5.0),
            ContinuousNumerical("ph", min_val=0.0, max_val=14.0),
            Categorical("solvent", values=["water", "ethanol", "methanol"]),
            DiscreteNumericalIrregular("pressure", values=[1, 2, 5]),
            Fixed("catalyst", value="Pt"),
            Substance("reagent", smiles=["CCO", "CCCCO"]),
        ]
        self.campaign = Campaign(target=Target(name="yield"))

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_template_file_creation(self):
        generator = CSVTemplateGenerator(self.parameters, self.campaign)
        file_path = os.path.join(self.test_dir, "template.csv")
        success = generator.generate_template(file_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))

    def test_generate_template_headers(self):
        generator = CSVTemplateGenerator(self.parameters, self.campaign)
        file_path = os.path.join(self.test_dir, "template.csv")
        generator.generate_template(file_path)

        with open(file_path, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = [p.name for p in self.parameters] + ["yield"]
            self.assertEqual(headers, expected_headers)

    def test_generate_template_row_count(self):
        generator = CSVTemplateGenerator(self.parameters, self.campaign)
        file_path = os.path.join(self.test_dir, "template.csv")
        generator.generate_template(file_path)

        with open(file_path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            rows = list(reader)
            self.assertEqual(len(rows), generator.NUM_EXAMPLE_ROWS)

    def test_generate_template_data_validation(self):
        generator = CSVTemplateGenerator(self.parameters, self.campaign)
        file_path = os.path.join(self.test_dir, "template.csv")
        generator.generate_template(file_path)

        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for param in self.parameters:
                    value_str = row[param.name]
                    is_valid, _, _ = self._validate_value(param, value_str)
                    self.assertTrue(
                        is_valid,
                        f"Value '{value_str}' for parameter '{param.name}' is not valid.",
                    )

    def _validate_value(self, param, value_str):
        try:
            converted_value = param.convert_value(value_str)
            is_valid, msg = param.validate_value(converted_value)
            return is_valid, converted_value, msg
        except (ValueError, TypeError) as e:
            return False, None, str(e)


if __name__ == "__main__":
    unittest.main()
