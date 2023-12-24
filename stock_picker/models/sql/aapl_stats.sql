{{ config(materialized='table') }}

select 
    date,
    open,
    close,
    low,
    high,
    volume
    
from {{ref('aapl')}}