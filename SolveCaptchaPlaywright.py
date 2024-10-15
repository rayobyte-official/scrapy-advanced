import asyncio
from playwright.async_api import async_playwright
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

async def solve_captcha(page, api_key, site_key, url):
    # Step 1: Initialize AntiCaptcha solver with provided API key and site details
    solver = recaptchaV2Proxyless()
    solver.set_key(api_key)
    solver.set_website_url(url)
    solver.set_website_key(site_key)

    # Step 2: Attempt to solve the CAPTCHA using the AntiCaptcha service
    captcha_solution = solver.solve_and_return_solution()
    if captcha_solution:
        print(f"Solved CAPTCHA: {captcha_solution}")  # Log the CAPTCHA solution
    else:
        raise Exception("Failed to solve CAPTCHA")  # Raise an exception if solving fails

    # Step 3: Inject CAPTCHA solution into the hidden textarea within the reCAPTCHA iframe
    frames = page.frames
    captcha_frame = None

    # Loop through the frames to find the reCAPTCHA iframe and set the solution
    for frame in frames:
        if "recaptcha" in frame.url:
            captcha_frame = frame
            # Inject the solution directly into the 'g-recaptcha-response' textarea
            await captcha_frame.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_solution}";')
            break
    if not captcha_frame:
        raise Exception("reCAPTCHA iframe not found.")  # Raise an error if iframe is not found

async def main():
    # Define the AntiCaptcha API key, the target URL, and the site key for reCAPTCHA
    api_key = "YOUR API KEY"  # Replace with your AntiCaptcha API key
    url = "https://www.google.com/recaptcha/api2/demo"
    site_key = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"  # Replace with the actual site key

    # Initialize Playwright and launch a browser instance with proxy configuration
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            proxy={  # Configure the proxy server details
                "server": "server_name:port",
                "username": "username",
                "password": "password"
            }
        )
        # Open a new page in the browser
        page = await browser.new_page()

        # Navigate to the target URL
        await page.goto(url)

        # Retry mechanism: attempt to reload the page until the reCAPTCHA iframe is detected
        retries = 5  # Set number of retries
        for attempt in range(retries):
            frames = page.frames
            if any("recaptcha" in frame.url for frame in frames):  # Check for reCAPTCHA iframe
                print("reCAPTCHA iframe found.")
                break
            else:
                # If iframe not found, reload the page and wait for 'networkidle' state
                print(f"reCAPTCHA iframe not found, retrying... ({attempt + 1}/{retries})")
                await page.reload()
                await page.wait_for_load_state("networkidle")  # Ensure full load after reload
                await asyncio.sleep(2)  # Short pause before next retry

        # Solve the CAPTCHA if the iframe was successfully found
        await solve_captcha(page, api_key, site_key, url)

        # Step 4: Submit the form by triggering the JavaScript click event
        await page.evaluate("document.getElementById('recaptcha-demo-submit').click();")

        # Retry mechanism: attempt to retrieve page content after form submission
        retries = 5
        for attempt in range(retries):
            try:
                # Wait for the page to finish loading and retrieve its content
                await page.wait_for_load_state("networkidle")  # Ensure the page is fully loaded
                content = await page.content()  # Retrieve the page HTML content
                print(content)  # Print the page content
                break
            except Exception as e:
                # If an error occurs, retry after a short delay
                print(f"Attempt {attempt + 1}/{retries}: Could not retrieve content due to navigation. Retrying...")
                await asyncio.sleep(2)  # Pause before retrying

        # Close the browser after completion
        await browser.close()

# Run the main function using asyncio
asyncio.run(main())
