import scrapy
from scrapy_playwright.page import PageMethod

class Minimize_interaction(scrapy.Spider):
    name = "minimize_interaction"
    allowed_domains = ["jsonplaceholder.typicode.com", "plzscrape.com"]
    
    # API URL and fallback URL (for Playwright-based scraping)
    start_urls = ["https://jsonplaceholder.typicode.com/posts", "https://plzscrape.com/advanced/dynamic-content"]

    def start_requests(self):
        # **Why use an API?**
        # APIs provide structured data in bulk and are specifically designed to give access to data
        # without unnecessary interactions like clicking, scrolling, or navigating multiple pages.
        # If the API is available, we can minimize interactions by fetching all data in one request.
        yield scrapy.Request(
            url=self.start_urls[0],  # Try to fetch data from the API (JSONPlaceholder)
            callback=self.parse_api,  # If API request is successful, process API data
            errback=self.handle_api_failure  # If API request fails, fall back to Playwright scraping
        )

    def parse_api(self, response):
        # This method parses data from the API if the API is available
        if response.status == 200:
            self.log("API is available, parsing API data...")
            posts = response.json()

            # Yield each post's data from the API
            for post in posts:
                yield {
                    'id': post['id'],
                    'title': post['title'],
                    'body': post['body'],
                    'userId': post['userId'],
                }

            # Close the spider after API data is fetched and parsed
            self.crawler.engine.close_spider(self, 'API scraping completed successfully.')

    def handle_api_failure(self, failure):
        # **What if the API is not available?**
        # When an API is not available, we must fall back to web scraping. However, we still aim to minimize interactions.
        # Using Playwright, we automate the interaction with the webpage, simulating user actions like clicking the "Load More" button,
        # which allows us to load more data dynamically. This reduces the need for multiple page reloads or navigating through multiple pages.

        self.log("API failed or not available. Falling back to Playwright for scraping dynamic content.")
        
        # Use Playwright to scrape dynamic content from the fallback URL
        yield scrapy.Request(
            url=self.start_urls[1],  # Fallback to dynamic content page if API is unavailable
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    # Wait until the posts container is loaded
                    PageMethod('wait_for_selector', '#posts-container'),
                    
                    # Automate the "Load More" button click up to 5 times to load more data dynamically
                    # **Minimizing interaction with Playwright**:
                    # Instead of scraping multiple pages or reloading content manually,
                    # we use Playwright to automate the "Load More" button. This way, we load more content
                    # in one go by clicking the button multiple times and reducing unnecessary requests.
                    PageMethod('evaluate', """
                        async () => {
                            let loadMoreButton = document.querySelector('#load-more');
                            let clickCount = 0;
                            while (loadMoreButton && !loadMoreButton.disabled && clickCount < 5) {
                                loadMoreButton.click();  // Click the "Load More" button
                                await new Promise(r => setTimeout(r, 2000));  // Wait for 2 seconds to load new content
                                
                                // Scroll to the bottom of the page after each click to trigger content loading
                                window.scrollBy(0, document.body.scrollHeight);
                                await new Promise(r => setTimeout(r, 1000));  // Wait for scrolling

                                // Update the "Load More" button status
                                loadMoreButton = document.querySelector('#load-more');
                                clickCount += 1;  // Increment the click counter
                            }
                        }
                    """),
                ]
            },
            callback=self.parse_dynamic_content  # Parse the dynamic content once it's loaded
        )

    def parse_dynamic_content(self, response):
        # Parse the dynamic content loaded by Playwright
        titles = response.css('#posts-container h2::text').getall()

        # Print and yield each title from the dynamic content
        for title in titles:
            self.log(f"Found title: {title}")
            yield {
                'title': title
            }

        # After parsing, close the spider
        self.crawler.engine.close_spider(self, 'Dynamic content scraping completed successfully.')
