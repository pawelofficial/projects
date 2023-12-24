
import requests
from bs4 import BeautifulSoup
import pandas as pd 


def model(dbt , session ):
    dbt.config(
        packages = ["numpy==1.23.1", "requests==2.27.1","pandas==1.4.2","beautifulsoup4==4.11.1"]    
        ,materialized="table"
    )
    #import pandas 
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    return df 


