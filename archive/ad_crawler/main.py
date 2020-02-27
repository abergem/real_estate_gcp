import json
import sys
import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ad_crawler.spiders.finn_spider import FinnSpider

from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=['POST'])
def ad_crawler():
    
    payload = request.get_json()
    app.logger.info(payload)
        
    start_url = payload['url']

    process = CrawlerProcess(get_project_settings())
    process.crawl(FinnSpider, url=start_url)
    process.start()

    return 'OK', 200

    

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(os.environ.get('PORT', 8080)), threaded=False)

else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger.handlers:
        logging.basicConfig(level=logging.INFO, format=gunicorn_logger.handlers[0].formatter._fmt)
