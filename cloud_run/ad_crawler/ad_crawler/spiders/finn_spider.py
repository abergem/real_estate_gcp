'''Spider to scrape Finn'''

import os
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import logging

# prevent verbose logging from selenium
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

class FinnSpider(scrapy.Spider):
    name = 'finn_ads'
    

    def __init__(self, **kwargs):
        
        # headless firefox webdriver
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        
        super(FinnSpider, self).__init__(**kwargs)
        url = kwargs.get('url')

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.request_ads)

    def request_ads(self, response):
        logging.info(f'Crawling {response.url}')
        # Follow links to each ad
        # for href in response.css('article.ads__unit a::attr(href)').getall():
        for href in [response.css('article.ads__unit a::attr(href)').get()]:
            # Only follow URLs with 'finnkode' (there are other links as well)
            if 'finnkode' in href:
                yield response.follow(href, callback=self.parse_ad)

    def parse_ad(self, response):

        def extract_digits(string):
            return re.sub('\D', '', string)

        # Use selenium to click on js button
        self.driver.get(response.url)
        logging.info(f'Scraping data from {response.url}')
        expand_data_button = self.driver.find_element_by_xpath('//button[@id="_expand"]')
        expand_data_button.click()
        d = {}
        d['finn_code'] = response.url.split('=')[1]
        
        # Extract key info
        for i, _ in enumerate(response.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dt').getall()):
            field = response.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dt[{i+1}]/text()').get()
            value = extract_digits(response.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dd[{i+1}]').get())
            if field == 'Omkostninger':
                d['fees'] = value
            elif field == 'Totalpris':
                d['total_price'] = value
            elif field == 'Felleskost/mnd.':
                d['overheads'] = value
            elif field == 'Fellesgjeld':
                d['joint_debt'] = value

        # Extract more key info (after clicking the <flere detaljer> button)
        for i, _ in enumerate(response.xpath('//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt').getall()):
            field = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt[{i}]/text()').get()
            value = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dd[{i}]/text()').get()
            
            if field == 'Rom':
                d['rooms'] = value
            elif field == 'Tomteareal':
                d['lot_space'] = extract_digits(value)
            elif field == 'Bruttoareal':
                d['gross_floor_space'] = extract_digits(value)
            elif field == 'Fellesformue':
                d['joint_capital'] = value
            elif field == 'Formuesverdi':
                d['asset_value'] = value
        

        # Adresse
        d['address'] = response.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()').get()
        # Pris
        d['price'] = extract_digits(response.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()').get())
        # Type eiendom
        d['type'] = response.xpath('//section[@class="panel"][2]//dd/text()').get()
        # Eieform
        d['tenure'] = response.xpath('//section[@class="panel"][2]//dd[2]/text()').get()
        # Antall soverom
        d['bedrooms'] = response.xpath('//section[@class="panel"][2]//dd[3]/text()').get()
        # Primærrom
        d['net_internal_area'] = extract_digits(response.xpath('//section[@class="panel"][2]//dd[4]/text()').get())
        # Bruksareal
        d['gross_internal_area'] = extract_digits(response.xpath('//section[@class="panel"][2]//dd[5]/text()').get())
        # Etasje
        d['floor'] = response.xpath('//section[@class="panel"][2]//dd[6]/text()').get()
        # Byggeår
        d['year_of_construction'] = response.xpath('//section[@class="panel"][2]//dd[7]/text()').get()
        # Energimerking
        d['energy_class'] = response.xpath('//section[@class="panel"][2]//dd[8]/text()').get()
        # Sist endret
        d['last_edited'] = response.xpath('//section[@aria-labelledby="ad-info-heading"]//tr/td/text()').get()

        self.logger.info(d)

        yield d