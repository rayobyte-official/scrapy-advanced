from selenium import webdriver
from selenium.webdriver.common.by import By
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
import time

# Function to initialize AntiCaptcha solver and return CAPTCHA solution
def solve_captcha(api_key, site_key, url):
    # Initialize the AntiCaptcha solver with the provided API key
    solver = recaptchaV2Proxyless()
    solver.set_key(api_key)
    solver.set_website_url(url)
    solver.set_website_key(site_key)

    # Solve the CAPTCHA using AntiCaptcha service
    captcha_solution = solver.solve_and_return_solution()
    if captcha_solution:
        print(f"Solved CAPTCHA: {captcha_solution}")  # Log CAPTCHA solution
        return captcha_solution
    else:
        raise Exception("Failed to solve CAPTCHA")  # Raise an error if solving fails

# Main function to solve reCAPTCHA using Selenium and AntiCaptcha with proxy
def main():
    # Replace with your actual AntiCaptcha API key, site key, and URL
    api_key = "YOUR API KEY"  # AntiCaptcha API key
    site_key = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"  # reCAPTCHA site key
    url = "https://www.google.com/recaptcha/api2/demo"  # Target URL containing reCAPTCHA

    # Proxy configuration
    proxy_server = "server_name:port"  # Replace with your proxy server and port
    proxy_username = "username"  # Replace with your proxy username
    proxy_password = "password"  # Replace with your proxy password

    # Set up Chrome options for proxy
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server={proxy_server}')

    # Add proxy authentication if necessary (for proxies that require username/password)
    if proxy_username and proxy_password:
        # Chrome does not support proxy authentication directly; use an extension for proxy authentication
        chrome_options.add_extension(create_proxy_auth_extension(proxy_server, proxy_username, proxy_password))

    # Initialize the Chrome WebDriver with configured options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the target URL containing reCAPTCHA
    driver.get(url)
    time.sleep(2)  # Short delay to allow the page to load

    # Solve the CAPTCHA using AntiCaptcha API and get the solution token
    captcha_solution = solve_captcha(api_key, site_key, url)

    # Find the hidden textarea where the CAPTCHA solution will be injected
    g_recaptcha_response = driver.find_element(By.ID, "g-recaptcha-response")

    # Inject the CAPTCHA solution into the hidden textarea field
    driver.execute_script(f"arguments[0].style.display = 'block';", g_recaptcha_response)  # Make textarea visible
    g_recaptcha_response.send_keys(captcha_solution)  # Inject CAPTCHA solution

    # Submit the form containing the reCAPTCHA (adjust selector to match your page structure)
    submit_button = driver.find_element(By.ID, "recaptcha-demo-submit")  # Find the submit button
    submit_button.click()  # Click to submit the form

    # Wait for some time to observe the result and confirm CAPTCHA is solved
    time.sleep(5)

    # Print page source after CAPTCHA submission
    print(driver.page_source)

    # Close the WebDriver after completion
    driver.quit()

# Function to create proxy authentication extension
# Function to create proxy authentication extension
def create_proxy_auth_extension(proxy_host, proxy_user, proxy_pass):
    import zipfile
    import os

    # Separate the host and port
    host = proxy_host.split(':')[0]  # Extract the host part (e.g., "la.residential.rayobyte.com")
    port = proxy_host.split(':')[1]  # Extract the port part (e.g., "8000")

    # Define proxy extension files
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

    # Create the extension
    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile
# Run the main function
main()
