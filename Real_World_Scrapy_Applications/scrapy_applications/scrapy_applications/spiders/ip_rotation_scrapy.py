import scrapy

class ProxyTestSpider(scrapy.Spider):
    name = "ip_rotation_scrapy"
    start_urls = ['https://httpbin.org/ip'] * 5  # Making 5 requests to test proxy rotation

    def parse(self, response):
        # Print the IP address returned by the website
        self.logger.info(f"IP Address: {response.text}")
