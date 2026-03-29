from typing import List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.models.user import User
from backend.app.models.workout import (
    WorkoutTemplate,
    WorkoutStep,
    WorkoutType,
    StepType,
    DurationType,
    TargetType,
)
from backend.app.core.config import settings

# Import existing CLI parsing logic
from workout_parser.parser import WorkoutParser


class WorkoutService:
    """
    Service for creating and managing workouts using AI parsing.

    Integrates with existing CLI workout parsing logic.
    """

    def __init__(self, db: Session):
        self.db = db
        self.parser = WorkoutParser(api_key=settings.GOOGLE_API_KEY)

    async def parse_workout(
        self, user: User, prompt: str, workout_type: WorkoutType
    ) -> WorkoutTemplate:
        """
        Parse a natural language workout description into a structured workout.

        Args:
            user: User model instance
            prompt: Natural language workout description
            workout_type: Type of workout (running, cycling, etc.)

        Returns:
            WorkoutTemplate: Created workout template with steps

        Raises:
            Exception: If parsing fails
        """
        try:
            # Parse workout using existing logic
            parsed_result = self.parser.parse(prompt, workout_type=workout_type.value)

            # Create workout template
            workout = WorkoutTemplate(
                user_id=user.id,
                name=parsed_result.get("name", "Untitled Workout"),
                description=parsed_result.get("description"),
                workout_type=workout_type,
                original_prompt=prompt,
                parsed_data=parsed_result,
            )

            self.db.add(workout)
            self.db.flush()  # Get workout ID without committing

            # Create workout steps
            steps_data = parsed_result.get("steps", [])
            for order, step_data in enumerate(steps_data):
                step = WorkoutStep(
                    workout_id=workout.id,
                    order=order,
                    step_type=StepType(step_data.get("type", "interval")),
                    description=step_data.get("description"),
                    duration_type=DurationType(step_data.get("duration_type", "time")),
                    duration_value=step_data.get("duration_value"),
                    target_type=TargetType(step_data.get("target_type", "open")),
                    target_value_low=step_data.get("target_low"),
                    target_value_high=step_data.get("target_high"),
                    repeat_times=step_data.get("repeat", 1),
                )
                self.db.add(step)

            self.db.commit()
            self.db.refresh(workout)

            return workout

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to parse workout: {str(e)}")

    async def get_user_workouts(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> List[WorkoutTemplate]:
        """
        Get all workouts for a user.

        Args:
            user: User model instance
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of WorkoutTemplate instances
        """
        return (
            self.db.query(WorkoutTemplate)
            .filter(WorkoutTemplate.user_id == user.id)
            .order_by(WorkoutTemplate.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_workout_by_id(
        self, user: User, workout_id: UUID
    ) -> WorkoutTemplate:
        """
        Get a specific workout by ID.

        Args:
            user: User model instance
            workout_id: Workout UUID

        Returns:
            WorkoutTemplate instance

        Raises:
            Exception: If workout not found or doesn't belong to user
        """
        workout = (
            self.db.query(WorkoutTemplate)
            .filter(
                WorkoutTemplate.id == workout_id,
                WorkoutTemplate.user_id == user.id,
            )
            .first()
        )

        if not workout:
            raise Exception("Workout not found")

        return workout

    async def delete_workout(self, user: User, workout_id: UUID) -> bool:
        """
        Delete a workout.

        Args:
            user: User model instance
            workout_id: Workout UUID

        Returns:
            bool: True if successful

        Raises:
            Exception: If workout not found or doesn't belong to user
        """
        workout = await self.get_workout_by_id(user, workout_id)

        try:
            self.db.delete(workout)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to delete workout: {str(e)}")

    def convert_to_garmin_format(self, workout: WorkoutTemplate) -> Dict[str, Any]:
        """
        Convert a WorkoutTemplate to Garmin-compatible format.

        Args:
            workout: WorkoutTemplate instance

        Returns:
            Dict with Garmin workout format
        """
        # This will use the existing conversion logic from the CLI tool
        garmin_workout = {
            "workoutName": workout.name,
            "description": workout.description or "",
            "sport": workout.workout_type.value,
            "workoutSegments": [],
        }

        for step in workout.steps:
            segment = {
                "segmentOrder": step.order + 1,
                "sportType": workout.workout_type.value,
                "workoutSteps": [
                    {
                        "type": step.step_type.value,
                        "durationType": step.duration_type.value,
                        "durationValue": step.duration_value,
                        "targetType": step.target_type.value,
                        "targetValueLow": step.target_value_low,
                        "targetValueHigh": step.target_value_high,
                    }
                ],
            }
            garmin_workout["workoutSegments"].append(segment)

        return garmin_workout
