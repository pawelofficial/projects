import unittest
from scraper import *
import scraper as sc 
import asyncio
import logging  
import ast 
from urllib.parse import urlparse
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
                    ,filename='./tests/test_scraper.log',filemode='w'
                    )

logger=logging.getLogger(__name__)
logger.info('Start of program')



class TestScraper(unittest.TestCase):
    def setUp(self):
        self.offers_url='https://www.otomoto.pl/osobowe/alfa-romeo/mito?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=35000&search%5Border%5D=created_at_first%3Adesc'
        logger.info(f'self.offers_url={self.offers_url}')

        from_web=True
        if from_web:
            logger.info('setting up from web ')
            self.offers_fetch_d, s = asyncio.run(sc.get_offers_from_offers_url(self.offers_url))
            self.offer_soup=self.offers_fetch_d[list(self.offers_fetch_d.keys())[0]]['soup']
        # read soup from file 
        else:    
            logger.info('setting up from file ')
            self.offers_fetch_d=sc.load_json('./tests/offers_fetch_d.json')
                        
            with open('./tests/offer_soup.html', 'r',encoding="utf-8") as file:
                self.offer_soup = file.read()
                self.offer_soup=BeautifulSoup(self.offer_soup,'html.parser')


    ###def test_get_offers_from_offers_url(self):
    ###    self.offers_fetch_d, s = asyncio.run(sc.get_offers_from_offers_url(self.offers_url))
    ###    logger.info(f'self.offers_fetch_d={self.offers_fetch_d}')
    ###    offers_list=list(self.offers_fetch_d.keys())
    ###    logger.info(f'offers_list={offers_list}')
    ###    self.assertTrue(offers_list!=[] )
    ###    sc.dump_json(self.offers_fetch_d,'./tests/offers_fetch_d.json')
#
    def test_get_data_from_offer(self,which=2):
        self.offer_soup=self.offers_fetch_d[list(self.offers_fetch_d.keys())[which]]['soup']
        logger.info(f'self.offer_soup={self.offer_soup}')
        # dump soup to file 
        with open('./tests/offer_soup.html', 'w',encoding="utf-8") as file:
            file.write(str(self.offer_soup))
        # assert soup is not none 
        self.assertTrue(self.offer_soup!=None)
        

    # checks if offer details get parsed correctly 
    def test_get_tag_contents_offer_details(self):
        soup=self.offer_soup
        url=soup.find_all('meta', property='og:url')[0]['content']
        logger.info(f'url: {url}')
        class_='content-details-section'
        offer_details,_,_=get_tag_contents(soup
                        ,tag='div'
                        ,attrs={'data-testid': class_}
                        ,sub_tags=['p','a'])
        logger.info(f'offer_details: {offer_details}')
        logger.info(f'soup: {soup}')
        assert(offer_details != None) 
        
    def test_get_tag_contents_tytul(self,soup=None ):
        if soup==None:
            soup=self.offer_soup
        url=soup.find_all('meta', property='og:url')[0]['content']
        logger.info(f'url: {url}')
        
        class_='ooa-3w0yoi e1aiyq9b3'
        data,txt,_=get_tag_contents(soup
                           ,tag='div'
                           ,attrs={'class': class_}
                           ,sub_tags=['h3']
                           )
        
        logger.info(f'tytul: {data}')
        logger.info(f'txt: {txt}')
        logger.info(f'_: {_}')
        logger.info(f'soup: {soup}')
        assert(data != None) 
        



if __name__ == '__main__':
    #with open('./tests/offer_soup.html', 'r',encoding="utf-8") as file:
    #    offer_soup = file.read()
    #    offer_soup=BeautifulSoup(offer_soup,'html.parser')
    
    t=TestScraper()
    t.setUp()
    #t.test_get_data_from_offer()
    #t.test_get_tag_contents_offer_details()
    t.test_get_tag_contents_tytul()
#    unittest.main(buffer=False)