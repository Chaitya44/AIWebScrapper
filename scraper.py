"""
scraper.py — Universal Scraper (DrissionPage local, Selenium server)
Based on the original AI-WebScraper project by Chaitya44.

Flow:
  1. Detect environment (local vs server/Docker)
  2. Launch browser with optimal settings
  3. Quick SPA detection — if HTML is thin, scroll more to trigger API loads
  4. Clean HTML with BeautifulSoup
  5. Return clean HTML → GeminiOrganizer handles the rest
"""

from bs4 import BeautifulSoup, Comment
import tempfile
import shutil
import random
import time
import os
import traceback


def get_website_content(url: str, headless: bool = False) -> tuple[str | None, str]:
    """
    Fetch a URL and return (cleaned_html, api_data_json_string).
    Uses Selenium on server, DrissionPage locally.
    Returns (None, "") on total failure.
    """
    print(f"\n🕵️ Stealth Scraping: {url}")

    is_server = os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH")

    if is_server:
        return _scrape_with_selenium(url)
    else:
        return _scrape_with_drission(url, headless)


def _scrape_with_selenium(url: str) -> tuple[str | None, str]:
    """Server-mode scraping with Selenium (reliable in Docker)."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, WebDriverException

    print("[Scraper] Server mode — using Selenium + ChromeDriver")

    temp_user_data = tempfile.mkdtemp()
    driver = None

    try:
        opts = Options()
        # Headless + critical Docker flags
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        # Memory optimization for Render free tier (512MB)
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-software-rasterizer")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-background-networking")
        opts.add_argument("--disable-default-apps")
        opts.add_argument("--disable-sync")
        opts.add_argument("--disable-translate")
        opts.add_argument("--disable-backgrounding-occluded-windows")
        opts.add_argument("--disable-renderer-backgrounding")
        opts.add_argument("--disable-background-timer-throttling")
        opts.add_argument("--js-flags=--max-old-space-size=256")
        opts.add_argument("--disable-features=VizDisplayCompositor,TranslateUI")
        opts.add_argument("--blink-settings=imagesEnabled=false")  # Skip images = huge memory save

        opts.add_argument(f"--user-data-dir={temp_user_data}")
        opts.add_argument("--window-size=1280,720")
        opts.add_argument("--disable-blink-features=AutomationControlled")

        # Set Chromium binary
        chromium_path = os.environ.get("CHROMIUM_PATH")
        if chromium_path:
            opts.binary_location = chromium_path

        # Use chromedriver from system
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=opts)

        # Anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Navigate with timeout protection
        driver.set_page_load_timeout(25)
        try:
            driver.get(url)
        except TimeoutException:
            print("⚠️ Page load timed out — using partial content")

        # Brief wait for JS to execute
        time.sleep(2)

        # Quick SPA check
        initial_len = len(driver.page_source)
        is_spa = initial_len < 10000

        if is_spa:
            print(f"⚡ SPA detected ({initial_len:,} chars) — extra scrolling...")
            scroll_count = 5
        else:
            print(f"📄 Rich HTML ({initial_len:,} chars) — light scrolling...")
            scroll_count = 3

        # Scroll to trigger lazy loading
        for _ in range(scroll_count):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(0.5)

        # Grab final HTML
        raw_html = driver.page_source
        clean = _clean_html(raw_html)

        print(f"✅ Captured {len(clean):,} chars")
        return clean[:300000], ""

    except Exception as e:
        print(f"❌ Selenium Error: {e}")
        traceback.print_exc()
        return None, ""

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        try:
            shutil.rmtree(temp_user_data, ignore_errors=True)
        except:
            pass


def _scrape_with_drission(url: str, headless: bool) -> tuple[str | None, str]:
    """Local-mode scraping with DrissionPage (better anti-detection)."""
    from DrissionPage import ChromiumPage, ChromiumOptions
    import json

    print("[Scraper] Local mode — using DrissionPage")

    temp_user_data = tempfile.mkdtemp()
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
    co.set_argument('--disable-gpu')
    co.set_argument('--single-process')
    co.auto_port()

    page = None
    api_responses = []
    total_api_bytes = 0

    # Max API data to capture
    MAX_API_DATA_BYTES = 50_000
    SKIP_PATTERNS = [
        "google-analytics", "googletagmanager", "facebook.com/tr",
        "doubleclick", "analytics", "tracking", "sentry", "hotjar",
        "amplitude", "segment", "mixpanel", "clarity.ms", ".png",
        ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".css", ".js",
        "favicon", "beacon", "telemetry",
    ]

    try:
        page = ChromiumPage(addr_or_opts=co)
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.get(url)
        time.sleep(2)

        # Quick SPA check
        initial_len = len(page.html)
        is_spa = initial_len < 10000

        if is_spa:
            print(f"⚡ SPA detected ({initial_len:,} chars) — enabling API listener + extra scrolling...")
            try:
                page.listen.start()
            except Exception:
                is_spa = False  # Listener failed, skip
            scroll_count = 6
        else:
            print(f"📄 Rich HTML ({initial_len:,} chars) — light scrolling...")
            scroll_count = 3

        # Scroll
        for _ in range(scroll_count):
            page.scroll.down(500)
            time.sleep(random.uniform(0.4, 0.8))

        # Collect API data only for SPAs
        if is_spa:
            try:
                for packet in page.listen.steps(timeout=2):
                    if not packet.response:
                        continue
                    try:
                        body = packet.response.body
                        if not body or len(body) < 20:
                            continue
                        url_lower = packet.url.lower()
                        if any(skip in url_lower for skip in SKIP_PATTERNS):
                            continue
                        data = json.loads(body)
                        if isinstance(data, dict) and len(data) <= 2:
                            continue
                        if total_api_bytes + len(body) > MAX_API_DATA_BYTES:
                            break
                        api_responses.append({"url": packet.url[:200], "data": data})
                        total_api_bytes += len(body)
                    except (json.JSONDecodeError, ValueError):
                        pass
            except Exception:
                pass
            try:
                page.listen.stop()
            except Exception:
                pass

        if api_responses:
            print(f"📡 Captured {len(api_responses)} API responses ({total_api_bytes:,} bytes)")

        raw_html = page.html
        clean = _clean_html(raw_html)

        # Build API data string
        api_data_str = ""
        if api_responses:
            api_data_str = json.dumps(api_responses, ensure_ascii=False, default=str)[:MAX_API_DATA_BYTES]

        print(f"✅ Captured {len(clean):,} chars HTML + {len(api_data_str):,} chars API data")
        return clean[:300000], api_data_str

    except Exception as e:
        print(f"❌ DrissionPage Error: {e}")
        traceback.print_exc()
        return None, ""

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


def _clean_html(raw_html: str) -> str:
    """Remove scripts, styles, SVGs, comments — keep meaningful content."""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "svg", "iframe", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    clean = str(soup.body or soup)
    return " ".join(clean.split())