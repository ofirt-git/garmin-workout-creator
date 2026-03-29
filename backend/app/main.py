"""
Garmin Workout Creator - FastAPI Application
Main entry point for the web application backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# This will be populated in Phase 2
# from app.api import auth, garmin, workouts
# from app.core.config import settings

app = FastAPI(
    title="Garmin Workout Creator API",
    version="2.0.0",
    description="API for creating and managing Garmin workouts with natural language"
)

# CORS Configuration - will be configured properly in Phase 2
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Garmin Workout Creator API",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "not_configured",  # Will be updated in Phase 2
        "api": "operational"
    }

# API routes will be added in Phase 2:
# app.include_router(auth.router)
# app.include_router(garmin.router)
# app.include_router(workouts.router)
