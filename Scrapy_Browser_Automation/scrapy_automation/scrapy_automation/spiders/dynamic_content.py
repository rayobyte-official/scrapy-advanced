import scrapy
from scrapy_playwright.page import PageMethod

class DynamicContentSpider(scrapy.Spider):
    name = "dynamic_content"
    allowed_domains = ["plzscrape.com"]
    start_urls = ["https://plzscrape.com/advanced/dynamic-content"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '#posts-container'),  # Wait until the initial posts are loaded
                        PageMethod('evaluate', """
                            async () => {
                                let loadMoreButton = document.querySelector('#load-more');
                                let clickCount = 0;
                                while (loadMoreButton && !loadMoreButton.disabled && clickCount < 5) {
                                    loadMoreButton.click();  // Click the "Load More" button
                                    await new Promise(r => setTimeout(r, 2000));  // Wait for 2 seconds to load new content
                                    
                                    // Scroll to the bottom of the page after each click
                                    window.scrollBy(0, document.body.scrollHeight);
                                    await new Promise(r => setTimeout(r, 1000));  // Wait for scrolling

                                    loadMoreButton = document.querySelector('#load-more');  // Check if the button is still active
                                    clickCount += 1;  // Increment the click counter
                                }
                            }
                        """),  # Keep clicking the button a maximum of 5 times
                    ]
                },
                dont_filter=True  # Prevent Scrapy from filtering and re-requesting the same URL
            )

    def parse(self, response):
        # Extract all <h2> elements within the #posts-container
        titles = response.css('#posts-container h2::text').getall()

        # Print the extracted titles
        for title in titles:
            print(title)

        # Yield the titles as Scrapy items
        for title in titles:
            yield {
                'title': title
            }

        # After parsing, close the spider
        self.crawler.engine.close_spider(self, 'Scraping completed successfully.')
