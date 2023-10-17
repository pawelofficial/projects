import os 
# add parent dir to path
import sys
import inspect 
import functools
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging 
logging.basicConfig(level=logging.INFO
                    ,filemode='w'
                    ,format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='./logs/tests.log')
from scraper import * 

def log_test(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        test_name = fn.__name__
        logging.info(f'running test {test_name}')
        
        result = fn(*args, **kwargs)
        
        if result:
            logging.info(f'{test_name} passed')
        else:
            logging.warning(f'{test_name} failed')
        return result
    return wrapped


OFFERS_LIST='https://www.otomoto.pl/osobowe/renault/clio/od-2015?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_fuel_type%5D=petrol&search%5Bfilter_float_mileage%3Ato%5D=100000&search%5Bfilter_float_price%3Afrom%5D=20000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=filter_float_price%3Adesc&search%5Badvanced_search_expanded%5D=true'
OFFER_DETAILS_URL='https://www.otomoto.pl/osobowe/oferta/renault-clio-szukasz-idealu-zapraszam-nawi-tempomat-podgrzewane-fotele-ID6FRmcm.html'


@log_test
def test__get_links_from_site(url=OFFERS_LIST):
    links=get_links_from_site(url )    
    return links !=[]


@log_test
def test__get_soup(url=OFFER_DETAILS_URL):
    soup = get_soup(url)
    return soup != None	


@log_test
def test__get_tag_contents(url=OFFER_DETAILS_URL):
    soup=get_soup(url)
    contents=get_tag_contents(soup)
    return contents != None



if __name__ == "__main__":
    test__get_tag_contents()
#    test__template()
#    test__get_data_from_ffer()