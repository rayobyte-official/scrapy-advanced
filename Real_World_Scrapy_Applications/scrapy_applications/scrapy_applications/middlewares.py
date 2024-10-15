# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import random
from decouple import config
import re
from fake_useragent import UserAgent
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
from scrapy.http import HtmlResponse
import os
import zipfile
from scrapy.exceptions import IgnoreRequest
from scrapy import signals
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScrapyApplicationsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapyApplicationsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

#This RotatingProxyMiddleware will be used to rotate proxies on every request.
class RotatingProxyMiddleware:
    def __init__(self):
        # Load multiple proxies from environment
        self.proxies = [
            config('proxy_1'),
            config('proxy_2'),
            config('proxy_3')
        ]
        self.proxy_index = 0  # Start with the first proxy
        # Regex pattern to extract username, password, and server from proxy
        self.proxy_pattern = re.compile(r"([^:]+):([^@]+)@(.*)")

    def get_next_proxy(self):
        # Get the current proxy and increment index
        selected_proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)  # Cycle to next proxy
        return selected_proxy

    def process_request(self, request, spider):
        # Get the next proxy in sequence
        selected_proxy = self.get_next_proxy()
        spider.logger.info(f"Using proxy: {selected_proxy}")

        # Match the proxy pattern to extract details
        match = self.proxy_pattern.match(selected_proxy)
        if match:
            username = match.group(1)
            password = match.group(2)
            server = match.group(3)

            if request.meta.get("playwright"):
                # Set Playwright-specific proxy configuration
                request.meta["playwright_context_kwargs"] = {
                    "ignore_https_errors": True,
                    "proxy": {
                        "server": server,
                        "username": username,
                        "password": password,
                    }
                }
            else:
                # For Scrapy requests, set the full proxy string
                request.meta['proxy'] = f"https://{selected_proxy}"
        else:
            spider.logger.error(f"Invalid proxy format: {selected_proxy}")

    def process_exception(self, request, exception, spider):
        # On exception, retry with the next proxy
        selected_proxy = self.get_next_proxy()
        spider.logger.warning(f'Proxy failed, retrying with next proxy: {selected_proxy}')

        match = self.proxy_pattern.match(selected_proxy)
        if match:
            username = match.group(1)
            password = match.group(2)
            server = match.group(3)

            if request.meta.get("playwright"):
                request.meta["playwright_context_kwargs"]["proxy"] = {
                    "server": server,
                    "username": username,
                    "password": password,
                }
            else:
                request.meta['proxy'] = f"https://{selected_proxy}"
        
        return request


#This RandomUserAgentMiddleware will be used to rotate user-agent on every request.
class RandomUserAgentMiddleware:
    def __init__(self):
        # Dynamically generate a random user agent
        self.ua = UserAgent()

    def process_request(self, request, spider):
        # Get a random user agent
        user_agent = self.ua.random
        request.headers['User-Agent'] = user_agent





#This RetryFailedRequestsMiddleware will be used to handling bans on every request.
class RetryFailedRequestsMiddleware:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            max_retries=crawler.settings.getint('MAX_RETRIES', 3)
        )

    def process_response(self, request, response, spider):
        # Log successful response
        if response.status == 200:
            self.logger.info(f"Success: Received 200 response for URL: {request.url}")
            with open("successful_requests.log", "a") as f:
                f.write(f"Success URL: {request.url} - Status: {response.status}\n")
            return response
        else:
            # Log and retry non-200 responses
            self.logger.warning(
                f"Warning: Received non-200 response ({response.status}) for URL: {request.url}. Retrying request..."
            )
            return self._retry_request(request, spider) or response

    def process_exception(self, request, exception, spider):
        # Log the exception and retry
        self.logger.error(
            f"Error: Exception for URL: {request.url}. Exception: {exception}. Retrying request..."
        )
        return self._retry_request(request, spider) or request

    def _retry_request(self, request, spider):
        # Get the current retry count
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retries:
            # Log retry attempt details
            self.logger.info(
                f"Retrying {request.url} (Attempt {retries}/{self.max_retries})"
            )
            new_request = request.copy()
            new_request.meta['retry_times'] = retries
            return new_request
        else:
            # Log to file after reaching max retries
            self.logger.error(
                f"Failed: Gave up on URL: {request.url} after {self.max_retries} attempts."
            )
            with open("failed_requests.log", "a") as f:
                f.write(f"Failed URL: {request.url} - Reached max retries\n")
            return None  # Return None if max retries are reached



class SeleniumMiddleware:
    def __init__(self):
        self.driver = None  # Lazy initialization of driver
        self.proxy_extension_path = 'proxy_auth_plugin.zip'  # Store extension path

    def _initialize_driver(self):
        # Proxy information
        proxy =  config('server')
        proxy_user = config('username')
        proxy_pass = config('password')

        # Set up Chrome options for Selenium
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f'--proxy-server={proxy}')

        # Add proxy authentication extension once
        if not os.path.exists(self.proxy_extension_path):
            self._create_proxy_auth_extension(proxy, proxy_user, proxy_pass)
        options.add_extension(self.proxy_extension_path)

        # Initialize the Chrome driver with configured options
        self.driver = webdriver.Chrome(options=options)

        # Apply stealth settings to make Selenium less detectable
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

    def _create_proxy_auth_extension(self, proxy_host, proxy_user, proxy_pass):
        # Separate the host and port
        host, port = proxy_host.split(':')

        # Define the proxy extension content
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{host}",
                    port: parseInt({port})
                }},
                bypassList: ["localhost"]
            }}
        }};
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
        chrome.webRequest.onAuthRequired.addListener(
            function(details) {{
                return {{
                    authCredentials: {{
                        username: "{proxy_user}",
                        password: "{proxy_pass}"
                    }}
                }};
            }},
            {{urls: ["<all_urls>"]}},
            ["blocking"]
        );
        """

        # Create the extension file
        with zipfile.ZipFile(self.proxy_extension_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

    def process_request(self, request, spider):
        # Check if Selenium is required for this request
        if request.meta.get('use_selenium', False):
            # Initialize driver if not already done
            if not self.driver:
                self._initialize_driver()

            # Use Selenium to open the URL
            self.driver.get(request.url)

            # Wait until the page is fully loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # Create and return a Scrapy HtmlResponse with Selenium-rendered content
            body = self.driver.page_source
            return HtmlResponse(url=self.driver.current_url, body=body, encoding='utf-8', request=request)

    def __del__(self):
        # Clean up driver and extension file
        if self.driver:
            self.driver.quit()
        if os.path.exists(self.proxy_extension_path):
            os.remove(self.proxy_extension_path)  # Remove extension file to avoid clutter


class BanMonitoringMiddleware:

    def __init__(self, crawler):
        self.crawler = crawler
        self.url_ban_counts = {}  # Track ban count per URL
        self.url_delays = {}  # Track delay per URL
        self.ban_threshold = 3  # Threshold for consecutive bans per URL
        self.base_delay = 0.5  # Base delay in seconds

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info("BanMonitoringMiddleware opened and initialized")

    def spider_closed(self, spider):
        spider.logger.info("BanMonitoringMiddleware closed")

    def process_response(self, request, response, spider):
        url = request.url

        # Log all non-200 responses
        if response.status != 200:
            spider.logger.warning(f"Non-200 response detected: {response.status} for {url}")

        # Specifically track 403, 404, and 429 status codes as bans
        if response.status in [403, 404, 429]:
            self.url_ban_counts[url] = self.url_ban_counts.get(url, 0) + 1
            spider.logger.info(f"Ban detected: {response.status} for {url} - Consecutive bans: {self.url_ban_counts[url]}")

            # If ban threshold is reached for the URL, increase its specific delay
            if self.url_ban_counts[url] >= self.ban_threshold:
                self.url_delays[url] = self.url_delays.get(url, self.base_delay) + 1  # Increment delay for this URL
                spider.logger.info(f"Ban threshold reached for {url}. Increased delay to {self.url_delays[url]} seconds")
                self.url_ban_counts[url] = 0  # Reset count after delay adjustment

            # Apply URL-specific delay if it exists
            delay = self.url_delays.get(url, 0)
            if delay > 0:
                spider.logger.info(f"Applying delay of {delay} seconds for {url}")
                time.sleep(delay)

        else:
            # Reset the ban counter and delay for the URL on successful response
            if url in self.url_ban_counts:
                spider.logger.debug(f"Resetting consecutive ban counter for {url}")
                self.url_ban_counts[url] = 0

        return response