"""
settings.py configuration for enabling cache in Scrapy.

# Enable HTTP cache
HTTPCACHE_ENABLED = True

# Set the expiration time (in seconds) - this defines how long items remain in the cache.
# 0 means no expiration, so items will be cached forever unless manually cleared.
HTTPCACHE_EXPIRATION_SECS = 0

# Specify the directory where cache files will be stored.
# You can customize the folder name where the cache is stored.
HTTPCACHE_DIR = 'httpcache'

# Specify HTTP response codes to ignore for caching. 
# For example, responses with 403 (forbidden) or 500 (server error) won't be cached.
HTTPCACHE_IGNORE_HTTP_CODES = [403, 500]

# Choose the type of cache storage. FilesystemCacheStorage will store the cache in files.
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Enable cache debugging to get detailed information about cache usage in logs.
# This is optional but useful for understanding whether requests are served from the cache or the server.
HTTPCACHE_DEBUG = True
"""
import scrapy


class ProxyCache(scrapy.Spider):
    name = 'scrapy_proxy_cache'

    def start_requests(self):
        urls = [
            'https://ipinfo.io/json'
        ]
        
        # Define your list of HTTPS proxies
        proxies = [
            'https://rayobyte_proxy_username:rayobyte_proxy_pass@server_name:port',  # Use 'https' for HTTPS proxies
         
        ]
        
        for i, url in enumerate(urls):
            # Assign proxy for each request
            yield scrapy.Request(
                url=url,
                meta={'proxy': proxies[i % len(proxies)]},  # Rotate or select proxy manually
                callback=self.parse
            )

    def parse(self, response):
        # Your parsing logic here
        self.log(f"Visited {response.text}")
