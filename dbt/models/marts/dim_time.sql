{{ config(materialized='table', schema='marts') }}

with times as (
    select distinct
        snapshot_time
    from {{ ref('stg_flights') }}
    where snapshot_time is not null
)

select
    row_number() over (order by snapshot_time) as time_key,
    snapshot_time,
    extract(year from snapshot_time) as year,
    extract(month from snapshot_time) as month,
    extract(day from snapshot_time) as day,
    extract(hour from snapshot_time) as hour,
    extract(minute from snapshot_time) as minute,
    extract(dow from snapshot_time) as day_of_week
from times
