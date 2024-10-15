# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from advance_scrapy.extensions import ItemCountExtension
from scrapy import signals

class AdvanceScrapyPipeline:
    def process_item(self, item, spider):
        return item




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