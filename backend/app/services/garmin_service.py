from datetime import datetime
from typing import Optional
import garth
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.core.security import encrypt_token, decrypt_token


class GarminService:
    """
    Service for handling Garmin Connect authentication and workout uploads.

    Uses the 'garth' library for Garmin Connect API interactions with
    encrypted token storage.
    """

    def __init__(self, db: Session):
        self.db = db

    async def connect_garmin(self, user: User, email: str, password: str) -> bool:
        """
        Authenticate with Garmin Connect and store encrypted tokens.

        Args:
            user: User model instance
            email: Garmin Connect email
            password: Garmin Connect password (not stored)

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        try:
            # Authenticate with Garmin
            garth.login(email, password)

            # Get OAuth tokens
            oauth1_token = garth.client.oauth1_token
            oauth2_token = garth.client.oauth2_token

            # Encrypt tokens before storage
            encrypted_oauth1 = encrypt_token(str(oauth1_token))
            encrypted_oauth2 = encrypt_token(str(oauth2_token))

            # Store in database
            user.garmin_email = email
            user.garmin_oauth1_token = encrypted_oauth1
            user.garmin_oauth2_token = encrypted_oauth2
            user.garmin_connected_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(user)

            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to connect to Garmin: {str(e)}")

    async def disconnect_garmin(self, user: User) -> bool:
        """
        Disconnect Garmin account by removing stored tokens.

        Args:
            user: User model instance

        Returns:
            bool: True if successful
        """
        try:
            user.garmin_email = None
            user.garmin_oauth1_token = None
            user.garmin_oauth2_token = None
            user.garmin_connected_at = None

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to disconnect Garmin: {str(e)}")

    def _restore_garmin_session(self, user: User) -> None:
        """
        Restore Garmin session from encrypted stored tokens.

        Args:
            user: User model instance with stored tokens

        Raises:
            Exception: If tokens are missing or invalid
        """
        if not user.garmin_oauth1_token or not user.garmin_oauth2_token:
            raise Exception("Garmin account not connected")

        try:
            # Decrypt tokens
            oauth1_token = decrypt_token(user.garmin_oauth1_token)
            oauth2_token = decrypt_token(user.garmin_oauth2_token)

            # Restore session
            garth.client.oauth1_token = eval(oauth1_token)
            garth.client.oauth2_token = eval(oauth2_token)

        except Exception as e:
            raise Exception(f"Failed to restore Garmin session: {str(e)}")

    async def upload_workout(
        self, user: User, workout_data: dict
    ) -> Optional[str]:
        """
        Upload a workout to Garmin Connect.

        Args:
            user: User model instance
            workout_data: Workout data in Garmin-compatible format

        Returns:
            str: Garmin workout ID if successful

        Raises:
            Exception: If upload fails
        """
        try:
            # Restore Garmin session
            self._restore_garmin_session(user)

            # Upload workout using garmin_uploader
            # This will use the existing garmin_uploader code
            from garmin_uploader.workflow import upload_workout as upload_to_garmin

            result = upload_to_garmin(workout_data)

            if result and "workout_id" in result:
                return result["workout_id"]
            else:
                raise Exception("Upload failed - no workout ID returned")

        except Exception as e:
            raise Exception(f"Failed to upload workout to Garmin: {str(e)}")

    async def is_connected(self, user: User) -> bool:
        """
        Check if user has connected Garmin account.

        Args:
            user: User model instance

        Returns:
            bool: True if Garmin is connected
        """
        return bool(user.garmin_oauth1_token and user.garmin_oauth2_token)
