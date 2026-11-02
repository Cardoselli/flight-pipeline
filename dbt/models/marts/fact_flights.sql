{{ config(materialized='table', schema='marts') }}

with flights as (
    select
        f.icao24,
        f.origin_country,
        f.snapshot_time,
        f.latitude,
        f.longitude,
        f.baro_altitude,
        f.geo_altitude,
        f.on_ground,
        f.velocity,
        f.true_track,
        f.vertical_rate,
        f.squawk,
        f.spi,
        f.position_source,
        f.callsign,
        a.aircraft_key,
        c.country_key,
        t.time_key
    from {{ ref('stg_flights') }} f
    left join {{ ref('dim_aircraft') }} a
        on f.icao24 = a.icao24
    left join {{ ref('dim_country') }} c
        on f.origin_country = c.origin_country
    left join {{ ref('dim_time') }} t
        on f.snapshot_time = t.snapshot_time
)

select
    row_number() over (order by snapshot_time, icao24) as flight_key,
    aircraft_key,
    country_key,
    time_key,
    latitude,
    longitude,
    baro_altitude,
    geo_altitude,
    on_ground,
    velocity,
    true_track,
    vertical_rate,
    squawk,
    spi,
    position_source,
    callsign
from flights
