"""
Main workout parser interface
Provides unified API for different parsing methods
"""

from .llm_parser import LLMWorkoutParser
from .gemini_parser import GeminiWorkoutParser
from .models import Workout
from typing import Literal


class WorkoutParser:
    """
    Main interface for parsing workout descriptions
    Supports multiple parsing backends
    """

    def __init__(self, method: Literal["llm", "gemini"] = "gemini", **kwargs):
        """
        Initialize parser with specified method

        Args:
            method: Parsing method to use ("llm" for Claude, "gemini" for Google Gemini)
            **kwargs: Method-specific configuration
                - api_key (str): Required for both methods

        Raises:
            ValueError: If method is unknown or required kwargs missing
        """
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError(f"api_key is required for {method} parsing method")

        if method == "llm":
            self.parser = LLMWorkoutParser(api_key=api_key)
        elif method == "gemini":
            self.parser = GeminiWorkoutParser(api_key=api_key)
        else:
            raise ValueError(f"Unknown parsing method: {method}")

        self.method = method

    def parse_to_json(self, workout_text: str, pretty: bool = True) -> str:
        """
        Parse workout text and return JSON string

        Args:
            workout_text: Natural language workout description
            pretty: Whether to format JSON with indentation

        Returns:
            JSON string representation of workout

        Raises:
            Exception: If parsing fails
        """
        workout = self.parser.parse(workout_text)
        if pretty:
            return workout.model_dump_json(indent=2)
        else:
            return workout.model_dump_json()

    def parse_to_object(self, workout_text: str) -> Workout:
        """
        Parse workout text and return Workout object

        Args:
            workout_text: Natural language workout description

        Returns:
            Validated Workout object

        Raises:
            Exception: If parsing fails
        """
        return self.parser.parse(workout_text)

    @staticmethod
    def validate_json(workout_json: str) -> tuple[bool, str]:
        """
        Validate a workout JSON string against schema

        Args:
            workout_json: JSON string to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Empty string if valid, error details if invalid
        """
        try:
            Workout.model_validate_json(workout_json)
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def load_from_json(workout_json: str) -> Workout:
        """
        Load a Workout object from JSON string

        Args:
            workout_json: Valid JSON string

        Returns:
            Workout object

        Raises:
            ValidationError: If JSON doesn't match schema
        """
        return Workout.from_json(workout_json)
