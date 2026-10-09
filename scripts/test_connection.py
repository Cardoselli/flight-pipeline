"""
Test connection to PostgreSQL database.

Usage:
    python scripts/test_connection.py
"""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def test_connection():
    """Test connection to PostgreSQL and print basic info."""
    try:
        conn = psycopg.connect(
            host="localhost",
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
        cursor = conn.cursor()

        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.success(f"Connected to PostgreSQL: {version[:50]}...")

        # Get current database
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        logger.info(f"Current database: {db_name}")

        # Get current user
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()[0]
        logger.info(f"Current user: {user}")

        cursor.close()
        conn.close()
        logger.success("Connection test passed!")

    except Exception as e:
        logger.error(f"Connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
