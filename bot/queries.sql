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