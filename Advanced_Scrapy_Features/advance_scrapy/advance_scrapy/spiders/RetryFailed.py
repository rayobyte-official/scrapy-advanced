"""
middlewares.py configuration for automatic retry and error handling.

This RetryFailedRequestsMiddleware class handles:
1. Logging and retrying requests that fail or return non-200 responses.
2. Saving logs for both successful and failed requests.
3. Retrying requests up to the specified max_retries limit (set in settings.py).



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

            

settings.py configuration
DOWNLOADER_MIDDLEWARES = {
     
    "advance_scrapy.middlewares.RetryFailedRequestsMiddleware": 543,   
    # Here, 'advance_scrapy' is my project name. Don't forget to replace 'advance_scrapy' with your project name.
}

# Set the maximum retries for failed requests
MAX_RETRIES = 3
"""
import scrapy

class ErrorHandlingTestSpider(scrapy.Spider):
    name = "error_handling_test"
    start_urls = [
        'https://httpbin.org/status/absac',  # We are intentionally making an invalid URL for testing
        'https://httpbin.org/status/efg',   
        'https://httpbin.org/status/ijk',   
        'https://httpbin.org/ip' #his is the correct URL.
    ]

    def parse(self, response):
        self.logger.info(f"Successfully retrieved: {response.url}")
