from typing import Any, Dict, List

from app.models.parameters.base import BaseParameter


class ParameterSerializer:
    """
    Handles serialization and deserialization of parameters.

    This class provides a simple interface for converting parameters to/from
    dictionary format. The actual serialization logic is handled by the
    parameter classes themselves, keeping this class simple and focused.
    """

    @staticmethod
    def serialize_parameters(
        parameters: List[BaseParameter],
    ) -> List[Dict[str, Any]]:
        """
        Convert parameter objects to dictionary format for saving.

        Args:
            parameters: List of parameter objects to serialize

        Returns:
            List of dictionaries representing the parameters
        """
        return [param.to_dict() for param in parameters]

    @staticmethod
    def deserialize_parameters(
        parameters_data: List[Dict[str, Any]],
    ) -> List[BaseParameter]:
        """
        Convert dictionary data back to parameter objects.

        Args:
            parameters_data: List of parameter dictionaries (from serialize_parameters)

        Returns:
            List of parameter objects

        Note:
            Uses BaseParameter.from_dict() so this class doesn't need to know
            about internal parameter formats or types.
        """
        parameters = []

        for param_dict in parameters_data:
            try:
                # Let the parameter classes handle their own deserialization
                parameter = BaseParameter.from_dict(param_dict)
                parameters.append(parameter)
            except Exception as e:
                print(f"Error loading parameter: {e}")
                # Continue loading other parameters even if one fails

        return parameters
