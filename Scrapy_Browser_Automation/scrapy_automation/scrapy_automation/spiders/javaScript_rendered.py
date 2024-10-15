import scrapy
from scrapy_playwright.page import PageMethod

class JavascriptRenderedSpider(scrapy.Spider):
    name = "javaScript_rendered"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/js"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                'playwright': True,  # Enable Playwright for this request
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', '.quote'),  # Wait for the quotes to be rendered
                    PageMethod('evaluate', '''{
                            window.scrollBy(0, document.body.scrollHeight);
                        }'''),
                    PageMethod('wait_for_timeout', 2000),  # Add delay to let new content load
                ]
                
            })

    async def parse(self, response):
        # Extract content as usual with Scrapy selectors
        quotes = response.css('.quote .text::text').getall()

        # Print each extracted quote
        for quote in quotes:
            print(quote)
