# extensions.py
"""
This extension tracks and logs the number of requests and responses each spider processes. It also integrates with Scrapy’s signals, allowing it to log these metrics when the spider starts and stops.
"""
from scrapy import signals
import logging
from collections import defaultdict
class RequestResponseLoggingExtension:
    def __init__(self):
        self.request_count = 0
        self.response_count = 0
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # Initialize the extension
        ext = cls()

        # Connect extension methods to Scrapy signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)

        return ext

    def spider_opened(self, spider):
        # Called when the spider opens, reset counts
        self.request_count = 0
        self.response_count = 0
        self.logger.info(f"Spider {spider.name} started. Tracking requests and responses...")

    def spider_closed(self, spider):
        # Called when the spider closes, log final counts
        self.logger.info(
            f"Spider {spider.name} closed. Total requests: {self.request_count}, Total responses: {self.response_count}"
        )

    def request_scheduled(self, request, spider):
        # Called each time a request is scheduled
        self.request_count += 1
        self.logger.debug(f"Request scheduled: {request.url}. Total requests: {self.request_count}")

    def response_received(self, response, request, spider):
        # Called each time a response is received
        self.response_count += 1
        self.logger.debug(f"Response received: {response.url}. Total responses: {self.response_count}")


"""
 
ProxyPerformanceLoggerExtension

This extension is designed to track and log the performance of each proxy used in a Scrapy project. It works alongside a proxy middleware that assigns a proxy to each request, and logs the success and failure rates for each proxy to help identify which proxies are reliable and which may need replacement.

Functionality:
- **Tracks Successes**: Counts the number of successful responses received for each proxy.
- **Tracks Failures**: Logs the number of times each proxy fails or drops a request.
- **Summarizes Proxy Performance**: Logs a summary of successes and failures for each proxy when the spider closes.

This setup provides valuable insights into proxy efficiency and reliability, which is useful for maintaining an optimal proxy pool for scraping.
"""

class ProxyPerformanceLoggerExtension:
    def __init__(self):
        # Initialize counters for tracking proxy performance
        self.success_count = defaultdict(int)
        self.failure_count = defaultdict(int)
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # Instantiate and connect signals to extension methods
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        crawler.signals.connect(ext.request_dropped, signal=signals.request_dropped)
        return ext

    def spider_opened(self, spider):
        # Log message when spider starts
        self.logger.info("Proxy Performance Logger started.")

    def spider_closed(self, spider):
        # Log overall proxy performance metrics when spider closes
        self.logger.info("Proxy performance summary:")
        for proxy, successes in self.success_count.items():
            failures = self.failure_count[proxy]
            self.logger.info(f"Proxy: {proxy} - Successes: {successes}, Failures: {failures}")

    def response_received(self, response, request, spider):
        # Track successful responses for each proxy
        proxy = request.meta.get('proxy')
        if proxy:
            self.success_count[proxy] += 1
            self.logger.debug(f"Successful request with proxy: {proxy}")

    def request_dropped(self, request, spider):
        # Track failed requests for each proxy
        proxy = request.meta.get('proxy')
        if proxy:
            self.failure_count[proxy] += 1
            self.logger.debug(f"Failed request with proxy: {proxy}")


"""
The extension listens for the spider’s open and close events, logging information and tracking the item count.

"""

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