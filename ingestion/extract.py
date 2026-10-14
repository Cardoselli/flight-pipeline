"""
Extract current flight states from OpenSky Network API.

Fetches all active flights worldwide and saves the raw JSON response
to data/raw/ with a timestamp in the filename.

Usage:
    python -m ingestion.extract
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from loguru import logger

from ingestion.opensky_auth import TokenManager

# OpenSky API endpoint for all state vectors
OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"

# Output directory for raw JSON files
RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


def fetch_states(tokens):
    """Fetch all current state vectors from OpenSky."""
    logger.info("Fetching all flight states from OpenSky...")

    response = requests.get(
        OPENSKY_STATES_URL,
        headers=tokens.headers(),
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    n_states = len(data.get("states") or [])
    logger.success(f"Received {n_states} flight states")

    return data


def save_raw_json(data):
    """Save the raw JSON response to data/raw/ with a timestamped filename."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = RAW_DATA_DIR / f"opensky_{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.success(f"Saved raw JSON to {filepath}")
    return filepath


def main():
    """Extract flight states and save them to disk."""
    try:
        tokens = TokenManager()
        data = fetch_states(tokens)
        save_raw_json(data)
        logger.success("Extraction completed successfully")

    except requests.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
