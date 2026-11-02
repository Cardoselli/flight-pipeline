{{ config(materialized='table', schema='marts') }}

with aircraft as (
    select distinct
        icao24,
        callsign,
        origin_country
    from {{ ref('stg_flights') }}
    where icao24 is not null
)

select
    row_number() over (order by icao24) as aircraft_key,
    icao24,
    callsign,
    origin_country
from aircraft
