create or replace procedure  gcp_wrapper( input_address varchar )
returns array
language sql
as
$$
declare 
    foo resultset;
    query varchar default 'SELECT gcptest( ''' ||:input_address||'''  ) ;' ;
    insert_query_tmp varchar default 'insert into gcp_requests_history ( request_string, request_url,raw_response,parsed_response  ) values (?,?,?,?)';

begin 
    select gcptest('foo') into :foo;
     let ar resultset := (execute immediate :query);
     let res2 resultset := (execute immediate :insert_query_tmp USING ( input_address,input_address,input_address,input_address ) );
     
return table(foo);
end;
$$
;


CREATE TABLE dev.signals (
	id serial4 NOT NULL,
	epoch bigint primary key,
	"timestamp" text NULL,
	"open" float8 NULL,
	"close" float8 NULL,
	low float8 NULL,
	high float8 NULL,
	volume float8 NULL,
	wave_signal text NULL,
	dif float8 NULL,
	flat bool NULL,
	green bool NULL,
	ema5 float8 NULL,
	ema10 float8 NULL,
	condition1 text NULL,
	condition2 bool NULL,
	tmp_wave bool NULL,
	tmp_orphans int4 NULL,
	condition3 int4 NULL,
	condition4 bool NULL
);



CREATE TABLE quantiles (
    id SERIAL,
    epoch bigint primary key,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume NUMERIC(10, 6) NOT NULL
,ar int[] NOT NULL
    );