import os
import json
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Charger la liste d'URLs à partir du fichier JSON
with open('urls.json', 'r') as fp:
    url_list = json.load(fp)

class ScrapBookSpider(scrapy.Spider):
    name = "scrap_book"
    start_urls = url_list
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)
        
    def parse(self, response):
        hotels = response.xpath('//div[@data-testid="property-card"]')
        for hotel in hotels:
            name = hotel.xpath('.//div[@data-testid="title"]/text()').get()
            #name = hotel.xpath('//*[@id="hp_hotel_name"]/div/h2/text()').get()
            #name = hotel.xpath("//h2[contains(@class, 'pp-header_title')]/text()").get()

            score = hotel.xpath('.//div[contains(@class, "d0522b0cca fd44f541d8")]/text()').get()
            url = hotel.xpath('.//a[@data-testid="title-link"]/@href').get()
            
            if url:
                yield response.follow(url, cb_kwargs={'name': name, 'score': score}, callback=self.parse_hotel)

    def parse_hotel(self, response, name, score):
        coord = response.xpath('//*[@id="hotel_sidebar_static_map_capla"]/div/div/div/div/text()').get()
        #coord = response.xpath('.//*[@id="hotel_sidebar_static_map"]/@data-atlas-latlng').get()
        
        #coord = response.xpath('//*[@id="hotel_sidebar_static_map_capla"]/@data-atlas-latlng').get()
        
        desc=response.xpath('//*[@id="property_description_content"]/div/div/p[1]/text()').get()
        #desc = response.xpath("//div[@id='property_description_content']/div/p/text()").get()
        yield {
            'name': name,
            'coord': coord,
            'score': score,
            'desc': desc,
            'url': response.url
        }

# Définir le nom du fichier où les résultats seront sauvegardés
filename = "scrap_book.json"

# Supprimer le fichier s'il existe déjà avant de lancer le crawling
if os.path.exists(filename):
    os.remove(filename)

# Configurer les paramètres de Scrapy
settings = {
    'CONCURRENT_REQUESTS': 5,
    'DOWNLOAD_DELAY': 0.5,
    'ROBOTSTXT_OBEY': True,
    'COOKIES_ENABLED': False,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'LOG_LEVEL': logging.INFO,
    'FEEDS': {
        filename: {"format": "json"},
    }
}

# Créer et démarrer le processus de crawling avec les paramètres définis
process = CrawlerProcess(settings=settings)
process.crawl(ScrapBookSpider)
process.start()