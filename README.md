# Flight Pipeline

A modern data pipeline that extracts real-time flight data from OpenSky Network, loads it into PostgreSQL, transforms it with dbt, orchestrates it with Airflow, and visualizes it with Metabase.

## Architecture

OpenSky API -> Python -> PostgreSQL (raw) -> dbt -> Star Schema -> Metabase
                              ^
                     (Orchestrated by Airflow)

## Stack

- Ingestion: Python, requests
- Storage: PostgreSQL 16
- Transformation: dbt
- Orchestration: Apache Airflow
- Visualization: Metabase
- Containerization: Docker, Docker Compose

## Project Structure

```
flight-pipeline/
├── docker/              # Docker Compose files
├── ingestion/           # Python extraction and load scripts
├── dbt/                 # dbt models (staging, intermediate, marts)
├── airflow/             # Airflow DAGs
├── scripts/             # Utility scripts
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md
```


### Prerequisites

- Docker
- Docker Compose
- Python 3.10+

### Setup

1. Clone the repository:
   git clone https://github.com/your-username/flight-pipeline.git
   cd flight-pipeline

2. Copy the environment template and fill in your credentials:
   cp .env.example .env

3. Start the containers:
   cd docker
   docker compose up -d

4. Access Adminer (database GUI) at http://localhost:8080

### Database credentials

- System: PostgreSQL
- Server: postgres
- Username: (from .env)
- Password: (from .env)
- Database: (from .env)

## What This Project Demonstrates

- Extraction from external APIs with rate limiting
- Loading raw data into a data warehouse
- Structured transformations with dbt
- Star Schema modeling (fact and dimension tables)
- Pipeline orchestration with Airflow
- Data quality testing
- Containerized development environment


