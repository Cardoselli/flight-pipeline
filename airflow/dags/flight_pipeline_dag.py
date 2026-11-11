"""
Flight Pipeline DAG.

Orchestrates:
  1. extract.py  → fetch flights from OpenSky
  2. load.py     → load into PostgreSQL (raw.flights)
  3. dbt run     → transform into Star Schema
  4. dbt test    → validate data quality

Runs every 15 minutes.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "flight-pipeline",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="flight_pipeline",
    description="Extract, load, transform and test flight data",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule_interval="*/15 * * * *",  # every 15 minutes
    catchup=False,
    max_active_runs=1,
    tags=["flight-pipeline", "opensky", "dbt"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command="cd /opt/airflow && python -m ingestion.extract",
    )

    load = BashOperator(
        task_id="load",
        bash_command="cd /opt/airflow && python -m ingestion.load",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
    )

    extract >> load >> dbt_run >> dbt_test
