import scrapy
import asyncio  # Required for delay
from scrapy_playwright.page import PageMethod

class ProxyTestSpider(scrapy.Spider):
    name = "playwright_ip_rotation"
    start_urls = ['https://httpbin.org/ip']
    request_count = 5  # Total number of requests to be made sequentially
    delay_between_requests = 5  # Delay in seconds to allow proxy IP refresh
    current_request = 0  # Track the current request count

    def start_requests(self):
        # Start with a single request and manage the sequence in `parse`
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse,
            dont_filter=True,  # Ensures each request is treated as unique
            meta={
                "playwright": True,
                "playwright_context": f"context_{self.current_request}",  # Unique context per request
                "playwright_close_context": True,  # Automatically close context after each request
                "playwright_page_coroutines": [
                    PageMethod("clear_browser_cookies"),
                    PageMethod("clear_browser_cache")
                ]
            }
        )

    async def parse(self, response):
        # Log the IP address to verify proxy rotation
        self.logger.info(f"IP Address: {response.text}")

        # Introduce a delay between requests to allow time for the proxy server to rotate IPs
        await asyncio.sleep(self.delay_between_requests)

        # Check if more requests are needed
        self.current_request += 1
        if self.current_request < self.request_count:
            # Initiate the next request
            yield scrapy.Request(
                url=self.start_urls[0],
                callback=self.parse,
                dont_filter=True,  # Ensures each request is treated as unique
                meta={
                    "playwright": True,
                    "playwright_context": f"context_{self.current_request}",  # Unique context per request
                    "playwright_close_context": True,  # Automatically close context after each request
                    "playwright_page_coroutines": [
                        PageMethod("clear_browser_cookies"),
                        PageMethod("clear_browser_cache")
                    ]
                }
            )
