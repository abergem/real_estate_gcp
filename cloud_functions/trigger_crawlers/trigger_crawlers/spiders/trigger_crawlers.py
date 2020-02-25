'''Spider to trigger crawlers'''

import scrapy
import requests

class CrawlerTrigger(scrapy.Spider):
    name = 'trigger_crawlers'

    def start_requests(self):
        main_page_url = 'https://www.finn.no/realestate/homes/search.html?location=0.20061'
        
        yield scrapy.Request(url=main_page_url, callback=self.trigger_crawler)

    def trigger_crawler(self, response):
        
        self.logger.info(f'Triggering crawler for {response.url}')
        payload = {'url': response.url}
        cloud_run_url = f'https://adcrawler-e2ofq27tbq-ew.a.run.app'
        headers = {'Content-Type': 'application/json'}
        r = requests.post(cloud_run_url, json=payload, headers=headers)

        next_page = response.xpath('//a[@aria-label="Neste side"]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.trigger_crawler)