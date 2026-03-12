"""
Gemini-based workout parser using Google's Generative AI
Uses structured output to convert natural language to workout JSON
"""

import json
from typing import Dict, Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "google-genai is required for Gemini parsing. "
        "Install it with: pip install google-genai"
    )

from .models import Workout


class GeminiWorkoutParser:
    """Parse workout descriptions using Google Gemini with structured output"""

    def __init__(self, api_key: str):
        """
        Initialize parser with Google API key

        Args:
            api_key: Google AI Studio API key
        """
        self.client = genai.Client(api_key=api_key)

    def parse(self, workout_text: str) -> Workout:
        """
        Parse free-text workout description into structured Workout object

        Args:
            workout_text: Natural language workout description

        Returns:
            Validated Workout object

        Raises:
            Exception: If parsing or validation fails
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(workout_text)

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            # Generate response using new API
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            # Parse and validate
            workout_data = json.loads(response_text)
            return Workout.model_validate(workout_data)

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {e}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Gemini parsing failed: {e}")

    def _build_system_prompt(self) -> str:
        """Build system prompt with instructions and examples"""
        return """You are a workout parser that converts natural language workout descriptions into structured JSON format.

Your task is to analyze workout descriptions and extract:
1. Workout name (generate descriptive name if not provided)
2. Sport type (running, cycling, swimming, or other)
3. Structured steps with proper warmup, intervals, recovery, cooldown, and repeat blocks

CRITICAL: You must return ONLY valid JSON, with no additional text before or after.

Key parsing rules:
- All durations in seconds (convert from minutes)
- All distances in meters (convert from km, miles, yards)
- Pace in seconds per km or seconds per mile
- Use "open" target when no specific target is mentioned (e.g., "easy", "recovery")
- Create repeat blocks for intervals (e.g., "6x800m" = repeat 6 times)
- Generate sequential step_id starting from 1
- Warmup and cooldown typically have "open" targets unless specified
- "Easy", "recovery" without specific pace = open target
- "Tempo", "threshold", "5k pace" = pace targets (estimate reasonable ranges)

Common pace interpretations (for running):
- Easy/Recovery: open target (no specific pace)
- 5K pace: 225-255 seconds per km
- 10K pace: 240-270 seconds per km
- Half marathon pace: 270-300 seconds per km
- Marathon pace: 300-330 seconds per km
- Tempo/Threshold: 255-285 seconds per km

For specific paces like "4:00/km", convert to range:
- 4:00/km = 240 sec/km, use range like 230-250 sec/km (±10 seconds)

JSON Schema:
{
  "workout_name": "string - descriptive name",
  "sport_type": "running|cycling|swimming|other",
  "description": "string - optional",
  "steps": [
    {
      "step_id": number,
      "step_type": "warmup|cooldown|interval|recovery|rest|repeat",
      "duration_type": "time|distance|lap_button|open",
      "duration_value": number,
      "duration_unit": "seconds|meters|kilometers|miles",
      "target_type": "open|pace|speed|heart_rate|cadence|power",
      "target_value": {
        "min_pace": number (seconds),
        "max_pace": number (seconds),
        "unit": "seconds_per_km|seconds_per_mile"
      } or null,
      "repeat_count": number (only for repeat type),
      "steps": [...] (only for repeat type - nested steps)
    }
  ]
}

Examples:

Example 1: "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down"
Output:
{
  "workout_name": "800m Intervals",
  "sport_type": "running",
  "steps": [
    {
      "step_id": 1,
      "step_type": "warmup",
      "duration_type": "time",
      "duration_value": 300,
      "duration_unit": "seconds",
      "target_type": "open",
      "target_value": null
    },
    {
      "step_id": 2,
      "step_type": "repeat",
      "repeat_count": 6,
      "target_type": "open",
      "steps": [
        {
          "step_id": 3,
          "step_type": "interval",
          "duration_type": "distance",
          "duration_value": 800,
          "duration_unit": "meters",
          "target_type": "pace",
          "target_value": {
            "min_pace": 225,
            "max_pace": 255,
            "unit": "seconds_per_km"
          }
        },
        {
          "step_id": 4,
          "step_type": "recovery",
          "duration_type": "distance",
          "duration_value": 400,
          "duration_unit": "meters",
          "target_type": "open",
          "target_value": null
        }
      ]
    },
    {
      "step_id": 5,
      "step_type": "cooldown",
      "duration_type": "time",
      "duration_value": 300,
      "duration_unit": "seconds",
      "target_type": "open",
      "target_value": null
    }
  ]
}

Remember: Return ONLY the JSON object, nothing else."""

    def _build_user_prompt(self, workout_text: str) -> str:
        """Build user prompt with the workout description"""
        return f"""Parse this workout description and return ONLY the JSON (no markdown, no explanation):

"{workout_text}"

Return the workout as a JSON object following the schema provided above."""
