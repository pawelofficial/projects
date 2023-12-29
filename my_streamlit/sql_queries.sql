
with cte as ( 
select Z_COMB, case when z_comb between -2.5 and 2.5 then 1 else 0 end as islow
, CLOSE, DATE , TICKER 
from stats where ticker ='SINX'
),cte2 as ( 
select Z_COMB, TICKER, close, islow,  max(islow) over (PARTITION BY TICKER  order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW ) as next_ten
,date 
 from cte 
 order by date 
)
,cte3 as ( 
 select Z_COMB, close, islow, next_ten, next_ten*sum(next_ten) over (PARTITION BY TICKER   order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as hodl_start  ,date
,TICKER
from cte2   
order by date 
) 
,CTE4 AS ( 
select Z_COMB, close, islow, next_ten
, case when hodl_Start = 1 then 1 else 0 end as hodl_startt
, next_ten*sum(hodl_startt) over (PARTITION BY TICKER  order by date) as which_event
, sum(next_ten) over (PARTITION BY TICKER  order by date ) as next_ten_sum
,date
,TICKER 
from cte3
order by date 
)
,cte5 as ( 
select Z_COMB, close,islow,next_ten,hodl_startt,which_event,next_ten_sum*next_ten as pre_index
,next_ten*lag(next_ten_sum,1) over (PARTITION BY TICKER  order by date ) as lagged_sum
,date
,TICKER 
from cte4 
order by date 
)
,helpful_cte as ( 
select TICKER, which_event,min(lagged_sum) as min_lagged_sum
from cte5 
group by all 
order by 1 
),cte6 as  ( 
select 
cte5.* 
,hcte.min_lagged_sum
from cte5 
left join helpful_cte hcte 
    on cte5.which_event = hcte.which_event
    AND CTE5.TICKER = HCTE.TICKER
order by date 
), CTE7 AS ( 
select cte6.*
,pre_index-min_lagged_sum as index
from  cte6 
order by TICKER,date 
)
SELECT Z_COMB,TICKER, DATE, CLOSE, INDEX , HODL_STARTT, NEXT_TEN 
FROM CTE7
ORDER BY TICKER,DATE

-- when hodl start == 1 then hodl starts 
-- in snowpark  loop over which_event to get your series ! 
;


SELECT TICKER, MAX(DATEADD('day', -1, "DATE"))::date::varchar as DATE_STR  FROM DATA GROUP BY ALL
;
TRUNCATE TABLE DATA;;


select TICKER,COUNT(*)  from data
GROUP BY ALL ;


select * from data 
where 
;

create or replace table data_backup as select * from data;
delete from stats where ticker !='AISP';