import asyncio
import random
from undetected_playwright.async_api import async_playwright, Playwright

# Function to inject JavaScript to create a visible cursor on the page
async def add_visible_cursor(page):
    await page.evaluate("""
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
    """)

# Function to move the custom cursor element on the page
async def move_visible_cursor(page, x, y):
    await page.evaluate(f"""
        const cursor = document.getElementById('customCursor');
        if (cursor) {{
            cursor.style.left = '{x}px';
            cursor.style.top = '{y}px';
        }}
    """)

# Function to perform random mouse movements
async def perform_mouse_movements(page):
    for _ in range(10):
        x = random.randint(100, 1000)
        y = random.randint(100, 700)
        
        # Move Playwright's actual mouse
        await page.mouse.move(x, y)
        # Update the position of the visible cursor
        await move_visible_cursor(page, x, y)
        
        await asyncio.sleep(random.uniform(0.1, 0.5))

# Function to perform random scrolling on the page
async def perform_scrolling(page):
    for _ in range(5):
        scroll_amount = random.randint(200, 800)
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(random.uniform(0.3, 1))

# Function to scrape data with a persistent cursor
async def scrape_data(playwright: Playwright):
    # Launch the browser with stealth settings and proxy
    args = ["--disable-blink-features=AutomationControlled"]
    browser = await playwright.chromium.launch(
                    headless=False, 
                    args=args,
                    proxy={  
                        "server": "server_name:port",
                        "username": "username",
                        "password": "password"
                    }
                )
    
    # Adding a delay to ensure the proxy connection stabilizes
    await asyncio.sleep(3)
    
    page = await browser.new_page()

    # Inject visible cursor
    await add_visible_cursor(page)

    # Go to the target URL
    await page.goto("https://bot.sannysoft.com/")
    
    # Perform random mouse movements
    await perform_mouse_movements(page)

    # Perform random scrolling
    await perform_scrolling(page)

    # Set cursor position at the end
    await move_visible_cursor(page, 500, 300)

    # Wait a few seconds to observe the results on the bot-detection page
    await asyncio.sleep(5)

    # Close the browser
    await browser.close()

# Main function to run the scraper
async def main():
    async with async_playwright() as playwright:
        await scrape_data(playwright)

# Entry point of the script
if __name__ == "__main__":
    asyncio.run(main())
