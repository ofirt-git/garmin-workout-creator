"""
LLM-based workout parser using Claude API
Uses structured output to convert natural language to workout JSON
"""

import anthropic
import json
from typing import Dict, Any
from .models import Workout


class LLMWorkoutParser:
    """Parse workout descriptions using Claude with structured output"""

    def __init__(self, api_key: str):
        """
        Initialize parser with Anthropic API key

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)

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

        # Use Claude with tool use to enforce structured output
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=[self._get_workout_schema()],
            tool_choice={"type": "tool", "name": "workout_definition"},
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            system=system_prompt
        )

        # Extract the structured workout from tool use
        for content_block in response.content:
            if content_block.type == "tool_use" and content_block.name == "workout_definition":
                workout_data = content_block.input
                return Workout.model_validate(workout_data)

        raise Exception("Failed to parse workout - no structured output received")

    def _build_system_prompt(self) -> str:
        """Build system prompt with instructions and examples"""
        return """You are a workout parser that converts natural language workout descriptions into structured JSON format.

Your task is to analyze workout descriptions and extract:
1. Workout name (generate descriptive name if not provided)
2. Sport type (running, cycling, swimming, or other)
3. Structured steps with proper warmup, intervals, recovery, cooldown, and repeat blocks

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

Common pace interpretations:
- Easy: open target
- Recovery: open target
- 5K pace: ~3:45-4:15 min/km (225-255 sec/km)
- 10K pace: ~4:00-4:30 min/km (240-270 sec/km)
- Half marathon pace: ~4:30-5:00 min/km (270-300 sec/km)
- Marathon pace: ~5:00-5:30 min/km (300-330 sec/km)
- Tempo/Threshold: ~4:15-4:45 min/km (255-285 sec/km)

Examples of structured output:

Example 1: "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down"
→ Warmup (5 min, open), Repeat 6x [800m interval at pace, 400m recovery open], Cooldown (5 min, open)

Example 2: "10 minute easy, then 4x1 mile at threshold with 2 minute recovery"
→ Warmup (10 min, open), Repeat 4x [1 mile at tempo pace, 2 min recovery open]

Example 3: "20 minute tempo run at 10k pace"
→ Single interval step (20 min, 10k pace target)

Always use the workout_definition tool to output the structured workout."""

    def _build_user_prompt(self, workout_text: str) -> str:
        """Build user prompt with the workout description"""
        return f"""Parse this workout description and return it in structured format:

"{workout_text}"

Return the workout using the workout_definition tool with proper JSON structure."""

    def _get_workout_schema(self) -> Dict[str, Any]:
        """
        Get the workout schema as a Claude tool definition
        This enforces structured output matching our Pydantic models
        """
        return {
            "name": "workout_definition",
            "description": "Structured workout definition with steps and targets",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workout_name": {
                        "type": "string",
                        "description": "Descriptive name for the workout"
                    },
                    "sport_type": {
                        "type": "string",
                        "enum": ["running", "cycling", "swimming", "other"],
                        "description": "Type of sport for this workout"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional workout description"
                    },
                    "steps": {
                        "type": "array",
                        "description": "List of workout steps",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_id": {"type": "integer"},
                                "step_type": {
                                    "type": "string",
                                    "enum": ["warmup", "cooldown", "interval", "recovery", "rest", "repeat"]
                                },
                                "duration_type": {
                                    "type": "string",
                                    "enum": ["time", "distance", "lap_button", "open"]
                                },
                                "duration_value": {
                                    "type": "number",
                                    "description": "Numeric value for duration"
                                },
                                "duration_unit": {
                                    "type": "string",
                                    "description": "Unit for duration (seconds, meters, etc.)"
                                },
                                "target_type": {
                                    "type": "string",
                                    "enum": ["open", "pace", "speed", "heart_rate", "cadence", "power"]
                                },
                                "target_value": {
                                    "type": "object",
                                    "description": "Target details (pace range, HR zone, etc.)"
                                },
                                "repeat_count": {
                                    "type": "integer",
                                    "description": "Number of repetitions (for repeat steps)"
                                },
                                "steps": {
                                    "type": "array",
                                    "description": "Nested steps for repeat blocks",
                                    "items": {"type": "object"}
                                }
                            },
                            "required": ["step_id", "step_type", "target_type"]
                        }
                    }
                },
                "required": ["workout_name", "sport_type", "steps"]
            }
        }
