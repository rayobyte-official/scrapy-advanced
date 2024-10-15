import scrapy
from scrapy_playwright.page import PageMethod
import logging

class LoginSpider(scrapy.Spider):
    name = "handle_click"
    start_urls = ["https://plzscrape.com/advanced/login/form"]

    def start_requests(self):
        yield scrapy.Request(
            url="https://plzscrape.com/advanced/login/form",
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    # Fill in the username field
                    PageMethod("fill", selector="#usr", value="test"),
                    # Fill in the password field
                    PageMethod("fill", selector="#pass", value="12345"),
                    # Click the login button
                    PageMethod("click", selector="#btn"),
                    # Wait for the dashboard to load (wait for the "DASHBOARD / User Information" heading)
                    PageMethod("wait_for_selector", selector="div.col-md-8", timeout=10000),  # Wait for the main content box
                    PageMethod("wait_for_timeout", 3000),  # Wait for 3 seconds for additional page load
                ],
            ),
        )

    def parse(self, response, **kwargs):
        # Print the full HTML of the page after login to help debugging
        full_html = response.text

        # Log the full HTML for debugging
        logging.info("Full Page HTML after login:")
        print(full_html)  # Print the full HTML to the terminal

        # Continue the usual parsing logic if needed
        yield {
            "url": response.url,
            "name": response.css("div.card-body div.col-md-6 p:contains('First Name')::text").get().strip().replace("First Name: ", ""),
            
        }

        logging.info("Full page HTML printed to terminal.")
