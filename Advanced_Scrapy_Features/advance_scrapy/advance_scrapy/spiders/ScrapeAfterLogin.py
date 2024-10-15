import scrapy
from scrapy.http import FormRequest
import re

class LoginAndDashboardSpider(scrapy.Spider):
    name = "after_login_spider"
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
            referer_url = response.request.headers.get('Referer', None)
            if referer_url:
                self.logger.info(f"Referer URL: {referer_url.decode('utf-8')}")

            # If login is successful, navigate to dashboard
            self.logger.info("Login successful. Navigating to dashboard page.")
            yield scrapy.Request(
                url="https://plzscrape.com/advanced/login/dashboard",
                callback=self.parse_dashboard
            )

    def parse_dashboard(self, response):
            # Log that we've reached the dashboard page
            self.logger.info("Reached dashboard page. Extracting user information...")
            
            # Extract and print the user's first name from the dashboard page
            page_html = response.text
            reg_name = r'First Name:[^>]+>([^<]+)<\/p>'
            name_match = re.search(reg_name, page_html)
            
            if name_match:
                name = name_match.group(1)
                print("-------------->First Name:", name)
            else:
                self.logger.warning("First Name not found on the page.")

            self.logger.info("Completed extracting user information from dashboard page.")
