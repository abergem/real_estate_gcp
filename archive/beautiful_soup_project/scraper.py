'''
Scraper for real-estate data from Finn.no
'''

import requests
from bs4 import BeautifulSoup
import re

def crawl_finn():
    # URL base for real-estate filtered by Oslo
    start_url = 'https://www.finn.no/realestate/homes/search.html?location=0.20061'
    r = requests.get(start_url)

    # Crawl and parse website html using urllib BeautifulSoup
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
    
    for link in links:
        r = requests.get(link)
        htlm = r.content
        soup = BeautifulSoup(html, 'html.parser')
        print('stop here')

    # Next page
    


if __name__ == '__main__':
    crawl_finn()