with ag as (
select ticker ag_ticker ,max(close) as max_close, min(close) as min_close
from stats
group by ag_ticker
)
, cte as (
select z100 AS METRIC, case when METRIC between -4.0600000000000005 and -3.06 then 1 else 0 end as islow
, (CLOSE - min_close) / ( max_close - min_close) as close 
, DATE , TICKER
from stats 
inner join ag 
    on stats.ticker=ag.ag_ticker
)
SELECT * FROM CTE 
WHERE CLOSE < 0 
;


;
with ag as (
select ticker ag_ticker ,max(close) as max_close, min(close) as min_close
from stats
group by ag_ticker
)
, cte as (
select z100 AS METRIC, case when METRIC between -4.0600000000000005 and -3.06 then 1 else 0 end as islow
, CLOSE - min_close / ( max_close - min_close) as norm_close,close 
, DATE , TICKER
from stats 
inner join ag 
    on stats.ticker=ag.ag_ticker
--where ticker in ('AISP','ATAKU','BROG','FBL','BRLIU','BJDX','CLOEU','AFRI','BRLI','BNZI','AMDS','FEXDU','BCEL','AIMD','CNGLU','DWSH','AAPB','CNEY','GATEU','ATAK','HYW','HCTI','BIS','DDI','ALVR','ECDA','CLNN','COEP','CACO','IMNN','EVOK','BLUE','BZFD','BZUN','GEGGL','BCAN','DPRO','CMPX','HALL','CHNR','EBIX','HTHT','ACAX','FRES','ARGX','HCDI','GHSI','INDP','GENE','AADI','CRCT','FAZE','AMPGW','CSTE','FAAR','ADN','DRMA','HNVR','ABIO','ENTX','ARKR','ADVM','AEY','HUGE','CELU','COMT','HNRG','EXC','FRZA','BFRI','CIZN','GGLS','CHEK','CMND','CRVO','EM','HGAS','CLST','IFBD','CSSEN','CVAC','FMST','ASLE','GDHG','CYCC','BCSAU','AMZD','ENG','ESLA','AXDX','ASYS','ELBM','DUOT','CUEN','GOGO','FRSX','ACGL','APPF','GFAI','ALTUW','ELWS','BLMN','FOLD','CODX','ATNI','HOTH','HAYN','CADL','BLBD','DMTK','GAINN','GLYC','BWBBP','FSBC','ATLX','FGF','EFSCP','APM','CONL','ELDN','ALTR','GCT','ADEA','ADAP','AEYE','CLSK','DLHC','DJCO','BITF','INBX','BITS','BHRB','AXSM','AUTL','BBIO','FMAO','BWB','BNIX','CAN','CVRX','BANX','ARBB','BPOPM','ANDE','BLIN','ABUS','ATOS','GREEL','GRNQ','GRPH','BTDR','ESPR','HYMCL','CPRX','CDAQ','HERD','ALT','GIFI','AVTE','HLVX','ABTS','FDIG','IMNM','CALT','BKCH','ANSS','GTX','FEXD','FTFT','ACIC','HIVE','ACIU','DAPP','FGI','CIFR','BTCT','ANNX','FSTR','HOWL','ACNT','DSKE','ARBK','BTBT','GDTC','HUT','EAC','GRCL','BCAB','FUSN','ABSI','BTCS','ANY','EBON','DGHI','ACST','GREE','IINNW','EWTX','HCVIU','CYTK')
),cte2 as (
select METRIC, TICKER, norm_close,close , islow,  max(islow) over (PARTITION BY TICKER  order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW ) as next_ten
,date
 from cte
 order by date
)
,cte3 as (
 select METRIC, norm_close,close , islow, next_ten, next_ten*sum(next_ten) over (PARTITION BY TICKER   order by date ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as hodl_start  ,date
,TICKER
from cte2
order by date
)
,CTE4 AS (
select METRIC, norm_close,close , islow, next_ten
, case when hodl_Start = 1 then 1 else 0 end as hodl_startt
, next_ten*sum(hodl_startt) over (PARTITION BY TICKER  order by date) as which_event
, sum(next_ten) over (PARTITION BY TICKER  order by date ) as next_ten_sum
,date
,TICKER
from cte3
order by date
)
,cte5 as (
select METRIC, norm_close,close ,islow,next_ten,hodl_startt,which_event,next_ten_sum*next_ten as pre_index
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
SELECT METRIC,TICKER, DATE, norm_close,close , INDEX , HODL_STARTT HODL_START, NEXT_TEN
FROM CTE7
where metric <=-4.5
ORDER BY TICKER,DATE
-- when hodl start == 1 then hodl starts
-- in snowpark  loop over which_event to get your series !
;

