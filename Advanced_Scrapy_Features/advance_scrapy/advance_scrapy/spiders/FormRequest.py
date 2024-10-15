import scrapy
from scrapy.http import FormRequest
import re

class LoginAndDashboardSpider(scrapy.Spider):
    name = "advanced_login_spider"
    allowed_domains = ["plzscrape.com"]
    start_urls = ["https://plzscrape.com/advanced/login/form"]
    
    def start_requests(self):
        # Access login page and submit login form
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.login
        )

    def login(self, response):
        # Submit the login form using FormRequest
        formdata = {
            "usr": "test",       # Username field
            "pass": "12345"      # Password field
        }
        
        yield FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.after_login
        )

    def after_login(self, response):
            pass