from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_project.spiders.finn_spider import FinnSpider

process = CrawlerProcess(get_project_settings())
process.crawl(FinnSpider)
process.start()