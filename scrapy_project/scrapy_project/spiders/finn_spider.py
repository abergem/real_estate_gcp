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

        d = {}
        for i, _ in enumerate(response.xpath(f'//div[@class="panel"]//dl[@class="definition-list"]/dt').getall()):
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

            d['address'] = response.xpath('//section[@class="panel"]//p[@class="u-caption"]/text()').get()
            d['price'] = extract_digits(response.xpath('//div[@class="panel"]//span[@class="u-t3"]/text()').get())
            d['type'] = response.xpath('//section[@class="panel"][2]//dd/text()').get()
            d['tenure'] = response.xpath('//section[@class="panel"][2]//dd[2]/text()').get()

        yield d