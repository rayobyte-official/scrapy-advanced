import scrapy
from scrapy_playwright.page import PageMethod
import logging

class LoginAndDynamicSpider(scrapy.Spider):
    name = "login_and_dynamic"
    allowed_domains = ["plzscrape.com"]
    start_urls = ["https://plzscrape.com/advanced/login/form"]

    def start_requests(self):
        # Step 1: Login request and navigation to the dynamic content page
        yield scrapy.Request(
            url=self.start_urls[0],
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    # Fill in the username and password fields
                    PageMethod("fill", selector="#usr", value="test"),
                    PageMethod("fill", selector="#pass", value="12345"),
                    # Click the login button
                    PageMethod("click", selector="#btn"),
                    # Wait for the navigation bar to load
                    PageMethod("wait_for_selector", selector=".navbar", timeout=10000),
                    PageMethod("wait_for_timeout", 3000),  # Wait for 3 seconds for additional load

                    # Step 2: Click the "Advanced Challenges" dropdown to expand it
                    PageMethod("click", selector=".dropdown:nth-child(2) .dropdown-toggle"),
                    
                    PageMethod("wait_for_timeout", 3000), 
                    
                    # Step 3: Click on the "Dynamic Content" link
                    PageMethod("click", selector="a[href='/advanced/dynamic-content']"),
                    PageMethod("wait_for_selector", "#posts-container"),  # Wait for the dynamic content page to load
                ],
            ),
            callback=self.parse_dynamic_content  # After login and navigation, go to the dynamic content parsing
        )

    def parse_dynamic_content(self, response):
        # Step 4: Use Playwright methods to click "Load More" and scroll, without creating a new request
        # Playwright methods will be executed within the same session
        yield scrapy.Request(
            url=response.url,
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', '#load-more'),  # Wait until the "Load More" button is visible
                    PageMethod('evaluate', """
                        async () => {
                            let loadMoreButton = document.querySelector('#load-more');
                            let clickCount = 0;
                            while (loadMoreButton && !loadMoreButton.disabled && clickCount < 3) {
                                loadMoreButton.click();  // Click the "Load More" button
                                await new Promise(r => setTimeout(r, 2000));  // Wait for 2 seconds to load new content
                                
                                // Scroll to the bottom of the page after each click
                                window.scrollBy(0, document.body.scrollHeight);
                                await new Promise(r => setTimeout(r, 1000));  // Wait for scrolling

                                loadMoreButton = document.querySelector('#load-more');  // Check if the button is still active
                                clickCount += 1;  // Increment the click counter
                            }
                        }
                    """)  # Click the "Load More" button 3 times and scroll down
                ],
            ),
            callback=self.parse_dynamic_content_items,  # Continue to extract content after performing actions
            dont_filter=True
        )

    def parse_dynamic_content_items(self, response):
        # Step 5: Extract all <h2> elements within the #posts-container
        titles = response.css('#posts-container h2::text').getall()

        # Print the extracted titles
        for title in titles:
            print(title)

        # Yield the titles as Scrapy items
        for title in titles:
            yield {
                'title': title
            }

        # After scraping, close the spider
        self.crawler.engine.close_spider(self, 'Scraping completed successfully.')
