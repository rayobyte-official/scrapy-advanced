import scrapy
import time
import datetime

class ParallelSpider(scrapy.Spider):
    name = "parallel"
    
    # Define your custom settings here
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,  # Process 16 requests in parallel
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,  # Limit to 8 concurrent requests per domain
        'DOWNLOAD_DELAY': 0,  # No delay to see the effect of parallelism
        'COOKIES_ENABLED': False,  # Disable cookies for faster scraping
        'RETRY_TIMES': 2,  # Retry failed requests up to 2 times
        'LOG_LEVEL': 'DEBUG',  # Set log level to debug to see detailed logs
    }
    
    # List of URLs to scrape
    start_urls = [
        'https://quotes.toscrape.com/page/1/',
        'https://quotes.toscrape.com/page/2/',
        'https://quotes.toscrape.com/page/3/',
        'https://quotes.toscrape.com/page/4/',
        'https://quotes.toscrape.com/page/5/',
        'https://quotes.toscrape.com/page/6/',
        'https://quotes.toscrape.com/page/7/',
        'https://quotes.toscrape.com/page/8/',
        'https://quotes.toscrape.com/page/9/',
    ]
    
    def __init__(self):
        super().__init__()
        self.start_time = None

    def start_requests(self):
        # Record the start time
        self.start_time = datetime.datetime.now()
        self.log(f"Spider started at {self.start_time}")

        # Send all requests in parallel
        for url in self.start_urls:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.log(f"[{current_time}] Sending request to: {url}")
            yield scrapy.Request(url, callback=self.parse)

    # Default parse method
    def parse(self, response):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.log(f"[{current_time}] Received response from: {response.url}")

        for quote in response.css('div.quote'):
            text = quote.css('span.text::text').get()
            author = quote.css('small.author::text').get()
            yield {
                'text': text,
                'author': author
            }

    def closed(self, response):
        # Record the end time
        end_time = datetime.datetime.now()
        total_time = end_time - self.start_time
        self.log(f"Spider closed at {end_time}")
        self.log(f"Total time taken: {total_time}")
