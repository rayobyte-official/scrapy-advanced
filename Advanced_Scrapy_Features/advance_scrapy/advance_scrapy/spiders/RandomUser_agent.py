"""
middlewares.py Configuration


1. Add this custom middleware to dynamically rotate User-Agent for each request.
2. This prevents websites from easily detecting your scraper by changing the User-Agent header on each request.


from fake_useragent import UserAgent
import random

class RandomUserAgentMiddleware:
    def __init__(self):
        # Dynamically generate a random user agent
        self.ua = UserAgent()

    def process_request(self, request, spider):
        # Get a random user agent
        user_agent = self.ua.random
        request.headers['User-Agent'] = user_agent
        spider.logger.info(f'Assigned User-Agent: {user_agent}')




Settings.py Configuration:

 To enable the middleware, you need to modify the **`settings.py`** file in your Scrapy project.


Example settings configuration:

# settings.py

DOWNLOADER_MIDDLEWARES = {
    'advance_scrapy.middlewares.RandomUserAgentMiddleware': 543,  # The number 543 sets the priority (lower = higher priority) 
    # Here, 'advance_scrapy' is my project name. Don't forget to replace 'advance_scrapy' with your project name.

}


"""

import scrapy

class UserAgentTestSpider(scrapy.Spider):
    name = "user_agent_test"
    start_urls = ['https://httpbin.org/user-agent'] * 5 # Making 5 requests to test user agent rotation. httpbin.org is a simple service that returns the request headers it receives

    def parse(self, response):
        # Print the user-agent to verify it's working
        self.logger.info(f"User-Agent in response: {response.text}")
