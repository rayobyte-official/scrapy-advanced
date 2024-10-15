import scrapy
import random
import asyncio
from scrapy_playwright.page import PageMethod

class PlaywrightStealthSpider(scrapy.Spider):
    name = "playwright_stealth_spider"
    start_urls = ["https://bot.sannysoft.com/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,  # Enable Playwright for this request
                    'playwright_page_methods': [
                        # Mask navigator.webdriver to bypass detection
                        PageMethod("evaluate", """
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            });
                        """),
                        # Inject visible cursor for testing
                        PageMethod("evaluate", """
                            if (!document.getElementById('customCursor')) {
                                const cursor = document.createElement('div');
                                cursor.id = 'customCursor';
                                cursor.style.width = '20px';
                                cursor.style.height = '20px';
                                cursor.style.backgroundColor = 'red';
                                cursor.style.border = '3px solid black';
                                cursor.style.borderRadius = '50%';
                                cursor.style.position = 'absolute';
                                cursor.style.zIndex = '10000';
                                cursor.style.pointerEvents = 'none';
                                document.body.appendChild(cursor);
                            }
                        """),
                        # Perform slower, more deliberate mouse movements
                        PageMethod("evaluate", """
                            let moveCursorSlowly = async () => {
                                for (let i = 0; i < 10; i++) {
                                    const x = Math.floor(Math.random() * 1000);
                                    const y = Math.floor(Math.random() * 700);
                                    const cursor = document.getElementById('customCursor');
                                    if (cursor) {
                                        cursor.style.left = `${x}px`;
                                        cursor.style.top = `${y}px`;
                                    }
                                    await new Promise(resolve => setTimeout(resolve, 500));  // Slower movement
                                }
                            };
                            moveCursorSlowly();
                        """),
                        # Perform slower, more gradual scrolling on the page
                        PageMethod("evaluate", """
                            let scrollPageSlowly = async () => {
                                for (let i = 0; i < 5; i++) {
                                    window.scrollBy(0, Math.floor(Math.random() * 800));
                                    await new Promise(resolve => setTimeout(resolve, 1000));  // Slower scrolling
                                }
                            };
                            scrollPageSlowly();
                        """),
                        PageMethod("screenshot", path="screenshot.png", full_page=True)
                    ],
                },
                callback=self.parse,
            )

    def parse(self, response):
        # Print the page content for debugging
        print(response.text)  # Or you can process the response further

