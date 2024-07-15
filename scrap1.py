import os
import json
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
# Charger la liste d'URLs à partir du fichier JSON
with open('urls.json','rb') as fp:
    url_list = json.load(fp)
class ScrapBookSpider(scrapy.Spider):
    name = "scrap_book"
    
    start_urls =url_list
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)
        

    def parse(self, response):
        
        hotels = response.xpath('//div[@data-testid="property-card"]')
        for hotel in hotels:
            
            name = hotel.xpath('.//div[@data-testid="title"]/text()').get()

            #name=unicodedata.normalize('NFKD',hotel_name).encode('latin1','ignore').decode('utf-8')
            #hotel_name_decoded = name.encode().decode('unicode_escape')
            score = hotel.xpath('.//div[contains(@class, "a3b8729ab1 d86cee9b25")]/text()').get()
            
            url = hotel.xpath('.//a[@data-testid="title-link"]/@href').get()
            
            yield scrapy.Request(response.urljoin(url), cb_kwargs={'name': name, 'score': score}, callback=self.parse_hotel)
            


    def parse_hotel(self, response, name, score):

        coord = response.xpath('//*[@id="hotel_sidebar_static_map"]/@data-atlas-latlng').get()
        desc =  response.xpath("//div[@id='property_description_content']/div/p/text()").get()
        yield {
               'name': name,
               'coord' : coord,
               'score' : score,
               'desc' : desc,
               'url' : response.url}
# Name of the file where the results will be saved
filename = "scrap_book.json"



# If the file already exists, delete it before crawling
if filename in os.listdir('./'):
    os.remove('./' + filename)
process = CrawlerProcess(settings = {
    'CONCURRENT_REQUESTS': 5,
    'DOWNLOAD_DELAY': 0.5,
    'ROBOTSTXT_OBEY': True,
    'COOKIES_ENABLED': False,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        './' + filename : {"format": "json"},
    },
})

# Start the crawling using the spider you defined above
process.crawl(ScrapBookSpider)
process.start()
