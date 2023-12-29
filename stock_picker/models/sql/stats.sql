{{ config(materialized='table') }}
with cte as ( 
select 
    ticker
    ,to_timestamp_ntz(date) date 
    ,open
    ,close
    ,low
    ,high
    ,volume
    -- smas 
    ,avg(close) over (partition by ticker order by date rows between 9 preceding and current row) as sma10    --sma 10
    ,avg(close) over (partition by ticker order by date rows between 24 preceding and current row) as sma25   --sma 25
    ,avg(close) over (partition by ticker order by date rows between 49 preceding and current row) as sma50   --sma 50 
    ,avg(close) over (partition by ticker order by date rows between 99 preceding and current row) as sma100  --sma 100
    -- standard deviations 
    ,stddev(close) over (partition by ticker order by date rows between 9 preceding and current row) as std10    --std 10
    ,stddev(close) over (partition by ticker order by date rows between 24 preceding and current row) as std25    --std 10
    ,stddev(close) over (partition by ticker order by date rows between 49 preceding and current row) as std50    --std 10
    ,stddev(close) over (partition by ticker order by date rows between 99 preceding and current row) as std100   --std 10
    
    , close - sma10 as diff10
    , close - sma25 as diff25
    , close - sma50 as diff50
    , close - sma100 as diff100
    -- z-scores
, (close - sma10) / NULLIF(std10,   0) as z10
, (close - sma25) / NULLIF(std25,   0) as z25
, (close - sma50) / NULLIF(std50,   0) as z50
, (close - sma100) / NULLIF(std100, 0) as z100 
, ( z10+z25+z50+z100  ) / 4.0 as z_comb

from {{ref('data')}}
)
,cte2 as ( 
select cte.*     
    , percent_rank() over (partition by ticker order by z10) as z10_prank
    , percent_rank() over (partition by ticker order by z25) as z25_prank
    , percent_rank() over (partition by ticker order by z50) as z50_prank
    , percent_rank() over (partition by ticker order by z100) as z100_prank
    -- ranks 
    , rank() over (partition by ticker order by z10) as z10_rank
    , rank() over (partition by ticker order by z25) as z25_rank
    , rank() over (partition by ticker order by z50) as z50_rank
    , rank() over (partition by ticker order by z100) as z100_rank
    -- rank sum, rank mean 
    ,z10_rank+z25_rank+z50_rank+z100_rank as rank_sum
    ,rank_sum/4.0 as rank_mean
    --prank sum, prank mean 
    ,z10_prank+z25_prank+z50_prank+z100_prank as prank_sum
    ,prank_sum/4.0 as prank_mean
    from cte 
WHERE std10 is not null -- skipping first row 
) select cte2.*
    -- rank of rank_sum 
    ,rank() over (partition by ticker order by rank_sum) as rank_rank_sum
    ,rank() over (partition by ticker order by rank_mean) as rank_rank_mean
    -- rank of prank_sum
    ,rank() over (partition by ticker order by prank_sum) as rank_prank_sum
    ,rank() over (partition by ticker order by prank_mean) as rank_prank_mean


from cte2
