"""
Garmin Connect authentication handler
Manages login sessions and credential caching
"""

import os
import pickle
import getpass
from pathlib import Path
from typing import Optional
from garth.exc import GarthHTTPError

try:
    from garth import Client
except ImportError:
    raise ImportError(
        "garth library is required for Garmin authentication. "
        "Install it with: pip install garth"
    )


class GarminAuth:
    """Handles authentication with Garmin Connect"""

    def __init__(self, credentials_dir: Optional[str] = None):
        """
        Initialize authentication handler

        Args:
            credentials_dir: Directory to store cached credentials
                           Defaults to ~/.garmin/
        """
        if credentials_dir is None:
            credentials_dir = os.path.expanduser("~/.garmin")

        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.credentials_dir / "session.pkl"
        self.client: Optional[Client] = None

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> Client:
        """
        Login to Garmin Connect

        Attempts to use cached session first, falls back to fresh login

        Args:
            email: Garmin Connect email (optional if session cached)
            password: Garmin Connect password (optional if session cached)

        Returns:
            Authenticated garth Client

        Raises:
            Exception: If login fails
        """
        # Try to load cached session
        # Check if garth session files exist
        oauth1_file = self.credentials_dir / "oauth1_token.json"
        oauth2_file = self.credentials_dir / "oauth2_token.json"

        if oauth1_file.exists() and oauth2_file.exists():
            try:
                self.client = self._load_cached_session()
                if self._test_connection():
                    print("Using cached Garmin Connect session")
                    return self.client
                else:
                    print("Cached session expired, logging in again...")
            except Exception as e:
                print(f"Failed to load cached session: {e}")

        # Fresh login required
        if not email or not password:
            # Try to load from environment file
            env_file = self.credentials_dir / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                email = os.getenv("GARMIN_EMAIL")
                password = os.getenv("GARMIN_PASSWORD")

            # If still missing, prompt interactively
            if not email or not password:
                # Check if running in interactive terminal
                import sys
                if not sys.stdin.isatty():
                    raise Exception("Session expired. Please provide email and password, or run interactively.")

                print("\nGarmin Connect credentials required")
                email = input("Email: ").strip()
                password = getpass.getpass("Password: ")

        try:
            self.client = Client()
            self.client.login(email, password)
            print("Successfully logged in to Garmin Connect")
            self._save_session()
            return self.client
        except GarthHTTPError as e:
            raise Exception(f"Garmin login failed: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during login: {e}")

    def logout(self):
        """Clear cached session"""
        oauth1_file = self.credentials_dir / "oauth1_token.json"
        oauth2_file = self.credentials_dir / "oauth2_token.json"

        if oauth1_file.exists():
            oauth1_file.unlink()
        if oauth2_file.exists():
            oauth2_file.unlink()
        # Also remove old pickle file if it exists
        if self.credentials_file.exists():
            self.credentials_file.unlink()

        self.client = None
        print("Logged out and cleared cached session")

    def _save_session(self):
        """Save authenticated session to disk"""
        if not self.client:
            return

        try:
            # Use garth's built-in dump method to save session
            self.client.dump(str(self.credentials_dir))
            print(f"Session saved to {self.credentials_dir}")
        except Exception as e:
            print(f"Warning: Failed to save session: {e}")

    def _load_cached_session(self) -> Client:
        """Load previously saved session from disk"""
        client = Client()
        # Use garth's built-in load method to restore session
        client.load(str(self.credentials_dir))
        return client

    def _test_connection(self) -> bool:
        """
        Test if current session is still valid

        Returns:
            True if session is valid, False otherwise
        """
        if not self.client:
            return False

        try:
            # Try a simple API call to test the connection
            # Use the workout list endpoint as it's lightweight
            self.client.request("GET", "connectapi", "/workout-service/workouts?limit=1", api=True)
            return True
        except Exception:
            return False

    def get_client(self) -> Optional[Client]:
        """Get the current authenticated client"""
        return self.client
