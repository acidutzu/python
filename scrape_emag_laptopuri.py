import scrapy
from scrapy.crawler import CrawlerProcess

class Emag(scrapy.Spider):
    name = 'emag'

    def start_requests(self):
        yield scrapy.Request('https://www.emag.ro/laptopuri/sort-priceasc/c')


    def parse(self, response):
        produse = response.css('div.card-item.card-standard.js-product-data')
        for produs in produse:
            yield {
                 'pret': produs.css('p.product-new-price::text').get().replace('.',''),
                 'descriere': produs.css('a.card-v2-title::text').get(),
                 'link': produs.css('a.card-v2-title').attrib['href'],
            }
        for page_nr in range(0,150):
             yield scrapy.Request(f'http://emag.ro/laptopuri/p{page_nr}/c', callback=self.parse)              

process = CrawlerProcess(settings= {
    'FEED_URI': 'emag_laptopuri.csv',
    'FEED_FORMAT':'csv' })

process.crawl(Emag)
process.start()