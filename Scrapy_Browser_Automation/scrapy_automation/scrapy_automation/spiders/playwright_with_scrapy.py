import scrapy

class PlaywrightWithScrapySpider(scrapy.Spider):
    name = "playwright_with_scrapy"
    allowed_domains = ["plzscrape.com"]
    start_urls = ["https://plzscrape.com"]

    # Enable Playwright for this request
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                'playwright': True  # Enable Playwright for this request
            })

    def parse(self, response):
        # Example of how to extract some data
        page_title = response.css('title::text').get()
        print(f'Page title: {page_title}')
        # Continue parsing the rest of the data...
