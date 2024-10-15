# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import random
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from decouple import config
import logging

class AdvanceScrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class AdvanceScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RandomUserAgentMiddleware:
    def __init__(self):
        # Dynamically generate a random user agent
        self.ua = UserAgent()

    def process_request(self, request, spider):
        # Get a random user agent
        user_agent = self.ua.random
        request.headers['User-Agent'] = user_agent
        spider.logger.info(f'Assigned User-Agent: {user_agent}')



class RotatingProxyMiddleware:
    def __init__(self):
        # Define a list of proxies
        self.proxies = [
           config('residential_proxy',default='')
             
            # Add as many proxies as you want here
        ]

    def process_request(self, request, spider):
        # Select a random proxy from the list for each request
        proxy = random.choice(self.proxies)
        spider.logger.info(f'Using proxy: {proxy}')
        
        # Assign the chosen proxy to the request meta
        request.meta['proxy'] = proxy

    def process_exception(self, request, exception, spider):
        # If there's an exception (e.g., proxy fails), retry with a new proxy
        spider.logger.warning(f'Proxy failed: {request.meta["proxy"]}. Retrying...')
        # Remove the failed proxy and retry with a new one
        request.meta['proxy'] = random.choice(self.proxies)
        return request  # Re-send the request with the new proxy





 

class RetryFailedRequestsMiddleware:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            max_retries=crawler.settings.getint('MAX_RETRIES', 3)
        )

    def process_response(self, request, response, spider):
        # Log successful response
        if response.status == 200:
            self.logger.info(f"Success: Received 200 response for URL: {request.url}")
            with open("successful_requests.log", "a") as f:
                f.write(f"Success URL: {request.url} - Status: {response.status}\n")
            return response
        else:
            # Log and retry non-200 responses
            self.logger.warning(
                f"Warning: Received non-200 response ({response.status}) for URL: {request.url}. Retrying request..."
            )
            return self._retry_request(request, spider) or response

    def process_exception(self, request, exception, spider):
        # Log the exception and retry
        self.logger.error(
            f"Error: Exception for URL: {request.url}. Exception: {exception}. Retrying request..."
        )
        return self._retry_request(request, spider) or request

    def _retry_request(self, request, spider):
        # Get the current retry count
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retries:
            # Log retry attempt details
            self.logger.info(
                f"Retrying {request.url} (Attempt {retries}/{self.max_retries})"
            )
            new_request = request.copy()
            new_request.meta['retry_times'] = retries
            return new_request
        else:
            # Log to file after reaching max retries
            self.logger.error(
                f"Failed: Gave up on URL: {request.url} after {self.max_retries} attempts."
            )
            with open("failed_requests.log", "a") as f:
                f.write(f"Failed URL: {request.url} - Reached max retries\n")
            return None  # Return None if max retries are reached