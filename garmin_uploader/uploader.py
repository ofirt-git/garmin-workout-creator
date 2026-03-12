"""
Main Garmin uploader interface
Handles authentication and workout upload to Garmin Connect
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .auth import GarminAuth
from .transformer import WorkoutTransformer


class GarminUploader:
    """
    Main interface for uploading workouts to Garmin Connect
    """

    def __init__(self, credentials_dir: Optional[str] = None):
        """
        Initialize uploader

        Args:
            credentials_dir: Directory to store cached credentials
                           Defaults to ~/.garmin/
        """
        self.auth = GarminAuth(credentials_dir=credentials_dir)
        self.transformer = WorkoutTransformer()
        self.client = None

    def upload_from_json(
        self,
        workout_json: str,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a workout from standard JSON format

        Args:
            workout_json: Workout in standard JSON format
            email: Garmin Connect email (optional if session cached)
            password: Garmin Connect password (optional if session cached)

        Returns:
            Dictionary with upload result:
            {
                "success": bool,
                "workout_id": int or None,
                "workout_name": str,
                "url": str or None,
                "error": str or None
            }
        """
        try:
            # Authenticate if not already authenticated
            if not self.client:
                self.client = self.auth.login(email, password)

            # Parse workout name for response
            workout_data = json.loads(workout_json)
            workout_name = workout_data.get("workout_name", "Untitled Workout")

            # Transform to Garmin format
            print(f"Transforming workout: {workout_name}")
            garmin_workout = self.transformer.transform(workout_json)

            # Upload to Garmin
            print("Uploading to Garmin Connect...")
            response = self._upload_workout(garmin_workout)

            workout_id = response.get("workoutId")
            url = f"https://connect.garmin.com/modern/workout/{workout_id}" if workout_id else None

            return {
                "success": True,
                "workout_id": workout_id,
                "workout_name": workout_name,
                "url": url,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "workout_id": None,
                "workout_name": workout_data.get("workout_name", "Unknown") if 'workout_data' in locals() else "Unknown",
                "url": None,
                "error": str(e)
            }

    def upload_from_file(
        self,
        json_file_path: str,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a workout from a JSON file

        Args:
            json_file_path: Path to JSON file containing workout
            email: Garmin Connect email (optional if session cached)
            password: Garmin Connect password (optional if session cached)

        Returns:
            Dictionary with upload result (same as upload_from_json)
        """
        file_path = Path(json_file_path)

        if not file_path.exists():
            return {
                "success": False,
                "workout_id": None,
                "workout_name": "Unknown",
                "url": None,
                "error": f"File not found: {json_file_path}"
            }

        try:
            with open(file_path, 'r') as f:
                workout_json = f.read()

            return self.upload_from_json(workout_json, email, password)

        except Exception as e:
            return {
                "success": False,
                "workout_id": None,
                "workout_name": "Unknown",
                "url": None,
                "error": f"Failed to read file: {e}"
            }

    def _upload_workout(self, garmin_workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Low-level upload to Garmin Connect API

        Args:
            garmin_workout: Workout in Garmin format

        Returns:
            API response dictionary

        Raises:
            Exception: If upload fails
        """
        if not self.client:
            raise Exception("Not authenticated. Call login() first.")

        try:
            # Debug: Print the workout being sent
            print(f"\n[DEBUG] Sending workout to Garmin:")
            print(json.dumps(garmin_workout, indent=2))

            # Use garth's request method with correct signature
            # request(method, subdomain, path, api=False, ...)
            try:
                response = self.client.request(
                    "POST",
                    "connectapi",
                    "/workout-service/workout",
                    api=True,
                    json=garmin_workout
                )

                print(f"\n[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response content: {response.text[:1000] if response.text else 'empty'}")

                if response.status_code in [200, 201]:
                    return response.json() if response.text else {}
                else:
                    raise Exception(f"Garmin returned {response.status_code}: {response.text}")

            except Exception as req_error:
                # Try to get the response from the exception or client
                resp = None

                # Check if it's a GarthHTTPError with an error attribute
                if hasattr(req_error, 'error') and hasattr(req_error.error, 'response'):
                    resp = req_error.error.response

                # Check client's last_resp if we didn't get it from error
                if not resp and hasattr(self.client, 'last_resp'):
                    resp = self.client.last_resp

                if resp is not None:
                    print(f"\n[DEBUG] Error response status: {resp.status_code}")
                    print(f"[DEBUG] Error response body:")
                    print(resp.text)
                    print(f"[DEBUG] Error response headers: {dict(resp.headers)}")
                else:
                    print(f"\n[DEBUG] Could not extract response (resp is None)")
                raise

        except Exception as e:
            print(f"\n[DEBUG] Full error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to upload workout to Garmin: {e}")

    def logout(self):
        """Clear cached authentication session"""
        self.auth.logout()
        self.client = None

    def get_workout_list(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of workouts from Garmin Connect

        Args:
            limit: Maximum number of workouts to retrieve

        Returns:
            List of workout dictionaries

        Raises:
            Exception: If not authenticated or API call fails
        """
        if not self.client:
            raise Exception("Not authenticated. Call login() first.")

        try:
            response = self.client.connectapi(
                f"/workout-service/workouts?limit={limit}",
                method="GET"
            )

            if isinstance(response, list):
                return response
            else:
                return json.loads(response)

        except Exception as e:
            raise Exception(f"Failed to retrieve workouts: {e}")
