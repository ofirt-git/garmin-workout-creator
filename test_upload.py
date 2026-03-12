#!/usr/bin/env python3
"""
Quick test script for uploading minimal workout
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from garmin_uploader import GarminUploader

# Read the minimal workout
with open("minimal_workout.json", "r") as f:
    workout_json = f.read()

# Create uploader - it will use cached session
uploader = GarminUploader()

# Get credentials from environment or prompt
email = os.environ.get("GARMIN_EMAIL")
password = os.environ.get("GARMIN_PASSWORD")

# Upload
print("Uploading minimal workout...")
result = uploader.upload_from_json(workout_json, email=email, password=password)

if result["success"]:
    print(f"✓ Workout uploaded successfully!")
    print(f"  Workout ID: {result['workout_id']}")
    print(f"  URL: {result['url']}")
else:
    print(f"✗ Upload failed: {result['error']}")
    sys.exit(1)
