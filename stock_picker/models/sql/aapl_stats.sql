{{ config(materialized='table') }}

select 
    ticker
    ,date
    ,open
    ,close
    ,low
    ,high
    ,volume
    -- smas 
    ,avg(close) over (order by date rows between 9 preceding and current row) as sma10    --sma 10
    ,avg(close) over (order by date rows between 24 preceding and current row) as sma25   --sma 25
    ,avg(close) over (order by date rows between 49 preceding and current row) as sma50   --sma 50 
    ,avg(close) over (order by date rows between 99 preceding and current row) as sma100  --sma 100
    -- standard deviations 
    ,stddev(close) over (order by date rows between 9 preceding and current row) as std10    --std 10
    ,stddev(close) over (order by date rows between 24 preceding and current row) as std25    --std 10
    ,stddev(close) over (order by date rows between 49 preceding and current row) as std50    --std 10
    ,stddev(close) over (order by date rows between 99 preceding and current row) as std100   --std 10
    -- diffs 
    , close - sma10 as diff10
    , close - sma25 as diff25
    , close - sma50 as diff50
    , close - sma100 as diff100
    -- z-scores
    , (close - sma10) / std10 as z10
    , (close - sma25) / std25 as z25
    , (close - sma50) / std50 as z50
    , (close - sma100) / std100 as z100 




from {{ref('aapl')}}
where ticker='AAPL'