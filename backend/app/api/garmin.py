from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user import GarminConnect
from backend.app.schemas.workout import WorkoutUploadResponse
from backend.app.services.garmin_service import GarminService
from backend.app.services.workout_service import WorkoutService
from backend.app.api.auth import get_current_user

router = APIRouter()


@router.post("/connect", status_code=status.HTTP_200_OK)
async def connect_garmin(
    credentials: GarminConnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Connect Garmin account with user credentials.

    Authenticates with Garmin Connect and stores encrypted OAuth tokens.
    The password is NOT stored - only OAuth tokens are kept.

    - **email**: Garmin Connect email
    - **password**: Garmin Connect password (not stored)
    """
    try:
        garmin_service = GarminService(db)
        await garmin_service.connect_garmin(
            user=current_user,
            email=credentials.email,
            password=credentials.password,
        )

        return {
            "message": "Successfully connected to Garmin",
            "connected_at": datetime.utcnow(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to Garmin: {str(e)}",
        )


@router.post("/disconnect", status_code=status.HTTP_200_OK)
async def disconnect_garmin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Disconnect Garmin account.

    Removes all stored Garmin credentials and tokens.
    """
    try:
        garmin_service = GarminService(db)
        await garmin_service.disconnect_garmin(user=current_user)

        return {"message": "Successfully disconnected from Garmin"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def garmin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check Garmin connection status.

    Returns whether the user has connected their Garmin account.
    """
    garmin_service = GarminService(db)
    is_connected = await garmin_service.is_connected(user=current_user)

    return {
        "connected": is_connected,
        "garmin_email": current_user.garmin_email if is_connected else None,
        "connected_at": current_user.garmin_connected_at if is_connected else None,
    }


@router.post("/upload/{workout_id}", response_model=WorkoutUploadResponse)
async def upload_workout_to_garmin(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a workout to Garmin Connect.

    Requires Garmin account to be connected.

    - **workout_id**: UUID of the workout to upload
    """
    # Check if Garmin is connected
    garmin_service = GarminService(db)
    if not await garmin_service.is_connected(user=current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected. Please connect your Garmin account first.",
        )

    try:
        # Get workout
        workout_service = WorkoutService(db)
        workout = await workout_service.get_workout_by_id(
            user=current_user, workout_id=workout_id
        )

        # Convert to Garmin format
        garmin_workout_data = workout_service.convert_to_garmin_format(workout)

        # Upload to Garmin
        garmin_workout_id = await garmin_service.upload_workout(
            user=current_user, workout_data=garmin_workout_data
        )

        # Update workout with Garmin ID
        workout.garmin_workout_id = garmin_workout_id
        workout.uploaded_at = datetime.utcnow()
        db.commit()

        return WorkoutUploadResponse(
            workout_id=workout.id,
            garmin_workout_id=garmin_workout_id,
            uploaded_at=workout.uploaded_at,
            message="Workout successfully uploaded to Garmin Connect",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload workout: {str(e)}",
        )
