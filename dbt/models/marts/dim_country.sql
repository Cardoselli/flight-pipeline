{{ config(materialized='table', schema='marts') }}

with countries as (
    select distinct
        origin_country
    from {{ ref('stg_flights') }}
    where origin_country is not null
)

select
    row_number() over (order by origin_country) as country_key,
    origin_country
from countries
