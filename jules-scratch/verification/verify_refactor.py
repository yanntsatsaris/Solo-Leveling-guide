from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:5001/")
    page.screenshot(path="jules-scratch/verification/home.png")
    page.goto("http://127.0.0.1:5001/characters")
    page.screenshot(path="jules-scratch/verification/characters.png")
    page.goto("http://127.0.0.1:5001/SJW")
    page.screenshot(path="jules-scratch/verification/sjw.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
