"""
scraper.py — Universal DrissionPage Scraper with Network Interception
Based on the original AI-WebScraper project by Chaitya44.

Flow:
  1. Launch Chromium with anti-detection (randomized viewport, no webdriver flag)
  2. Start network listener to capture API/XHR/Fetch responses
  3. Navigate to URL and scroll to trigger lazy loading
  4. Collect both rendered HTML and intercepted API JSON data
  5. Clean HTML with BeautifulSoup
  6. Return clean HTML + API data → GeminiOrganizer handles the rest
"""

from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup, Comment
import tempfile
import shutil
import random
import time
import os
import json
import traceback


# Max bytes of API data to collect (avoid token overload)
MAX_API_DATA_BYTES = 50_000

# Content types that indicate useful API JSON data
JSON_CONTENT_TYPES = {"application/json", "text/json"}

# URL patterns to SKIP (tracking, analytics, ads — not useful data)
SKIP_PATTERNS = [
    "google-analytics", "googletagmanager", "facebook.com/tr",
    "doubleclick", "analytics", "tracking", "sentry", "hotjar",
    "amplitude", "segment", "mixpanel", "clarity.ms", ".png",
    ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".css",
    ".js", "favicon", "beacon", "log", "telemetry",
]


def _is_useful_api_response(url: str, body: str) -> bool:
    """Filter out tracking/analytics/asset requests, keep real API data."""
    url_lower = url.lower()
    if any(skip in url_lower for skip in SKIP_PATTERNS):
        return False
    # Must be JSON-parseable and non-trivial
    if not body or len(body) < 20:
        return False
    try:
        data = json.loads(body)
        # Skip if it's just a status or tiny object
        if isinstance(data, dict) and len(data) <= 2:
            return False
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def get_website_content(url: str, headless: bool = False) -> tuple[str | None, str]:
    """
    Fetch a URL and return (cleaned_html, api_data_json_string).
    The api_data is a JSON string of intercepted API responses.
    Returns (None, "") on total failure.
    """
    print(f"\n🕵️ Stealth Scraping: {url}")

    # Auto-detect server environment — force headless if no display
    if os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH"):
        headless = True
        print("[Scraper] Server detected — forcing headless mode")

    # Create a temporary user profile — every run looks like a fresh computer
    temp_user_data = tempfile.mkdtemp()

    is_server = os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH")

    # Randomize the viewport — bots usually have standard sizes
    width = random.randint(1024, 1920)
    height = random.randint(768, 1080)

    co = ChromiumOptions()
    if is_server:
        # Server/Docker: use new headless mode and conservative flags
        co.set_argument('--headless=new')
    else:
        co.headless(headless)
    co.set_argument(f'--window-size={width},{height}')
    co.set_argument(f'--user-data-dir={temp_user_data}')
    co.set_argument('--no-first-run')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-gpu')
    co.set_argument('--disable-software-rasterizer')
    # --single-process crashes in Docker; only use locally
    if not is_server:
        co.set_argument('--single-process')
    co.auto_port()

    # Set Chromium binary path from environment (for Docker/Render)
    chromium_path = os.environ.get("CHROMIUM_PATH")
    if chromium_path:
        co.set_browser_path(chromium_path)

    page = None
    api_responses = []
    total_api_bytes = 0
    use_listener = True  # Will be disabled if it causes issues

    try:
        page = ChromiumPage(addr_or_opts=co)

        # Anti-detection: remove the webdriver flag
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # ── START NETWORK LISTENER before navigating ──
        # This captures XHR/Fetch API responses that SPAs load dynamically
        try:
            page.listen.start()
            print("📡 Network listener active — capturing API calls...")
        except Exception as listen_err:
            print(f"⚠️ Network listener unavailable: {listen_err}")
            use_listener = False

        page.get(url)

        # Wait for page to stabilize
        print("⏳ Waiting for page to stabilize...")
        time.sleep(3)

        # Scroll to trigger lazy loading
        print("⬇️ Scrolling to wake up the page...")
        for _ in range(8):
            page.scroll.down(500)
            time.sleep(random.uniform(0.5, 1.2))

        # If page looks empty, wait longer
        if len(page.html) < 2000:
            print("⚠️ Page looks empty. Waiting longer...")
            time.sleep(5)

        # ── COLLECT INTERCEPTED API RESPONSES ──
        if use_listener:
            try:
                # Drain all captured packets (non-blocking, with short timeout)
                for packet in page.listen.steps(timeout=2):
                    if not packet.response:
                        continue
                    try:
                        body = packet.response.body
                        if body and _is_useful_api_response(packet.url, body):
                            if total_api_bytes + len(body) > MAX_API_DATA_BYTES:
                                break  # Cap total data
                            api_responses.append({
                                "url": packet.url[:200],  # Truncate long URLs
                                "data": json.loads(body),
                            })
                            total_api_bytes += len(body)
                    except Exception:
                        pass  # Skip malformed packets
            except Exception as drain_err:
                print(f"⚠️ Error draining packets: {drain_err}")

            try:
                page.listen.stop()
            except Exception:
                pass

        if api_responses:
            print(f"📡 Captured {len(api_responses)} API responses ({total_api_bytes:,} bytes)")
        else:
            print("📡 No API responses intercepted (static page)")

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

        # Build API data string
        api_data_str = ""
        if api_responses:
            api_data_str = json.dumps(api_responses, ensure_ascii=False, default=str)[:MAX_API_DATA_BYTES]

        print(f"✅ Captured {len(clean_html):,} chars HTML + {len(api_data_str):,} chars API data")
        return clean_html[:300000], api_data_str

    except Exception as e:
        print(f"❌ Scraper Error: {e}")
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