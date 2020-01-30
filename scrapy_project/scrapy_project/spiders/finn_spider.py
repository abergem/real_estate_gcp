'''Spider to scrape Finn'''


import scrapy
from selenium import webdriver
import re
import logging

class FinnSpider(scrapy.Spider):
    name = 'Finn'
    start_urls = [
        'https://www.finn.no/realestate/homes/search.html?location=0.20061'
    ]

    def __init__(self):
        self.driver = webdriver.Firefox()

    def parse(self, response):
        logging.info(f'Crawling {response.url}')
        # follow links to each ad
        # for href in response.css('article.ads__unit a::attr(href)').getall():
        for href in [response.css('article.ads__unit a::attr(href)').get()]:
            if 'finnkode' in href:
                yield response.follow(href, callback=self.parse_ad)

        next_page = response.xpath('//a[@aria-label="Neste side"]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):

        def extract_digits(string):
            return re.sub('\D', '', string)

        self.driver.get(response.url)
        logging.info(f'Scraping data from {response.url}')
        expand_data_button = self.driver.find_element_by_xpath('//button[@id="_expand"]')
        expand_data_button.click()
        d = {}
        d['finn_code'] = response.url.split('=')[1]
        
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

        for i, _ in enumerate(response.xpath('//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt').getall()):
            field = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dt[{i}]/text()').get()
            value = response.xpath(f'//div[@data-controller="moreKeyInfo"]//dl[@class="definition-list"]/dd[{i}]/text()').get()
            
            if field == 'Rom':
                d['no_of_rooms'] = value
            elif field == 'Tomteareal':
                d['lot_space'] = extract_digits(value)
            elif field == 'Bruttoareal':
                d['floor_space'] = extract_digits(value)
            elif field == 'Fellesformue':
                d['joint_capital'] = value
            elif field == 'Formuesverdi':
                d['asset_value'] = value
            
            d['address'] = response.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()').get()
            d['price'] = extract_digits(response.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()').get())
            d['type'] = response.xpath('//section[@class="panel"][2]//dd/text()').get()
            d['tenure'] = response.xpath('//section[@class="panel"][2]//dd[2]/text()').get()

        yield d