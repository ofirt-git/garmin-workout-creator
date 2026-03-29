from fastapi import APIRouter
from .auth import router as auth_router
from .workouts import router as workouts_router
from .garmin import router as garmin_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workouts_router, prefix="/workouts", tags=["Workouts"])
api_router.include_router(garmin_router, prefix="/garmin", tags=["Garmin"])

__all__ = ["api_router"]
