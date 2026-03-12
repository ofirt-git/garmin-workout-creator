#!/usr/bin/env python3
"""
Fetch existing workouts from Garmin to see the correct format
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from garmin_uploader import GarminUploader

uploader = GarminUploader()

# Use cached session
try:
    uploader.client = uploader.auth._load_cached_session()
    print("Fetching workouts from Garmin Connect...")

    # Get workout list
    workouts = uploader.get_workout_list(limit=5)

    print(f"\nFound {len(workouts)} workouts\n")

    for workout in workouts:
        print(f"Workout: {workout.get('workoutName', 'Unnamed')}")
        print(f"ID: {workout.get('workoutId')}")
        print(f"Sport: {workout.get('sportType', {})}")
        print("-" * 50)

    # Get full details of first workout
    if workouts:
        first_id = workouts[0].get('workoutId')
        print(f"\n\nFetching full details for workout {first_id}...")

        response = uploader.client.request(
            "GET",
            "connectapi",
            f"/workout-service/workout/{first_id}",
            api=True
        )

        print("\n[FULL WORKOUT FORMAT]")
        print(json.dumps(response.json(), indent=2))

        # Save to file
        with open("/tmp/garmin_workout_example.json", "w") as f:
            json.dump(response.json(), f, indent=2)
        print("\n✓ Saved to /tmp/garmin_workout_example.json")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
