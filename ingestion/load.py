"""
Load raw OpenSky JSON data into PostgreSQL.

Reads the most recent JSON file from data/raw/ and inserts the flight
states into the raw.flights table in PostgreSQL.

Usage:
    python -m ingestion.load
"""

import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env in the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Directory with raw JSON files
RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Table name (schema + table)
RAW_TABLE = "raw.flights"


def get_latest_raw_file():
    """Find the most recent JSON file in data/raw/."""
    files = sorted(RAW_DATA_DIR.glob("opensky_*.json"))
    if not files:
        raise FileNotFoundError(f"No JSON files found in {RAW_DATA_DIR}")
    return files[-1]


def load_json(filepath):
    """Load the JSON file and return the parsed data."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_db_connection():
    """Create a connection to PostgreSQL using .env credentials."""
    return psycopg.connect(
        host="localhost",
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )


def create_raw_schema_and_table(conn):
    """Create the raw schema and flights table if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
                snapshot_time     BIGINT,
                icao24            TEXT,
                callsign          TEXT,
                origin_country    TEXT,
                time_position     BIGINT,
                last_contact      BIGINT,
                longitude         DOUBLE PRECISION,
                latitude          DOUBLE PRECISION,
                baro_altitude     DOUBLE PRECISION,
                on_ground         BOOLEAN,
                velocity          DOUBLE PRECISION,
                true_track        DOUBLE PRECISION,
                vertical_rate     DOUBLE PRECISION,
                sensors           INT[],
                geo_altitude      DOUBLE PRECISION,
                squawk            TEXT,
                spi               BOOLEAN,
                position_source   INT,
                ingested_at       TIMESTAMPTZ DEFAULT NOW()
            );
        """)
    conn.commit()
    logger.info(f"Ensured schema 'raw' and table '{RAW_TABLE}' exist")


def insert_flights(conn, snapshot_time, states):
    """Insert flight states into raw.flights."""
    if not states:
        logger.warning("No states to insert")
        return 0

    rows = []
    for s in states:
        s = s + [None] * (18 - len(s))
        rows.append((
            snapshot_time,
            s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8],
            s[9], s[10], s[11], s[12], s[13], s[14], s[15], s[16],
        ))

    with conn.cursor() as cur:
        cur.executemany(f"""
            INSERT INTO {RAW_TABLE} (
                snapshot_time, icao24, callsign, origin_country,
                time_position, last_contact, longitude, latitude,
                baro_altitude, on_ground, velocity, true_track,
                vertical_rate, sensors, geo_altitude, squawk, spi,
                position_source
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, rows)
    conn.commit()
    return len(rows)


def main():
    """Load the latest raw JSON into PostgreSQL."""
    try:
        filepath = get_latest_raw_file()
        logger.info(f"Loading raw JSON: {filepath}")

        data = load_json(filepath)
        snapshot_time = data.get("time")
        states = data.get("states") or []

        if snapshot_time is None:
            logger.error("Missing 'time' field in JSON")
            sys.exit(1)

        conn = get_db_connection()
        create_raw_schema_and_table(conn)
        n_loaded = insert_flights(conn, snapshot_time, states)
        conn.close()

        logger.success(f"Loaded {n_loaded} flights into {RAW_TABLE}")
        logger.success("Load completed successfully")

    except Exception as e:
        logger.error(f"Load failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
