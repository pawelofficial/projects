


def mod5(x: int) -> int:
    return x % 5


def model(dbt , session ):
    dbt.config(
        packages = ["numpy==1.23.1", "requests==2.27.1","pandas==1.4.2","beautifulsoup4==4.11.1"]    
        ,materialized="table"
    )
    #import pandas 
    df = dbt.ref("aapl").apply(mod5)
    # lmao i really dont know how to use snowpark 
    

    return df 


