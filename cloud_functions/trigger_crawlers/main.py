from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from trigger_crawlers.spiders.trigger_crawlers import CrawlerTrigger

def start_crawler_trigger(event=None, context=None):
    '''Pub-sub triggered GCF to initiate crawling jobs'''

    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlerTrigger)
    process.start()

if __name__ == '__main__':

    start_crawler_trigger()