import scrapy

class PlaywrightWithScrapySpider(scrapy.Spider):
    name = "playwright_with_scrapy_proxy"
    allowed_domains = ["ipinfo.io"]
    start_urls = ["https://ipinfo.io/json"]

    # Enable Playwright with Proxy for this request
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                        "playwright": True,
                        "playwright_context": "new",
                        "playwright_context_kwargs": {
                            "java_script_enabled": False,
                            "ignore_https_errors": True,
                            "proxy": {
                                "server": "server_name", #example la.residential.rayobyte.com:8000
                                "username": "username",
                                "password": "password",
                            },
                        },
                    },
            )

    def parse(self, response):
        # Example of how to extract some data
         
        print(f'ip info: {response.text}')
        # Continue parsing the rest of the data...
