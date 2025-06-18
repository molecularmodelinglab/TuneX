"""
CSV Template Generator for experimental data import.

This module generates CSV templates based on configured parameters from Step 2.
The template includes:
- Column headers matching parameter names
- Example rows with valid sample data
- Proper formatting for different parameter types

The generator follows the existing architecture pattern by working with
BaseParameter objects and their constraints.
"""

import csv
from typing import List, Dict, Any, Union, Optional

from app.models.parameters.base import BaseParameter


class CSVTemplateGenerator:
    """
    Generates CSV templates based on configured parameters.

    This class analyzes the parameters configured in Step 2 and creates
    a CSV file with appropriate column headers and example data that
    matches the parameter constraints.
    """

    # Template constants
    NUM_EXAMPLE_ROWS = 3
    TARGET_COLUMN_NAME = "target_value"
    TARGET_EXAMPLE_VALUES = [0.85, 0.92, 0.78]

    def __init__(
        self,
        parameters: List[BaseParameter],
        campaign_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the template generator.

        Args:
            parameters: List of configured parameters from Step 2
            campaign_data: Campaign configuration data containing target information
        """
        self.parameters = parameters
        self.campaign_data = campaign_data or {}

    def generate_template(self, file_path: str) -> bool:
        """
        Generate CSV template and save to specified file path.

        Args:
            file_path: Path where to save the CSV template

        Returns:
            bool: True if template was generated successfully, False otherwise
        """
        try:
            # Generate template data
            headers = self._generate_headers()
            rows = self._generate_example_rows()

            # Write to CSV file
            self._write_csv_file(file_path, headers, rows)

            print(f"CSV template generated successfully: {file_path}")
            print(
                f"Template includes {len(headers)} columns and {len(rows)} example rows"
            )

            return True

        except Exception as e:
            print(f"Error generating CSV template: {e}")
            return False

    def _generate_headers(self) -> List[str]:
        """
        Generate column headers from parameter names.

        Returns:
            List of column header names
        """
        headers = []

        for parameter in self.parameters:
            headers.append(parameter.name)

        # Use target name from campaign data if available, otherwise use default
        target_name = self.TARGET_COLUMN_NAME
        if self.campaign_data and "target" in self.campaign_data:
            target_name = self.campaign_data["target"].get(
                "name", self.TARGET_COLUMN_NAME
            )

        headers.append(target_name)

        return headers

    def _generate_example_rows(self) -> List[List[str]]:
        """
        Generate example data rows that respect parameter constraints.

        Returns:
            List of rows, where each row is a list of string values
        """
        rows = []

        for row_index in range(self.NUM_EXAMPLE_ROWS):
            row = []

            # Generate example value for each parameter
            for parameter in self.parameters:
                example_value = self._generate_example_value(parameter)
                row.append(str(example_value))

            # Add target value
            target_value = self.TARGET_EXAMPLE_VALUES[
                row_index % len(self.TARGET_EXAMPLE_VALUES)
            ]
            row.append(str(target_value))

            rows.append(row)

        return rows

    def _generate_example_value(
        self, parameter: BaseParameter
    ) -> Union[str, float, int]:
        """
        Generate a valid example value for a specific parameter.

        Args:
            parameter: The parameter to generate a value for

        Returns:
            Random valid value that respects the parameter's constraints
        """
        return parameter.get_random_valid_value()

    def _write_csv_file(
        self, file_path: str, headers: List[str], rows: List[List[str]]
    ) -> None:
        """
        Write the CSV file with headers and data rows.

        Args:
            file_path: Path to write the CSV file
            headers: Column headers
            rows: Data rows
        """
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(headers)

            # Write data rows
            for row in rows:
                writer.writerow(row)

    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about the template that would be generated.

        Returns:
            Dictionary with template metadata
        """
        headers = self._generate_headers()

        return {
            "num_parameters": len(self.parameters),
            "num_columns": len(headers),
            "column_names": headers,
            "num_example_rows": self.NUM_EXAMPLE_ROWS,
            "parameter_types": [
                param.parameter_type.value for param in self.parameters
            ],
        }
