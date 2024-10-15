"""
You can use any CAPTCHA-solving API here; in this example, I'm using Anti-Captcha.
Update your existing RotatingProxyMiddleware to use the proxy with Playwright, or you can also configure the proxy directly in your spider 

middlewares.py configuration

class RotatingProxyMiddleware:

    def process_request(self, request, spider):
        spider.logger.info(f"Using proxy:  {config('server', default='')}")
        
        if request.meta.get("playwright"):
            # Set Playwright-specific proxy configuration
            request.meta["playwright_context_kwargs"] = {
                "ignore_https_errors": True,
                "proxy": {
                    "server":   config('server', default=''),
                    "username":   config('username', default=''),
                    "password":   config('password', default=''),
                }
            }
        else:
            # For Scrapy requests, set proxy without protocol specification
            request.meta['proxy'] =  config('residential_proxy', default='')

    def process_exception(self, request, exception, spider):
        # Log and retry with the same proxy if there’s an error
        spider.logger.warning(f'Proxy failed for {request.meta.get("proxy", "None")}. Retrying...')
        request.meta['proxy'] =  config('server', default='')
        return request

"""

import scrapy
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

class RecaptchaSpider(scrapy.Spider):
    name = "recaptcha_spider"
    start_urls = ["https://www.google.com/recaptcha/api2/demo"]
    
    """
    I have disabled my existing `RotatingProxyMiddleware` since I am directly configuring my proxy in Playwright for this case.
    You can use custom settings to disable any specific middleware, extension, or pipeline.

    """
    custom_settings = {
       # Disable all DOWNLOADER_MIDDLEWARES
        "DOWNLOADER_MIDDLEWARES": {
        },
        # Disable all EXTENSIONS
        "EXTENSIONS":{

        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
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
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        if not page:
            self.logger.error("Playwright page not found in response meta.")
            return

        api_key = "your api key"
        page_url = response.url
        solver = recaptchaV2Proxyless()
        solver.set_key(api_key)
        solver.set_website_url(page_url)
        solver.set_website_key("6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-") # Replace this site key with the actual website's key

        # Solve CAPTCHA using Anti-Captcha
        captcha_solution = solver.solve_and_return_solution()
        if captcha_solution:
            print(f"Solved CAPTCHA: {captcha_solution}")
            
        else:
            self.logger.error("Failed to solve CAPTCHA.")
 