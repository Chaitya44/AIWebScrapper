"""
scraper.py — Clean DrissionPage Scraper
Based on the original AI-WebScraper project by Chaitya44.

Flow:
  1. Launch Chromium with anti-detection tricks (randomized viewport, no webdriver flag)
  2. Scroll to trigger lazy loading
  3. Clean HTML with BeautifulSoup
  4. Return clean HTML → GeminiOrganizer handles the rest
"""

from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup, Comment
import tempfile
import shutil
import random
import time
import os
import traceback


def get_website_content(url: str, headless: bool = False) -> str:
    """
    Fetch a URL and return cleaned HTML text.
    Returns None on total failure.
    """
    print(f"\n🕵️ Stealth Scraping: {url}")

    # Auto-detect server environment — force headless if no display
    if os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH"):
        headless = True
        print("[Scraper] Server detected — forcing headless mode")

    # Create a temporary user profile — every run looks like a fresh computer
    temp_user_data = tempfile.mkdtemp()

    # Randomize the viewport — bots usually have standard sizes
    width = random.randint(1024, 1920)
    height = random.randint(768, 1080)

    co = ChromiumOptions()
    co.headless(headless)
    co.set_argument(f'--window-size={width},{height}')
    co.set_argument(f'--user-data-dir={temp_user_data}')
    co.set_argument('--no-first-run')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.auto_port()

    # Set Chromium binary path from environment (for Docker/Render)
    chromium_path = os.environ.get("CHROMIUM_PATH")
    if chromium_path:
        co.set_browser_path(chromium_path)

    page = None
    try:
        page = ChromiumPage(addr_or_opts=co)

        # Anti-detection: remove the webdriver flag
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.get(url)

        # Wait for page to stabilize
        print("⏳ Waiting for page to stabilize...")
        time.sleep(3)

        # Scroll to trigger lazy loading
        print("⬇️ Scrolling to wake up the page...")
        for _ in range(4):
            page.scroll.down(400)
            time.sleep(random.uniform(0.5, 1.2))

        # If page looks empty, wait longer
        if len(page.html) < 2000:
            print("⚠️ Page looks empty. Waiting longer...")
            time.sleep(5)

        # Grab the HTML
        raw_html = page.html

        # Clean with BeautifulSoup — remove only truly useless tags
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "svg", "iframe", "noscript"]):
            tag.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        clean_html = str(soup.body or soup)
        clean_html = " ".join(clean_html.split())

        print(f"✅ Captured {len(clean_html):,} chars")
        return clean_html[:300000]

    except Exception as e:
        print(f"❌ Scraper Error: {e}")
        traceback.print_exc()
        return None

    finally:
        if page:
            try:
                page.quit()
            except:
                pass
        try:
            shutil.rmtree(temp_user_data, ignore_errors=True)
        except:
            pass