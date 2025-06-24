import os
import shutil
import unittest
from typing import List

from app.models.parameters.base import BaseParameter
from app.models.parameters.types import (
    Categorical,
    ContinuousNumerical,
    DiscreteNumericalIrregular,
    DiscreteNumericalRegular,
    Fixed,
    Substance,
)
from app.screens.campaign.steps.components.csv_data_importer import (
    CSVDataImporter,
)


class TestCSVDataImporter(unittest.TestCase):
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
        self.campaign_data = {"target": {"name": "yield"}}

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_csv(self, filename: str, lines: List[str]):
        path = os.path.join(self.test_dir, filename)
        with open(path, "w", newline="") as f:
            f.write("\n".join(lines))
        return path

    def test_import_valid_csv(self):
        csv_path = self._create_csv(
            "valid.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield",
                "10.0,7.0,water,1,Pt,CCO,85.5",
                "25.0,5.5,ethanol,2,Pt,CCCCO,92.1",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(data), 2)
        self.assertEqual(result.total_rows, 2)
        self.assertEqual(result.valid_rows, 2)
        self.assertEqual(data[0]["temp"], 10.0)
        self.assertEqual(data[1]["solvent"], "ethanol")

    def test_import_missing_columns(self):
        csv_path = self._create_csv("missing_col.csv", ["temp,yield", "10.0,85.5"])
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertFalse(result.is_valid)
        self.assertEqual(len(data), 0)
        self.assertIn("Missing required column: 'ph'", result.errors)
        self.assertIn("Missing required column: 'solvent'", result.errors)

    def test_import_extra_columns(self):
        csv_path = self._create_csv(
            "extra_col.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield,extra_param",
                "10.0,7.0,water,1,Pt,CCO,85.5,ignored",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("Extra column found: 'extra_param' (will be ignored)", result.warnings)
        self.assertEqual(len(data), 1)

    def test_import_duplicate_columns(self):
        csv_path = self._create_csv(
            "duplicate_col.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield,temp",
                "10.0,7.0,water,1,Pt,CCO,85.5,20.0",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)
        self.assertFalse(result.is_valid)
        self.assertIn("Duplicate column header: 'temp'", result.errors)

    def test_import_invalid_data_type(self):
        csv_path = self._create_csv(
            "invalid_type.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield",
                "abc,7.0,water,1,Pt,CCO,85.5",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertFalse(result.is_valid)
        self.assertEqual(len(data), 0)
        self.assertIn(1, result.row_errors)
        self.assertIn("Cannot convert 'abc' for parameter 'temp'", result.row_errors[1][0])

    def test_import_out_of_range_value(self):
        csv_path = self._create_csv(
            "out_of_range.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield",
                "110.0,7.0,water,1,Pt,CCO,85.5",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertFalse(result.is_valid)
        self.assertEqual(len(data), 0)
        self.assertIn(1, result.row_errors)
        self.assertIn("Value 110.0 is outside range [0.0, 100.0]", result.row_errors[1][0])

    def test_import_invalid_categorical_value(self):
        csv_path = self._create_csv(
            "invalid_category.csv",
            [
                "temp,ph,solvent,pressure,catalyst,reagent,yield",
                "10.0,7.0,acetone,1,Pt,CCO,85.5",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertFalse(result.is_valid)
        self.assertEqual(len(data), 0)
        self.assertIn(1, result.row_errors)
        self.assertIn("not in allowed categories", result.row_errors[1][0])

    def test_import_file_not_found(self):
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv("non_existent_file.csv")

        self.assertFalse(result.is_valid)
        self.assertEqual(len(data), 0)
        self.assertIn("Failed to import CSV", result.errors[0])

    def test_import_semicolon_delimiter(self):
        csv_path = self._create_csv(
            "semicolon.csv",
            [
                "temp;ph;solvent;pressure;catalyst;reagent;yield",
                "10.0;7.0;water;1;Pt;CCO;85.5",
            ],
        )
        importer = CSVDataImporter(self.parameters, self.campaign_data)
        data, result = importer.import_csv(csv_path)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["temp"], 10.0)


if __name__ == "__main__":
    unittest.main()
