'''
Settings.py configuration. We also downloaded the Selenium Chrome executable and placed it in the scrapy_automation folder.

Scrapy_Browser_Automation\
├── scrapy_automation\    
│   └── chrome.exe  #Chrome executable
├── scrapy_automation\          
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   └── spiders\
│       ├── __init__.py
│       ├── basic_scripting_playwright.py 
│       └── basic_scripting_selenium.py
└── scrapy.cfg          


from shutil import which
  
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS=['--headless']  

DOWNLOADER_MIDDLEWARES = {
     'scrapy_selenium.SeleniumMiddleware': 800
     }

'''

import scrapy
from scrapy_selenium import SeleniumRequest


class BasicScriptingSeleniumSpider(scrapy.Spider):
    name = "basic_scripting_selenium"
    allowed_domains = ["quotes.toscrape.com"]
    def start_requests(self):
        url = 'https://quotes.toscrape.com'
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
          print(response.text)
