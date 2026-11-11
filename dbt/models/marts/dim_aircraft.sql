{{ config(materialized='table', schema='marts') }}

with aircraft as (
    select distinct
        icao24,
        callsign,
        origin_country,
        row_number() over (
            partition by icao24
            order by snapshot_time desc
        ) as rn
    from {{ ref('stg_flights') }}
    where icao24 is not null
)

select
    row_number() over (order by icao24) as aircraft_key,
    icao24,
    callsign,
    origin_country
from aircraft
where rn = 1
