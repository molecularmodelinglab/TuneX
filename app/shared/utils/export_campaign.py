import csv

from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.models.enums import ParameterType


class CampaignExporter:
    """Utility class for exporting campaign data to various formats."""

    @staticmethod
    def export_campaign_to_csv(campaign, parent_widget=None):
        """Export campaign data to CSV file with file dialog."""
        if not campaign:
            if parent_widget:
                QMessageBox.warning(parent_widget, "Export Error", "No campaign data to export.")
            return False

        campaign_name = campaign.name or "campaign"
        safe_name = "".join(c for c in campaign_name if c.isalnum() or c in (" ", "-", "_")).rstrip()
        default_filename = f"{safe_name}.csv"

        filename, _ = QFileDialog.getSaveFileName(
            parent_widget, "Export Campaign Data", default_filename, "CSV Files (*.csv);;All Files (*)"
        )

        if filename:
            try:
                CampaignExporter._write_campaign_csv(campaign, filename)
                if parent_widget:
                    QMessageBox.information(
                        parent_widget, "Export Successful", f"Campaign data exported to:\n{filename}"
                    )
                return True
            except Exception as e:
                if parent_widget:
                    QMessageBox.critical(parent_widget, "Export Error", f"Failed to export campaign data:\n{str(e)}")
                return False

        return False

    @staticmethod
    def _write_campaign_csv(campaign, filename: str):
        """Write campaign data to CSV file."""
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(["Campaign Information"])
            writer.writerow(["Name", campaign.name or ""])
            writer.writerow(["Description", campaign.description or ""])
            writer.writerow([])

            if hasattr(campaign, "parameters") and campaign.parameters:
                writer.writerow(["Parameters"])
                writer.writerow(["Parameter Name", "Type", "Values"])

                for param in campaign.parameters:
                    param_name = param.name or ""
                    param_type = CampaignExporter._format_parameter_type(param)
                    param_values = CampaignExporter._format_parameter_values(param)
                    writer.writerow([param_name, param_type, param_values])

                writer.writerow([])

            if hasattr(campaign, "experiments") and campaign.experiments:
                writer.writerow(["Experiments"])
                writer.writerow(["Experiment ID", "Status", "Results"])

                for exp in campaign.experiments:
                    exp_id = getattr(exp, "id", "N/A")
                    exp_status = getattr(exp, "status", "N/A")
                    exp_results = getattr(exp, "results", "N/A")
                    writer.writerow([exp_id, exp_status, exp_results])

    @staticmethod
    def _format_parameter_type(param) -> str:
        """Format parameter type for display."""
        if not hasattr(param, "parameter_type") or not param.parameter_type:
            return "Unknown"

        param_type = param.parameter_type

        if param_type == ParameterType.DISCRETE_NUMERICAL_REGULAR:
            return "Discrete Numerical Regular"
        elif param_type == ParameterType.DISCRETE_NUMERICAL_IRREGULAR:
            return "Discrete Numerical Irregular"
        elif param_type == ParameterType.CONTINUOUS_NUMERICAL:
            return "Continuous Numerical"
        elif param_type == ParameterType.CATEGORICAL:
            return "Categorical"
        elif param_type == ParameterType.FIXED:
            return "Fixed"
        elif param_type == ParameterType.SUBSTANCE:
            return "Substance"
        else:
            return param_type.name.replace("_", " ").title()

    @staticmethod
    def _format_parameter_values(param) -> str:
        """Format parameter values for display."""
        if not hasattr(param, "parameter_type") or not param.parameter_type:
            return "No values defined"

        param_type = param.parameter_type.value

        try:
            if param_type == "discrete_numerical_regular":
                start = getattr(param, "min_val", "N/A")
                stop = getattr(param, "max_val", "N/A")
                step = getattr(param, "step", "N/A")
                return f"start: {start}, stop: {stop}, step: {step}"

            elif param_type == "discrete_numerical_irregular":
                values = getattr(param, "values", [])
                if isinstance(values, list) and values:
                    return ", ".join(map(str, values))
                return "No values"

            elif param_type == "continuous_numerical":
                start = getattr(param, "min_val", "N/A")
                end = getattr(param, "max_val", "N/A")
                return f"start: {start}, end: {end}"

            elif param_type == "fixed":
                value = getattr(param, "value", "N/A")
                return f"Value: {value}"

            elif param_type == "categorical":
                values = getattr(param, "values", [])
                if isinstance(values, list) and values:
                    return ", ".join(map(str, values))
                return "No values"

            elif param_type == "substance":
                smiles = getattr(param, "smiles", "N/A")
                return f"SMILES: {smiles}"

            else:
                if hasattr(param, "values"):
                    values = param.values
                    if isinstance(values, list) and values:
                        return ", ".join(map(str, values))
                return "No values defined"

        except Exception as e:
            return f"Error: {str(e)}"


class ParameterFormatter:
    """Utility class for formatting parameter data for display."""

    @staticmethod
    def format_parameter_type(param) -> str:
        """Format parameter type for display."""
        return CampaignExporter._format_parameter_type(param)

    @staticmethod
    def format_parameter_values(param) -> str:
        """Format parameter values for display."""
        return CampaignExporter._format_parameter_values(param)
