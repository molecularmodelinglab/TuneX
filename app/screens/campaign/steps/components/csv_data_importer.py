"""
CSV Data Importer with validation against parameter constraints.

This module handles importing CSV files and validating the data against
the configured parameters from Step 2. It provides detailed error reporting
and data validation using the existing parameter validation methods.
"""

import csv
from typing import Any, Dict, List, Optional, Tuple

from app.models.parameters.base import BaseParameter


class CSVValidationResult:
    """Container for CSV validation results with detailed error information."""

    def __init__(self) -> None:
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.missing_columns: List[str] = []
        self.extra_columns: List[str] = []
        self.row_errors: Dict[int, List[str]] = {}
        self.total_rows: int = 0
        self.valid_rows: int = 0

    def add_error(self, message: str) -> None:
        """Add a general error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_row_error(self, row_index: int, message: str) -> None:
        """Add an error for a specific row."""
        if row_index not in self.row_errors:
            self.row_errors[row_index] = []
        self.row_errors[row_index].append(message)
        self.is_valid = False

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        if self.is_valid:
            return f"Validation passed: {self.valid_rows}/{self.total_rows} rows valid"

        error_count = len(self.errors) + len(self.row_errors)
        return f"Validation failed: {error_count} errors found"

    def get_error_for_row(self, row_index: int) -> Optional[str]:
        """
        Get error message for specific row, or None if no error.

        TODO: Implement actual error lookup logic when CSVValidationResult
        structure is finalized.

        Args:
            row_index: Zero-based row index

        Returns:
            Error message string or None if no error for this row
        """
        # Not implemented
        return None


class CSVDataImporter:
    """
    Imports and validates CSV data against configured parameters.

    This class handles the complete workflow of importing experimental data:
    1. Parse CSV file structure
    2. Validate column headers against parameters
    3. Validate data values using parameter constraints
    4. Provide detailed error reporting
    """

    TARGET_COLUMN_NAME = "target_value"

    def __init__(
        self,
        parameters: List[BaseParameter],
        campaign_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the CSV importer.

        Args:
            parameters: List of configured parameters from Step 2
        """
        self.parameters = parameters
        self.campaign_data = campaign_data or {}

    def import_csv(self, file_path: str) -> Tuple[List[Dict[str, Any]], CSVValidationResult]:
        """
        Import and validate CSV file.

        Args:
            file_path: Path to the CSV file to import

        Returns:
            Tuple of (imported_data, validation_result)
            - imported_data: List of dictionaries, one per row
            - validation_result: Detailed validation information
        """
        result = CSVValidationResult()
        imported_data: List[Dict[str, Any]] = []

        try:
            raw_data, headers = self._parse_csv_file(file_path)
            result.total_rows = len(raw_data)

            self._validate_columns(headers, result)

            if not result.is_valid:
                return imported_data, result

            imported_data = self._validate_data_rows(raw_data, headers, result)

            result.valid_rows = result.total_rows - len(result.row_errors)

            print(f"CSV import completed: {result.get_summary()}")

        except Exception as e:
            result.add_error(f"Failed to import CSV: {e}")

        return imported_data, result

    def _parse_csv_file(self, file_path: str) -> Tuple[List[List[str]], List[str]]:
        """
        Parse CSV file and extract headers and data rows.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (data_rows, headers)
        """
        data_rows = []
        headers = []

        with open(file_path, "r", encoding="utf-8") as csvfile:
            # Read a small sample to detect CSV dialect (delimiter, quoting, etc.)
            # We need to detect if CSV uses comma, semicolon, tab, etc. as separator
            sample = csvfile.read(1024)
            # Reset file pointer to beginning so we can read the full file
            # After read(1024), the pointer is at position 1024, but we need to start from 0
            csvfile.seek(0)

            # Use csv.Sniffer to detect delimiter
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
                reader = csv.reader(csvfile, dialect)
            except csv.Error:
                # Fallback to comma delimiter
                reader = csv.reader(csvfile)

            # Read headers (first row)
            headers = next(reader)
            headers = [header.strip() for header in headers]  # Clean whitespace

            for row_index, row in enumerate(reader):
                # Pad row with empty strings if it's shorter than headers
                while len(row) < len(headers):
                    row.append("")

                # Take only as many columns as headers
                row = row[: len(headers)]
                data_rows.append(row)

        return data_rows, headers

    def _validate_columns(self, headers: List[str], result: CSVValidationResult) -> None:
        """
        Validate that CSV headers match the configured parameters.

        Args:
            headers: List of column headers from CSV
            result: Validation result object to update
        """
        expected_columns = set(param.name for param in self.parameters)
        expected_columns.add(self.campaign_data["target"].get("name", self.TARGET_COLUMN_NAME))
        actual_columns = set(headers)

        missing = expected_columns - actual_columns
        if missing:
            result.missing_columns = list(missing)
            for col in missing:
                result.add_error(f"Missing required column: '{col}'")
                print(f"Error: Required column '{col}' is missing from CSV")

        # Check for extra columns (not an error, just a warning)
        extra = actual_columns - expected_columns
        if extra:
            result.extra_columns = list(extra)
            for col in extra:
                result.add_warning(f"Extra column found: '{col}' (will be ignored)")
                print(f"Warning: Extra column '{col}' found in CSV (will be ignored)")

        # Check for duplicate headers
        if len(headers) != len(set(headers)):
            duplicates = [h for h in headers if headers.count(h) > 1]
            for dup in set(duplicates):
                result.add_error(f"Duplicate column header: '{dup}'")
                print(f"CSV headers validated: {len(headers)} columns found")

    def _validate_data_rows(
        self,
        data_rows: List[List[str]],
        headers: List[str],
        result: CSVValidationResult,
    ) -> List[Dict[str, Any]]:
        """
        Validate data in each row against parameter constraints.

        Args:
            data_rows: Raw data rows from CSV
            headers: Column headers
            result: Validation result object to update

        Returns:
            List of validated data dictionaries
        """
        validated_data = []

        for row_index, row in enumerate(data_rows):
            row_dict = {}
            row_has_errors = False

            # Create dictionary from row data
            for col_index, header in enumerate(headers):
                value = row[col_index].strip() if col_index < len(row) else ""
                row_dict[header] = value

            # Validate each parameter column
            for param in self.parameters:
                if param.name in row_dict:
                    raw_value = row_dict[param.name]

                    is_valid, converted_value, error_msg = self._validate_parameter_value(param, raw_value, row_index)

                    if is_valid:
                        row_dict[param.name] = converted_value
                    else:
                        result.add_row_error(row_index + 1, error_msg)  # +1 for human-readable row numbers
                        row_has_errors = True

            # Only add valid rows to final data
            if not row_has_errors:
                validated_data.append(row_dict)

        return validated_data

    def _validate_parameter_value(
        self, parameter: BaseParameter, raw_value: str, row_index: int
    ) -> Tuple[bool, Any, str]:
        """
        Validate a single value against a parameter's constraints.

        Args:
            parameter: The parameter to validate against
            raw_value: Raw string value from CSV
            row_index: Row index for error reporting

        Returns:
            Tuple of (is_valid, converted_value, error_message)
        """
        if not raw_value:
            return False, None, f"Empty value for parameter '{parameter.name}'."

        try:
            converted_value = parameter.convert_value(raw_value)

            is_valid, error_msg = parameter.validate_value(converted_value)

            if is_valid:
                return True, converted_value, ""
            else:
                return False, None, f"Parameter '{parameter.name}': {error_msg}."

        except (ValueError, TypeError) as e:
            return (
                False,
                None,
                f"Cannot convert value '{raw_value}' for parameter '{parameter.name}': {e}",
            )
