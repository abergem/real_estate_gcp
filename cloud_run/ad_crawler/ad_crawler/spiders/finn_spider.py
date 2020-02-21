'''Spider to scrape Finn'''

import os
import scrapy
from selenium import webdriver
import re
import logging
import chromedriver_binary
import json
from google.cloud import storage

# prevent verbose logging from selenium
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

class FinnSpider(scrapy.Spider):
    name = 'finn_ads'
    

    def __init__(self, **kwargs):

        # Set headless Chrome as driver for selenium
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        
        super(FinnSpider, self).__init__(**kwargs)
        self.url = kwargs.get('url')

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.request_ads)

    def request_ads(self, response):
        logging.info(f'Crawling {response.url}')
        # Follow links to each ad on the web page
        for href in response.css('article.ads__unit a::attr(href)').getall():
        # for href in [response.css('article.ads__unit a::attr(href)').get()]:
            # Only follow URLs with 'finnkode' (there are other links as well)
            if 'finnkode' in href:
                yield response.follow(href, callback=self.parse_ad)

    def parse_ad(self, response):

        # Use selenium to click on js button
        self.driver.get(response.url)
        logging.info(f'Scraping data from {response.url}')
        expand_data_button = self.driver.find_element_by_xpath('//button[@id="_expand"]')
        expand_data_button.click()
        d = {}
        finn_code = response.url.split('=')[1]
        d['finn_code'] = finn_code
        
        # Extract price info
        for i, _ in enumerate(response.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dt').getall()):
            field = response.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dt[{i+1}]/text()').get()
            value = self.extract_digits(response.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dd[{i+1}]').get())
            if field == 'Omkostninger':
                d['fees'] = value
            elif field == 'Totalpris':
                d['total_price'] = value
            elif field == 'Felleskost/mnd.':
                d['overheads'] = value
            elif field == 'Fellesgjeld':
                d['joint_debt'] = value
        

        # Adresse
        d['address'] = response.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()').get()
        # Pris
        d['price'] = self.extract_digits(response.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()').get())
        
        # Extract key info
        for i, _ in enumerate(response.xpath('//section[@class="panel"][2]//dt').getall()):
            field = response.xpath(f'//section[@class="panel"][2]//dt[{i}]/text()').get()
            value = response.xpath(f'//section[@class="panel"][2]//dd[{i}]/text()').get()

            d = self.extract_field_value_pairs(field, value, d)

        # Extract more key info (after clicking the <flere detaljer> button)
        for i, _ in enumerate(response.xpath('//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt').getall()):
            field = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt[{i}]/text()').get()
            value = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dd[{i}]/text()').get()
            
            d = self.extract_field_value_pairs(field, value, d)

        # Extract more key info a second time (in case there is another definition list) (after clicking the <flere detaljer> button)
        for i, _ in enumerate(response.xpath('//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"][2]/dt').getall()):
            field = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"][2]/dt[{i}]/text()').get()
            value = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"][2]/dd[{i}]/text()').get()
            
            d = self.extract_field_value_pairs(field, value, d)

        # Sist endret
        d['last_edited'] = response.xpath('//section[@aria-labelledby="ad-info-heading"]//tr/td/text()').get()

        self.logger.info(d)
        
        if not os.path.exists('output'):
            os.makedirs('output')
        file_path = f'output/{finn_code}.json'
        with open(file_path, 'w') as outfile:
            json.dump(d, outfile)
        
        # Upload to cloud storage
        bucket_name = 'advance-nuance248610-realestate-landing'
        source_file_name = file_path
        destination_blob_name = file_path

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)

        self.logger.info(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )
        
        yield d

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
            d['asset_value'] = value

        return d

    def extract_digits(self, string):
        return re.sub('\D', '', string)
