"""
Rotating Proxy Middleware Configuration:
This middleware allows Scrapy to rotate through a list of proxies for each request. This is useful to avoid getting blocked by websites, as it sends requests through different IP addresses.

# Add this to your Scrapy middlewares.py file
class RotatingProxyMiddleware:
    def __init__(self):
        # Define a list of proxies
        self.proxies = [
            'https://rayobyte_proxy_user_name:rayobyte_proxy_password@server_name:port',
             
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


 
# Add this to your Scrapy settings.py file

DOWNLOADER_MIDDLEWARES = {
    'advance_scrapy.middlewares.RotatingProxyMiddleware': 543, 
    # Here, 'advance_scrapy' is my project name. Don't forget to replace 'advance_scrapy' with your project name.


 
"""
import scrapy

class ProxyTestSpider(scrapy.Spider):
    name = "proxy_test"
    start_urls = ['https://httpbin.org/ip'] * 5  # Making 5 requests to test proxy rotation

    def parse(self, response):
        # Print the IP address returned by the website
        self.logger.info(f"IP Address: {response.text}")
