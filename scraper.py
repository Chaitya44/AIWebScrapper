from DrissionPage import ChromiumPage, ChromiumOptions
import time
from bs4 import BeautifulSoup


def get_website_content(url):
    """
    Uses DrissionPage to bypass Cloudflare and scrape data.
    """
    print(f"🕵️‍♂️ Launching DrissionPage for: {url}")

    # 1. Setup options to look like a real user
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')  # Helps on some systems

    # CRITICAL: Mute audio so the browser doesn't make noise
    co.set_argument('--mute-audio')

    try:
        # 2. Start the browser
        # DrissionPage finds your existing Chrome installation automatically
        page = ChromiumPage(co)

        # 3. Visit the URL
        page.get(url)

        # 4. ANTI-BOT HANDLING (The "Cyborg" Part)
        print("⏳ Analyzing page for protection...")
        time.sleep(3)  # Wait for redirects

        # Check if we are on a "Just a moment..." or "Access denied" page
        if "Just a moment" in page.title or "Access denied" in page.title or "Cloudflare" in page.title:
            print("⚠️ Cloudflare/Captcha detected! Attempting bypass...")

            # DrissionPage can look inside the "Shadow DOM" (where Cloudflare hides)
            # We look for the checkbox wrapper and try to click it
            try:
                # Common Cloudflare ID
                if page.ele("@id=turnstile-wrapper", timeout=2):
                    page.ele("@id=turnstile-wrapper").click()
                    print("✅ Clicked Turnstile verification.")
                    time.sleep(3)

                # Sometimes it's a specific challenge frame
                elif page.ele("tag:iframe@src^https://challenges.cloudflare.com", timeout=2):
                    iframe = page.get_frame("tag:iframe@src^https://challenges.cloudflare.com")
                    if iframe and iframe.ele("tag:input@type=checkbox"):
                        iframe.ele("tag:input@type=checkbox").click()
                        print("✅ Clicked Challenge Checkbox.")
                        time.sleep(3)

            except Exception as e:
                print(f"⚠️ Auto-click failed: {e}. Waiting for manual solve...")
                # If auto-click fails, we wait for YOU to do it
                time.sleep(10)

                # 5. Wait for real content to load
        # We assume real content is loaded when the title changes or text appears
        time.sleep(3)

        # 6. Scroll to load lazy data (images/products)
        print("📜 Scrolling to load data...")
        page.scroll.to_bottom()
        time.sleep(1)
        page.scroll.to_top()

        # 7. Extract HTML
        html_content = page.html

        # Close the browser connection (keeps browser open usually, but we disconnect)
        page.quit()

        # 8. Clean with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove junk elements
        for element in soup(["script", "style", "nav", "footer", "iframe", "svg"]):
            element.extract()

        # Get clean text
        clean_text = soup.get_text(separator=' ', strip=True)
        return clean_text[:15000]  # Return first 15k chars

    except Exception as e:
        print(f"❌ DrissionPage Error: {e}")
        try:
            page.quit()
        except:
            pass
        return None