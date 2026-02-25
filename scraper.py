"""
scraper.py — Hybrid Universal Scraper
Strategy: requests-first (fast, no browser), Selenium fallback (for JS-heavy sites)

Flow:
  1. Try to fetch with requests + BeautifulSoup (< 3 seconds)
  2. If HTML is too thin → site needs JS rendering → fall back to Selenium
  3. On server: Selenium with memory-optimized Chrome
  4. Locally: DrissionPage with full anti-detection + API interception
"""

from bs4 import BeautifulSoup, Comment
import requests as http_requests
import tempfile
import shutil
import random
import time
import os
import traceback


# Threshold: if requests-fetched HTML has less meaningful text, it's a JS-rendered site
SPA_TEXT_THRESHOLD = 500  # characters of visible text


def get_website_content(url: str, headless: bool = False) -> tuple[str | None, str]:
    """
    Fetch a URL and return (cleaned_html, api_data_json_string).
    Uses a fast requests-first approach, falls back to browser for JS sites.
    Returns (None, "") on total failure.
    """
    print(f"\n🕵️ Scraping: {url}")

    # ── PHASE 1: Try fast HTTP fetch (no browser needed) ──
    html = _try_requests_fetch(url)
    if html:
        text_len = len(BeautifulSoup(html, "html.parser").get_text(strip=True))
        if text_len > SPA_TEXT_THRESHOLD:
            print(f"⚡ Fast fetch succeeded ({text_len:,} chars of text) — no browser needed!")
            clean = _clean_html(html)
            return clean[:300000], ""
        else:
            print(f"📡 Thin page ({text_len} chars text) — needs JS rendering, using browser...")
    else:
        print("📡 HTTP fetch failed — using browser fallback...")

    # ── PHASE 2: Browser fallback for JS-rendered sites ──
    is_server = os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH")

    if is_server:
        return _scrape_with_selenium(url)
    else:
        return _scrape_with_drission(url, headless)


def _try_requests_fetch(url: str) -> str | None:
    """Fast HTTP fetch with requests — works for most static/SSR sites."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
        resp = http_requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()

        # Only process HTML responses
        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None

        return resp.text
    except Exception as e:
        print(f"⚠️ HTTP fetch error: {e}")
        return None


def _scrape_with_selenium(url: str) -> tuple[str | None, str]:
    """Server-mode scraping with Selenium (reliable in Docker)."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    print("[Scraper] Server mode — Selenium + ChromeDriver")

    temp_user_data = tempfile.mkdtemp()
    driver = None

    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")  # CRITICAL for Docker: prevents "Timed out receiving message from renderer"
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-browser-side-navigation")  # Prevents renderer timeouts
        opts.add_argument("--window-size=1280,720")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument(f"--user-data-dir={temp_user_data}")
        opts.page_load_strategy = 'eager'  # Don't wait for heavy images/iframes to load

        chromium_path = os.environ.get("CHROMIUM_PATH")
        if chromium_path:
            opts.binary_location = chromium_path

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=opts)
        driver.set_page_load_timeout(40)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"🌐 Loading {url}...")
        try:
            from selenium.common.exceptions import TimeoutException
            driver.get(url)
        except TimeoutException:
            print("⚠️ Page load timeout (Render limits) — using partial content")
        except Exception as load_err:
            print(f"⚠️ Page load warning: {load_err}")

        # Verify navigation succeeded (if it didn't completely fail)
        current = driver.current_url
        if current in ("about:blank", "data:,", "chrome://newtab/"):
            print(f"⚠️ Navigation failed — stuck on {current}")
            return None, ""

        print(f"✅ Loaded: {current}")
        time.sleep(2)

        # Scroll to trigger lazy loading
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(0.5)

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
    """Local-mode scraping with DrissionPage."""
    from DrissionPage import ChromiumPage, ChromiumOptions
    import json

    print("[Scraper] Local mode — DrissionPage")

    temp_user_data = tempfile.mkdtemp()

    co = ChromiumOptions()
    co.headless(headless)
    co.set_argument(f'--window-size={random.randint(1024,1920)},{random.randint(768,1080)}')
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
    MAX_API_DATA_BYTES = 50_000
    SKIP_PATTERNS = [
        "google-analytics", "googletagmanager", "facebook.com/tr",
        "doubleclick", "analytics", "tracking", "sentry", "hotjar",
        "amplitude", "segment", "mixpanel", "clarity.ms",
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".css",
        ".js", "favicon", "beacon", "telemetry",
    ]

    try:
        page = ChromiumPage(addr_or_opts=co)
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Start API listener for SPA data
        use_listener = False
        try:
            page.listen.start()
            use_listener = True
        except Exception:
            pass

        page.get(url)
        time.sleep(2)

        # Scroll
        for _ in range(5):
            page.scroll.down(500)
            time.sleep(random.uniform(0.4, 0.8))

        # Collect API data
        if use_listener:
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

        api_data_str = ""
        if api_responses:
            api_data_str = json.dumps(api_responses, ensure_ascii=False, default=str)[:MAX_API_DATA_BYTES]

        print(f"✅ Captured {len(clean):,} chars HTML + {len(api_data_str):,} chars API")
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
    """Remove scripts, styles, SVGs, comments."""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "svg", "iframe", "noscript"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    clean = str(soup.body or soup)
    return " ".join(clean.split())