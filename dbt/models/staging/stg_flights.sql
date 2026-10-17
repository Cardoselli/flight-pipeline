{{ config(materialized='view', schema='staging') }}

with source as (
    select * from raw.flights
),

renamed as (
    select
        -- identifiers
        icao24,
        trim(callsign) as callsign,
        origin_country,

        -- timestamps (Unix → timestamp)
        to_timestamp(snapshot_time) as snapshot_time,
        to_timestamp(time_position) as time_position,
        to_timestamp(last_contact) as last_contact,

        -- position
        longitude,
        latitude,

        -- altitude
        baro_altitude,
        geo_altitude,

        -- status
        on_ground,
        velocity,
        true_track,
        vertical_rate,

        -- metadata
        squawk,
        spi,
        position_source,

        -- ingestion
        ingested_at
    from source
)

select * from renamed
