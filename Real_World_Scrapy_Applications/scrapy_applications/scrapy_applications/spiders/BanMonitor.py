"""
Here is a real-world example: we have already integrated rotating proxies, random user agents, and a retry middleware.
Our BanMonitoringMiddleware monitors for bans and increases the delay if a ban is detected. 
We intentionally added some invalid URLs for testing so you can check the logs.

"""
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "ban_monitor"
    start_urls = [
        'https://quotes.toscrape.com/page/1/',  # Valid URL
        'https://quotes.toscrape.com/page/2/',  # Valid URL
        'https://quotes.toscrape.com/page/9999/',  # Invalid URL to trigger 404
        'https://invalidurl.toscrape.com/',  # Non-existent domain to simulate ban/error
    ]

    def parse(self, response):
        if response.status == 200:
            for quote in response.css('div.quote'):
                yield {
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                }
        else:
            self.logger.info(f"Skipping parse as response status is {response.status}")
