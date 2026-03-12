"""
Transformer to convert standard workout JSON to Garmin Connect format
"""

import json
from typing import Dict, Any, List


class WorkoutTransformer:
    """
    Converts standardized workout JSON to Garmin Connect API format
    """

    # Sport type mappings (Garmin internal IDs)
    SPORT_TYPE_MAP = {
        "running": {"sportTypeId": 1, "sportTypeKey": "running"},
        "cycling": {"sportTypeId": 2, "sportTypeKey": "cycling"},
        "swimming": {"sportTypeId": 3, "sportTypeKey": "lap_swimming"},
        "other": {"sportTypeId": 1, "sportTypeKey": "running"},  # Default to running
    }

    # Duration type mappings
    DURATION_TYPE_MAP = {
        "time": "time",
        "distance": "distance",
        "lap_button": "lap.button",
        "open": "open",
    }

    # Target type mappings
    TARGET_TYPE_MAP = {
        "open": "no.target",
        "pace": "pace.zone",
        "speed": "speed.zone",
        "heart_rate": "heart.rate.zone",
        "cadence": "cadence.zone",
        "power": "power.zone",
    }

    # Step type mappings
    STEP_TYPE_MAP = {
        "warmup": 1,
        "cooldown": 2,
        "interval": 3,
        "recovery": 4,
        "rest": 5,
        "repeat": 6,
    }

    def transform(self, workout_json: str) -> Dict[str, Any]:
        """
        Convert standard workout JSON to Garmin workout format

        Args:
            workout_json: JSON string in standard format

        Returns:
            Dictionary ready for Garmin Connect API

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            workout_data = json.loads(workout_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        sport_info = self.SPORT_TYPE_MAP.get(
            workout_data.get("sport_type", "running"),
            self.SPORT_TYPE_MAP["running"]
        )

        # Get workout steps
        workout_steps = self._transform_steps(workout_data.get("steps", []))

        garmin_workout = {
            "workoutName": workout_data.get("workout_name", "Untitled Workout"),
            "sportType": sport_info,
            "workoutSegments": [
                {
                    "segmentOrder": 1,
                    "sportType": sport_info,
                    "workoutSteps": workout_steps
                }
            ]
        }

        # Only add description if it exists and is not None
        description = workout_data.get("description")
        if description:
            garmin_workout["description"] = description

        return garmin_workout

    def _transform_steps(self, steps: List[Dict[str, Any]], inside_repeat: bool = False) -> List[Dict[str, Any]]:
        """
        Transform workout steps to Garmin format

        Args:
            steps: List of standard format steps
            inside_repeat: Whether these steps are inside a repeat block

        Returns:
            List of Garmin format steps
        """
        garmin_steps = []
        order = 1

        for step in steps:
            if step["step_type"] == "repeat":
                garmin_step = self._transform_repeat_step(step, order)
            else:
                garmin_step = self._transform_regular_step(step, order, inside_repeat)

            garmin_steps.append(garmin_step)
            order += 1

        return garmin_steps

    def _transform_regular_step(self, step: Dict[str, Any], order: int, inside_repeat: bool = False) -> Dict[str, Any]:
        """
        Transform a single workout step to Garmin format

        Args:
            step: Standard format step
            order: Step order number

        Returns:
            Garmin format step
        """
        step_type = step["step_type"]
        step_type_id = self.STEP_TYPE_MAP.get(step_type, 3)  # Default to interval

        garmin_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": order,
            "stepType": {
                "stepTypeId": step_type_id,
                "stepTypeKey": step_type
            },
            "childStepId": 1 if inside_repeat else None,
            "description": step.get("description")
        }

        # Add duration
        duration = self._transform_duration(step)
        if duration:
            garmin_step["endCondition"] = duration
            garmin_step["endConditionValue"] = duration.get("endConditionValue", 0.0)
        else:
            # If no duration, use lap button as default
            garmin_step["endCondition"] = {
                "conditionTypeId": 1,
                "conditionTypeKey": "lap.button"
            }
            garmin_step["endConditionValue"] = 0.0

        garmin_step["preferredEndConditionUnit"] = None
        garmin_step["endConditionCompare"] = None

        # Add target
        target = self._transform_target(step)
        if target:
            garmin_step["targetType"] = target
            garmin_step["targetValueOne"] = target.get("targetValueOne")
            garmin_step["targetValueTwo"] = target.get("targetValueTwo", 0.0)
        else:
            # Default target
            garmin_step["targetType"] = {
                "workoutTargetTypeId": 1,
                "workoutTargetTypeKey": "no.target"
            }
            garmin_step["targetValueOne"] = None
            garmin_step["targetValueTwo"] = 0.0

        garmin_step["targetValueUnit"] = None
        garmin_step["zoneNumber"] = None
        garmin_step["secondaryTargetType"] = None
        garmin_step["secondaryTargetValueOne"] = None
        garmin_step["secondaryTargetValueTwo"] = None
        garmin_step["secondaryTargetValueUnit"] = None
        garmin_step["secondaryZoneNumber"] = None
        garmin_step["endConditionZone"] = None

        # Add required but unused fields for running
        garmin_step["strokeType"] = {
            "strokeTypeId": 0,
            "strokeTypeKey": None,
            "displayOrder": 0
        }
        garmin_step["equipmentType"] = {
            "equipmentTypeId": 0,
            "equipmentTypeKey": None,
            "displayOrder": 0
        }
        garmin_step["category"] = None
        garmin_step["exerciseName"] = None
        garmin_step["workoutProvider"] = None
        garmin_step["providerExerciseSourceId"] = None
        garmin_step["weightValue"] = None
        garmin_step["weightUnit"] = {
            "unitId": 8,
            "unitKey": "kilogram",
            "factor": 1000.0
        }

        return garmin_step

    def _transform_repeat_step(self, step: Dict[str, Any], order: int) -> Dict[str, Any]:
        """
        Transform a repeat block to Garmin format

        Args:
            step: Standard format repeat step
            order: Step order number

        Returns:
            Garmin format repeat step
        """
        nested_steps = step.get("steps", [])

        garmin_step = {
            "type": "RepeatGroupDTO",
            "stepOrder": order,
            "stepType": {
                "stepTypeId": 6,
                "stepTypeKey": "repeat"
            },
            "childStepId": 1,  # Repeat groups use childStepId: 1
            "numberOfIterations": step.get("repeat_count", 1),
            "smartRepeat": False,
            "workoutSteps": self._transform_steps(nested_steps, inside_repeat=True)
        }

        return garmin_step

    def _transform_duration(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform duration to Garmin format

        Args:
            step: Standard format step

        Returns:
            Garmin format duration (endCondition)
        """
        duration_type = step.get("duration_type")

        if not duration_type or duration_type == "open":
            return {
                "conditionTypeId": 1,
                "conditionTypeKey": "lap.button"
            }

        if duration_type == "time":
            # Convert to seconds if needed
            value = step.get("duration_value", 0)
            unit = step.get("duration_unit", "seconds")

            if unit == "minutes":
                value = value * 60

            return {
                "conditionTypeId": 2,
                "conditionTypeKey": "time",
                "endConditionValue": float(value)
            }

        if duration_type == "distance":
            # Convert to meters if needed
            value = step.get("duration_value", 0)
            unit = step.get("duration_unit", "meters")

            if unit == "kilometers" or unit == "km":
                value = value * 1000
            elif unit == "miles":
                value = value * 1609.34
            elif unit == "yards":
                value = value * 0.9144

            return {
                "conditionTypeId": 3,
                "conditionTypeKey": "distance",
                "endConditionValue": float(value)
            }

        if duration_type == "lap_button":
            return {
                "conditionTypeId": 1,
                "conditionTypeKey": "lap.button"
            }

        # Default to lap button
        return {
            "conditionTypeId": 1,
            "conditionTypeKey": "lap.button"
        }

    def _transform_target(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform target to Garmin format

        Args:
            step: Standard format step

        Returns:
            Garmin format target
        """
        target_type = step.get("target_type", "open")
        target_value = step.get("target_value")

        if target_type == "open" or not target_value:
            return {
                "workoutTargetTypeId": 1,
                "workoutTargetTypeKey": "no.target"
            }

        if target_type == "pace":
            # IMPORTANT: Despite being called "pace.zone", Garmin's API actually expects SPEED in m/s!
            # min_pace = faster pace = higher speed (e.g., 230s/km = 4.35 m/s)
            # max_pace = slower pace = lower speed (e.g., 250s/km = 4.00 m/s)
            min_pace_sec = target_value.get("min_pace", 0)  # faster pace in seconds per km
            max_pace_sec = target_value.get("max_pace", 0)  # slower pace in seconds per km

            # Convert pace (seconds per km) to speed (meters per second)
            # Speed (m/s) = 1000 meters / seconds_per_km
            speed_from_min_pace = 1000.0 / min_pace_sec if min_pace_sec > 0 else 0  # faster = higher speed
            speed_from_max_pace = 1000.0 / max_pace_sec if max_pace_sec > 0 else 0  # slower = lower speed

            # Garmin expects targetValueOne = FASTER (higher speed value)
            #                targetValueTwo = SLOWER (lower speed value)
            # (Display shows targetValueOne first, targetValueTwo second)
            return {
                "workoutTargetTypeId": 6,
                "workoutTargetTypeKey": "pace.zone",
                "targetValueOne": round(speed_from_min_pace, 7),  # faster pace = higher speed
                "targetValueTwo": round(speed_from_max_pace, 7)   # slower pace = lower speed
            }

        if target_type == "speed":
            # Speed zones
            min_speed = target_value.get("min_speed", 0)
            max_speed = target_value.get("max_speed", 0)

            return {
                "workoutTargetTypeId": 7,
                "workoutTargetTypeKey": "speed.zone",
                "targetValueOne": min_speed,
                "targetValueTwo": max_speed
            }

        if target_type == "heart_rate":
            # Check if zone-based or absolute
            zone = target_value.get("zone")

            if zone:
                return {
                    "workoutTargetTypeId": 4,
                    "workoutTargetTypeKey": "heart.rate.zone",
                    "zoneNumber": zone
                }
            else:
                min_hr = target_value.get("min_hr", 0)
                max_hr = target_value.get("max_hr", 0)

                return {
                    "workoutTargetTypeId": 4,
                    "workoutTargetTypeKey": "heart.rate.zone",
                    "targetValueOne": min_hr,
                    "targetValueTwo": max_hr
                }

        if target_type == "power":
            # Power zones
            zone = target_value.get("zone")

            if zone:
                return {
                    "workoutTargetTypeId": 10,
                    "workoutTargetTypeKey": "power.zone",
                    "zoneNumber": zone
                }
            else:
                min_power = target_value.get("min_power", 0)
                max_power = target_value.get("max_power", 0)

                return {
                    "workoutTargetTypeId": 10,
                    "workoutTargetTypeKey": "power.zone",
                    "targetValueOne": min_power,
                    "targetValueTwo": max_power
                }

        if target_type == "cadence":
            # Cadence zones
            min_cadence = target_value.get("min_cadence", 0)
            max_cadence = target_value.get("max_cadence", 0)

            return {
                "workoutTargetTypeId": 5,
                "workoutTargetTypeKey": "cadence.zone",
                "targetValueOne": min_cadence,
                "targetValueTwo": max_cadence
            }

        # Default to no target
        return {
            "workoutTargetTypeId": 1,
            "workoutTargetTypeKey": "no.target"
        }
