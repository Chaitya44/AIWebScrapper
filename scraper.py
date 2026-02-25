"""
scraper.py — Pure DrissionPage Scraper
"""

from bs4 import BeautifulSoup, Comment
from DrissionPage import ChromiumPage, ChromiumOptions
import tempfile
import shutil
import random
import time
import os
import traceback
import json

def get_website_content(url: str, headless: bool = False) -> tuple[str | None, str]:
    print(f"\n🕵️ Scraping (Pure DrissionPage): {url}")
    
    is_server = bool(os.environ.get("RENDER") or os.environ.get("CHROMIUM_PATH"))

    temp_user_data = tempfile.mkdtemp()
    
    co = ChromiumOptions()
    co.headless(headless or is_server)
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-gpu')
    co.set_argument('--disable-software-rasterizer')
    co.set_argument(f'--user-data-dir={temp_user_data}')
    co.set_argument('--window-size=1280,720')
    
    if is_server:
        co.set_argument('--disable-extensions')
        co.set_argument('--js-flags=--max-old-space-size=256')
        co.set_argument('--single-process')
        # Fix DrissionPage WebSocket issue in Docker:
        co.set_argument('--remote-debugging-address=0.0.0.0')
        debug_port = random.randint(9200, 9300)
        co.set_argument(f'--remote-debugging-port={debug_port}')
        co.set_local_port(debug_port)
    else:
        co.auto_port()

    chromium_path = os.environ.get("CHROMIUM_PATH")
    if chromium_path:
        co.set_browser_path(chromium_path)
    
    page = None
    api_responses = []
    total_api_bytes = 0
    MAX_API_DATA_BYTES = 50_000
    
    try:
        # Retry logic for Docker cold starts
        max_retries = 3 if is_server else 1
        for attempt in range(max_retries):
            try:
                page = ChromiumPage(addr_or_opts=co)
                break
            except Exception as e:
                print(f"⚠️ Browser attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    print("❌ Browser connection failed completely.")
                    return None, ""
                time.sleep(2)
                
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Only use listener locally to avoid Docker instability
        use_listener = not is_server
        if use_listener:
            try:
                page.listen.start()
            except:
                use_listener = False
                
        page.set.timeouts(page_load=30, script=10)
        
        print(f"🌐 Loading {url}...")
        try:
            page.get(url)
        except Exception as e:
            print(f"⚠️ Page load warning: {e}")
            
        time.sleep(2)
        
        # Scroll
        for _ in range(4):
            page.scroll.down(500)
            time.sleep(0.5)
            
        if use_listener:
            try:
                for packet in page.listen.steps(timeout=2):
                    if not packet.response: continue
                    body = packet.response.body
                    if not body or len(body) < 20: continue
                    try:
                        data = json.loads(body)
                        api_responses.append({"url": packet.url[:200], "data": data})
                        total_api_bytes += len(body)
                        if total_api_bytes > MAX_API_DATA_BYTES: break
                    except:
                        pass
            except:
                pass
            try:
                page.listen.stop()
            except:
                pass
                
        raw_html = page.html
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "svg", "iframe", "noscript"]):
            tag.decompose()
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        clean = " ".join(str(soup.body or soup).split())
        
        api_data_str = ""
        if api_responses:
            api_data_str = json.dumps(api_responses, ensure_ascii=False)[:MAX_API_DATA_BYTES]
            
        print(f"✅ Captured {len(clean):,} chars HTML + {len(api_data_str):,} chars API")
        return clean[:300000], api_data_str
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")
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