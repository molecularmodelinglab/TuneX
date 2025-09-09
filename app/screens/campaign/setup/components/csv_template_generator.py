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
import logging
from typing import Any, Dict, List, Union

from app.models.campaign import Campaign
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
        campaign: Campaign,
    ) -> None:
        """
        Initialize the template generator.

        Args:
            parameters: List of configured parameters from Step 2
            campaign: The campaign data model
        """
        self.parameters = parameters
        self.campaign = campaign
        self.logger = logging.getLogger(__name__)

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

            self.logger.info(f"CSV template generated successfully: {file_path}")
            self.logger.info(f"Template includes {len(headers)} columns and {len(rows)} example rows")

            return True

        except Exception as e:
            self.logger.error(f"Error generating CSV template: {e!r}")
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
        if self.campaign and self.campaign.targets:
            for target in self.campaign.targets[:]:
                headers.append(target.name)
        else:
            headers.append(self.TARGET_COLUMN_NAME)

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

            # Add target values
            if self.campaign and self.campaign.targets:
                for _ in self.campaign.targets:
                    target_value = self.TARGET_EXAMPLE_VALUES[row_index % len(self.TARGET_EXAMPLE_VALUES)]
                    row.append(str(target_value))
            else:
                # If no targets, use default target value
                row.append(str(self.TARGET_EXAMPLE_VALUES[row_index % len(self.TARGET_EXAMPLE_VALUES)]))

            rows.append(row)

        return rows

    def _generate_example_value(self, parameter: BaseParameter) -> Union[str, float, int]:
        """
        Generate a valid example value for a specific parameter.

        Args:
            parameter: The parameter to generate a value for

        Returns:
            Random valid value that respects the parameter's constraints
        """
        return parameter.get_random_valid_value()

    def _write_csv_file(self, file_path: str, headers: List[str], rows: List[List[str]]) -> None:
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
            "parameter_types": [param.parameter_type.value for param in self.parameters],
        }
