from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup, Comment
import tempfile
import shutil
import random
import time
import os


def get_website_content(url):
    print(f"🕵️ Student Stealth Mode: {url}")

    # TRICK 1: Create a temporary user profile
    # This makes every run look like a "fresh" computer to the website.
    temp_user_data = tempfile.mkdtemp()

    # TRICK 2: Randomize the Viewport (Window Size)
    # Bots usually have standard sizes (800x600). We randomize it to look human.
    width = random.randint(1024, 1920)
    height = random.randint(768, 1080)

    co = ChromiumOptions()
    co.headless(False)  # MUST BE FALSE. Visible windows are trusted more.
    co.set_argument(f'--window-size={width},{height}')
    co.set_argument(f'--user-data-dir={temp_user_data}')
    co.set_argument('--no-first-run')
    co.auto_port()

    page = None
    try:
        page = ChromiumPage(addr_or_opts=co)

        # TRICK 3: Anti-Detection Scripts
        # These remove the "I am a robot" flags that Chrome sends by default.
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.get(url)

        # TRICK 4: "Human" Interaction Logic
        # Instead of a fixed sleep, we wait for the network to stop moving.
        print("⏳ Waiting for page to stabilize...")

        # Dynamic Wait: Wait 2s, then scroll, then wait again.
        # This triggers "Lazy Loading" on Zillow/Spotify.
        time.sleep(3)

        print("⬇️ Scrolling to wake up the page...")
        for _ in range(4):
            page.scroll.down(400)  # Small scroll, like a mouse wheel
            time.sleep(random.uniform(0.5, 1.2))  # Random pause

        # Check for empty page (common block)
        if len(page.html) < 2000:
            print("⚠️ Page looks empty. Waiting longer...")
            time.sleep(5)

        # FINAL GRAB
        raw_html = page.html

        # CLEANUP: Remove junk to save AI tokens
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "svg", "img", "video", "header", "footer", "iframe", "meta"]):
            tag.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        clean_html = str(soup.body)
        clean_html = " ".join(clean_html.split())

        print(f"✅ Success! Captured {len(clean_html)} chars.")
        return clean_html[:300000]

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    finally:
        # cleanup
        if page:
            try:
                page.quit()
            except:
                pass
        try:
            shutil.rmtree(temp_user_data, ignore_errors=True)
        except:
            pass