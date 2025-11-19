
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://127.0.0.1:5001/game-contents/game-modes")
        await page.screenshot(path="verification/game_modes_fixed.png")
        await browser.close()

asyncio.run(main())
