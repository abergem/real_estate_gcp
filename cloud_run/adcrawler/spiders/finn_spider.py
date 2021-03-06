'''Spider to scrape Finn


'''

import os
from bs4 import BeautifulSoup
import re
import logging
import json
from google.cloud import storage
from time import sleep
from datetime import datetime
import requests
from requests import Session
from lxml import html
import random

from retry.api import retry_call

def retry_decorator(f):
    def inner(self, *fargs, **fkwargs):
        result = retry_call(f, fargs=(self,)+fargs, fkwargs=fkwargs, tries=self.tries,
                            delay=self.delay, logger=self.logger)
        return result
    return inner

class FinnSpider():

    def __init__(self, logger):
        self.logger = logger
        self.delay = 3
        self.tries = 3
        
        user_agents = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
                       'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
                       'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
                       'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0']
        user_agent = random.choice(user_agents)
        self.headers = {'User-Agent': user_agent}

    @retry_decorator
    def crawl_ads(self, page_url):
        
        # Get all links to ads
        r = requests.get(page_url, headers=self.headers)
        html = r.content
        soup = BeautifulSoup(html, 'html.parser')

        page_results = soup.find_all(class_='ads__unit')
        links = []
        for tag in page_results:
            res = tag.find_all('a')
            try:
                links.append(res[0].get('href'))
            except IndexError:
                pass
        links = ['https://finn.no'+l for l in links if 'finnkode' in l]
        links = [l for l in links if 'homes' in l]
        
        # Parse all ads
        ads_crawled = 0
        for url in links:
            self.parse_ad(url)
            ads_crawled += 1
            sleep(2)
        self.logger.info(f'Crawled {ads_crawled} from {page_url}')


    @retry_decorator
    def parse_ad(self, url):

        d = {}
        finn_code = url.split('=')[1]
        d['finn_code'] = finn_code
        page = requests.get(url, headers=self.headers)
        tree = html.fromstring(page.content)
        
        # Extract price info
        for i, _ in enumerate(tree.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dt')):
            field = tree.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dt[{i+1}]/text()')[0]
            value = self.extract_digits(tree.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dd[{i+1}]/text()')[0])
            if field == 'Omkostninger':
                d['fees'] = value
            elif field == 'Totalpris':
                d['total_price'] = value
            elif field == 'Felleskost/mnd.':
                d['overheads'] = value
            elif field == 'Fellesgjeld':
                d['joint_debt'] = value

        # Adresse
        d['address'] = tree.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()')[0]

        # Pris
        d['price'] = self.extract_digits(tree.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()')[0])
        
        # Extract key info
        selected_fields = ['Boligtype', 'Eieform', 'Soverom', 'Primærrom', 'Bruksareal', 'Etasje',
                  'Byggeår', 'Energimerking', 'Rom', 'Tomteareal', 'Bruttoareal', 'Fellesformue', 'Formuesverdi']

        fields = []
        values = []
        final_fields = []
        final_values = []
        for i, _ in enumerate(tree.xpath('//section[@class="panel"]//dt')):
            fields = tree.xpath(f'//section[@class="panel"]//dt[{i+1}]/text()')
            values = tree.xpath(f'//section[@class="panel"]//dd[{i+1}]/text()')
            for field in fields:
                if field in selected_fields:
                    final_fields.append(field)
                    final_values.append(values[fields.index(field)])

        for field, value in zip(final_fields, final_values):
            d = self.extract_field_value_pairs(field, value, d)

        # Sist endret
        d['last_edited'] = tree.xpath('//section[@aria-labelledby="ad-info-heading"]//tr/td/text()')[0]
        
        # Dump to local /tmp folder
        local_file_path = f'/tmp/{finn_code}.json'
        with open(local_file_path, 'w') as outfile:
            json.dump(d, outfile)
        
        # Upload to cloud storage
        bucket_name = 'advance-nuance-248610-realestate-ads-landing'
        year, month, day = datetime.today().year, datetime.today().month, datetime.today().day
        date_tag = str(year)+str(month)+str(day)
        destination_blob_name = os.path.join('landing', date_tag, finn_code+'.json')

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)


    def extract_field_value_pairs(self, field: str, value: str, d: dict) -> dict:
        # What is usually in 'key info'
        if field == 'Boligtype':
                d['type'] = value
        elif field == 'Eieform':
            d['tenure'] = value
        elif field == 'Soverom':
            d['bedrooms'] = value
        elif field == 'Primærrom':
            d['net_internal_area'] = self.extract_digits(value)
        elif field == 'Bruksareal':
            d['gross_internal_area'] = self.extract_digits(value)
        elif field == 'Etasje':
            d['floor'] = value
        elif field == 'Byggeår':
            d['year_of_construction'] = value
        elif field == 'Energimerking':
            d['energy_class'] = '' # TODO 
        # What is usually in 'more key info', but could come here
        if field == 'Rom':
            d['rooms'] = value
        elif field == 'Tomteareal':
            d['lot_space'] = self.extract_digits(value)
        elif field == 'Bruttoareal':
            d['gross_floor_space'] = self.extract_digits(value)
        elif field == 'Fellesformue':
            d['joint_capital'] = self.extract_digits(value)
        elif field == 'Formuesverdi':
            d['asset_value'] = self.extract_digits(value)

        return d

    def extract_digits(self, string):
        return re.sub('\D', '', string)
