"""
OpenSky OAuth2 authentication.

Handles token retrieval and automatic refresh for the OpenSky Network API.

Usage:
    from ingestion.opensky_auth import TokenManager
    tokens = TokenManager()
    headers = tokens.headers()
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env in the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# OpenSky OAuth2 token endpoint
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

# Refresh the token 30 seconds before it expires
TOKEN_REFRESH_MARGIN = 30


class TokenManager:
    """Manages OpenSky OAuth2 tokens with automatic refresh."""

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("OPENSKY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OPENSKY_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "OPENSKY_CLIENT_ID and OPENSKY_CLIENT_SECRET must be set in .env"
            )

        self.token = None
        self.expires_at = None

    def get_token(self):
        """Return a valid access token, refreshing if necessary."""
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self):
        """Fetch a new access token from OpenSky."""
        logger.debug("Refreshing OpenSky access token...")

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self.expires_at = datetime.now() + timedelta(
            seconds=expires_in - TOKEN_REFRESH_MARGIN
        )

        logger.debug(f"Token refreshed, expires at {self.expires_at}")
        return self.token

    def headers(self):
        """Return HTTP headers with a valid Bearer token."""
        return {"Authorization": f"Bearer {self.get_token()}"}
