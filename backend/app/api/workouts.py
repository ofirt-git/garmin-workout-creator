from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.workout import WorkoutCreate, WorkoutResponse
from backend.app.services.workout_service import WorkoutService
from backend.app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new workout from natural language description.

    Parses the prompt using AI and creates a structured workout.

    - **prompt**: Natural language workout description (e.g., "5k tempo run with 2km warmup")
    - **workout_type**: Type of workout (running, cycling, swimming, strength, other)
    """
    try:
        workout_service = WorkoutService(db)
        workout = await workout_service.parse_workout(
            user=current_user,
            prompt=workout_data.prompt,
            workout_type=workout_data.workout_type,
        )
        return workout

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/", response_model=List[WorkoutResponse])
async def get_workouts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all workouts for the current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    workout_service = WorkoutService(db)
    workouts = await workout_service.get_user_workouts(
        user=current_user, skip=skip, limit=min(limit, 100)
    )
    return workouts


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific workout by ID.

    Returns the workout with all its steps.
    """
    try:
        workout_service = WorkoutService(db)
        workout = await workout_service.get_workout_by_id(
            user=current_user, workout_id=workout_id
        )
        return workout

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a workout.

    Permanently removes the workout and all its steps.
    """
    try:
        workout_service = WorkoutService(db)
        await workout_service.delete_workout(user=current_user, workout_id=workout_id)
        return None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
