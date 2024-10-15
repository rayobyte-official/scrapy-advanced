"""
On several tests, I found that Selenium works better than Playwright at avoiding bot detection

"""
import scrapy
import time
class SeleniumSpider(scrapy.Spider):
    name = "selenium_undetected"
    start_urls = ["https://bot.sannysoft.com/"]  # Test URL to check stealth features
   
    def start_requests(self):
        for url in self.start_urls:
            # Use Selenium only on this specific request
           
            yield scrapy.Request(url, meta={'use_selenium': True}, callback=self.parse)



    def parse(self, response):
        # Log the response to verify if Selenium Stealth worked
        self.log("Page loaded with Selenium Stealth")

        # Extract data from the response using Scrapy's selectors
        title = response.xpath('//title/text()').get()
        self.log(f"Title of the page: {title}")
