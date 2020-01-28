'''Spider to scrape Finn'''


import scrapy
import re

class FinnSpider(scrapy.Spider):
    name = 'Finn'
    start_urls = [
        'https://www.finn.no/realestate/homes/search.html?location=0.20061'
    ]

    def parse(self, response):
        # follow links to each ad
        # for href in response.css('article.ads__unit a::attr(href)').getall():
        for href in [response.css('article.ads__unit a::attr(href)').get()]:
            if 'finnkode' in href:
                yield response.follow(href, callback=self.parse_ad)

        next_page = response.xpath('//a[@aria-label="Neste side"]/@href').get()
        print(next_page)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(sef, response):

        def extract_digits(string):
            return re.sub('\D', '', string)

        yield {
            
            'address': response.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()').get(),
            'price': extract_digits(response.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()').get()),
            'fees': extract_digits(response.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dd').get()),
            'total_price': extract_digits(response.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dd[2]').get()),
            'overheads': extract_digits(response.xpath('//div[@class="panel"]//dl[@class="definition-list"]/dd[3]').get()),
            'type': response.xpath('//section[@class="panel"][2]//dd/text()').get(),
            'tenure': response.xpath('//section[@class="panel"][2]//dd[2]/text()').get()
        }