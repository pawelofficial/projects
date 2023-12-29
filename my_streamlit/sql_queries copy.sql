
with cte as ( 
select  close, case when close < -1 then 1 else 0 end as islow
,* exclude(close) from stats where ticker ='SINX'
order by date 
),cte2 as ( 
select close, islow,  max(islow) over ( order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW ) as next_ten
,date 
 from cte 
 order by date 
)
,cte3 as ( 
 select close, islow, next_ten, next_ten*sum(next_ten) over (  order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as hodl_start  ,date
from cte2 
order by date 
) 
,CTE4 AS ( 
select close, islow, next_ten
, case when hodl_Start = 1 then 1 else 0 end as hodl_startt
, next_ten*sum(hodl_startt) over ( order by date) as which_event
, sum(next_ten) over ( order by date ) as next_ten_sum
,date
from cte3
order by date 
)
,cte5 as ( 
select close,islow,next_ten,hodl_startt,which_event,next_ten_sum*next_ten as pre_index
,next_ten*lag(next_ten_sum,1) over ( order by date ) as lagged_sum
,date
from cte4 
order by date 
)
,helpful_cte as ( 
select which_event,min(lagged_sum) as min_lagged_sum
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
order by date 
)
select cte6.*
,pre_index-min_lagged_sum as index
from  cte6 
order by date 


-- when hodl start == 1 then hodl starts 
-- in snowpark  loop over which_event to get your series ! 