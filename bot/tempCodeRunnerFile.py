            select * from live_data hd 
            where timestamp = ( select max ( timestamp) from live_data  hd2 )