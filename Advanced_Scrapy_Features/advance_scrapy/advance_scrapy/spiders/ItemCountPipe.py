 
"""
The extension listens for the spider’s open and close events, logging information and tracking the item count.

extensions.py configuration 

class ItemCountExtension:
    def __init__(self):
        self.item_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        
        # Store the extension instance in crawler.stats for easy access in the pipeline
        crawler.stats.set_value("item_count_extension", ext)
        
        return ext

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")

    def spider_closed(self, spider):
        spider.logger.info(f"Spider closed: {spider.name}")
        spider.logger.info(f"Total items scraped: {self.item_count}")

    def increment_item_count(self):
        self.item_count += 1


pipelines.py configuration 

from advance_scrapy.extensions import ItemCountExtension
from scrapy import signals


class ItemCounterPipeline:
    def __init__(self, item_count_extension):
        self.item_count_extension = item_count_extension

    @classmethod
    def from_crawler(cls, crawler):
        # Get the extension instance from crawler.stats
        item_count_extension = crawler.stats.get_value("item_count_extension")
        return cls(item_count_extension)

    def process_item(self, item, spider):
        # Increment the item count in the extension if it exists
        if self.item_count_extension:
            self.item_count_extension.increment_item_count()
        # Process the item (e.g., save it to a database or clean data)
        return item

        
settings.py configuration

EXTENSIONS = {
  
    'advance_scrapy.extensions.ItemCountExtension': 500,  # Replace 'advance_scrapy' with your actual project name

}


ITEM_PIPELINES = {
    'advance_scrapy.pipelines.ItemCounterPipeline': 300,  # Replace 'advance_scrapy' with your actual project name
}


"""

import scrapy

class QuotesSpider(scrapy.Spider):
    name = "item_count"
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        # Loop through each quote on the page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall()
            }
        
        # Follow pagination links and repeat parsing on the next page
        #next_page = response.css("li.next a::attr(href)").get()
        #if next_page is not None:
            #yield response.follow(next_page, self.parse)
