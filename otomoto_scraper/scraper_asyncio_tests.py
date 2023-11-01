import scraper_asyncio as sa 
import asyncio 

with open('./data/links.txt','r') as f:
    links=f.readlines()
    LINKS=[l.strip() for l in links][:5]
    


## test 1 -> fetch all 
#asyncio.run(sa.fetch_all(LINKS))

## test 2 -> parallel fetch nicely
#fetch_d, s = asyncio.run(sa.parallel_fetch_nicely(LINKS))

