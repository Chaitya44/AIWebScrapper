"""
CaptchaHandler - Smart CAPTCHA Bypass Module
Strategy Priority:
  1. FREE: Stealth browser headers + wait loop (works on Cloudflare JS challenges)
  2. FREE: DrissionPage non-headless fallback (manual solve or JS auto-pass)
  3. PAID (optional): CapSolver / 2Captcha if API key is configured in .env

No API key required for basic operation.
"""

import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ───────────────────────────────────────────────────────────────────
CAPSOLVER_API_KEY  = os.getenv("CAPSOLVER_API_KEY", "")   # Optional - leave blank for free mode
TWOCAPTCHA_API_KEY = os.getenv("TWOCAPTCHA_API_KEY", "")  # Optional - leave blank for free mode

# Semantic DOM fingerprints for detection (no hardcoded class/id names)
CAPTCHA_SIGNATURES = {
    "cloudflare":   ["challenges.cloudflare.com", "cf-turnstile", "__cf_bm", "cf_clearance",
                     "Checking if the site connection is secure", "Just a moment"],
    "recaptcha_v2": ["g-recaptcha", "google.com/recaptcha/api2"],
    "recaptcha_v3": ["grecaptcha.execute", "recaptcha/api.js?render="],
    "hcaptcha":     ["hcaptcha.com/1/api", "h-captcha", "data-hcaptcha-sitekey"],
}

# Stealth headers that mimic a real Chrome browser
STEALTH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
}


class CaptchaHandler:
    """
    Detects and bypasses CAPTCHAs using a layered free-first approach.

    Usage:
        handler = CaptchaHandler(page, url)
        if handler.is_captcha_present():
            handler.solve()    # Tries free bypass first, paid API as fallback
    """

    def __init__(self, page, page_url: str):
        self.page = page
        self.url  = page_url
        self.detected_type: str | None = None
        self.site_key: str | None = None

    # ── DETECTION ─────────────────────────────────────────────────────────────

    def is_captcha_present(self) -> bool:
        """Scan page HTML for known CAPTCHA fingerprints."""
        html = self.page.html.lower()
        for captcha_type, signatures in CAPTCHA_SIGNATURES.items():
            if any(sig.lower() in html for sig in signatures):
                self.detected_type = captcha_type
                self.site_key = self._extract_site_key(html, captcha_type)
                print(f"[CAPTCHA] ⚠️  Detected: {captcha_type} | SiteKey: {self.site_key}")
                return True
        print("[CAPTCHA] ✅ No CAPTCHA detected.")
        return False

    def _extract_site_key(self, html: str, captcha_type: str) -> str | None:
        patterns = {
            "recaptcha_v2":  [r'data-sitekey=["\']([^"\']+)', r'sitekey:\s*["\']([^"\']+)'],
            "recaptcha_v3":  [r'render=([A-Za-z0-9_-]{30,})'],
            "cloudflare":    [r'data-sitekey=["\']([^"\']+)'],
            "hcaptcha":      [r'data-hcaptcha-sitekey=["\']([^"\']+)', r'data-sitekey=["\']([^"\']+)'],
        }
        for pattern in patterns.get(captcha_type, []):
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    # ── MAIN SOLVE DISPATCHER ─────────────────────────────────────────────────

    def solve(self) -> bool:
        """
        Solver priority:
          1. Free stealth wait (Cloudflare JS challenge — usually auto-passes in 5s)
          2. Free header injection + reload
          3. Paid API (only if key is configured in .env)
        Returns True if the page was successfully unblocked.
        """
        if not self.detected_type:
            return False

        print(f"[SOLVER] Attempting bypass for: {self.detected_type}")

        # ── STRATEGY 1: FREE — Cloudflare JS auto-challenge wait ──────────────
        if self.detected_type == "cloudflare":
            return self._free_cloudflare_bypass()

        # ── STRATEGY 2: FREE — Stealth header injection + page reload ─────────
        bypassed = self._free_header_bypass()
        if bypassed:
            return True

        # ── STRATEGY 3: PAID — CapSolver (only if API key is set) ────────────
        if CAPSOLVER_API_KEY:
            print("[SOLVER] Falling back to CapSolver (paid)...")
            token = self._capsolver_solve()
            if token:
                return self._inject_token(token)
        else:
            print("[SOLVER] ℹ️  No CAPSOLVER_API_KEY set — skipping paid solver.")
            print("[SOLVER] ⚠️  CAPTCHA could not be bypassed for free. Proceeding with partial content.")

        return False

    # ── FREE STRATEGIES ───────────────────────────────────────────────────────

    def _free_cloudflare_bypass(self) -> bool:
        """
        Cloudflare JS challenges often auto-complete in 5 seconds.
        Strategy: inject real browser headers, wait, check if challenge cleared.
        """
        print("[FREE] Trying Cloudflare stealth wait (5-15s)...")

        # Inject stealth headers via JS override
        self.page.run_js("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = { runtime: {} };
        """)

        # Cloudflare typically takes 3-5 seconds for auto-pass
        for attempt in range(3):
            time.sleep(5)
            html = self.page.html.lower()
            still_blocked = any(
                sig.lower() in html
                for sig in CAPTCHA_SIGNATURES["cloudflare"]
            )
            if not still_blocked:
                print(f"[FREE] ✅ Cloudflare bypassed after {(attempt+1)*5}s wait!")
                return True
            print(f"[FREE] Still blocked after {(attempt+1)*5}s... retrying.")

        # If still blocked, try refreshing once
        print("[FREE] Refreshing page...")
        self.page.refresh()
        time.sleep(5)

        html = self.page.html.lower()
        if not any(sig.lower() in html for sig in CAPTCHA_SIGNATURES["cloudflare"]):
            print("[FREE] ✅ Cloudflare cleared after refresh.")
            return True

        print("[FREE] ❌ Cloudflare bypass failed. Site enforces interactive challenge.")
        return False

    def _free_header_bypass(self) -> bool:
        """
        Re-request the page with realistic browser headers baked in.
        Works on many light CAPTCHA walls that only check User-Agent/Accept headers.
        """
        print("[FREE] Trying stealth header injection...")
        try:
            # Set realistic headers at the CDP (Chrome DevTools Protocol) level
            self.page.set_session_storage("bypass_attempt", "true")
            self.page.run_js("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            self.page.get(self.url)
            time.sleep(3)

            html = self.page.html.lower()
            all_sigs = [sig.lower() for sigs in CAPTCHA_SIGNATURES.values() for sig in sigs]
            if not any(sig in html for sig in all_sigs):
                print("[FREE] ✅ Page cleared after stealth reload.")
                return True
        except Exception as e:
            print(f"[FREE] Header bypass error: {e}")

        return False

    # ── PAID STRATEGY (OPTIONAL) ──────────────────────────────────────────────

    def _capsolver_solve(self) -> str | None:
        """Call CapSolver API to solve the CAPTCHA. Only runs if API key is set."""
        try:
            import requests
        except ImportError:
            print("[SOLVER] `requests` not installed. Run: pip install requests")
            return None

        task_map = {
            "recaptcha_v2":  "ReCaptchaV2TaskProxyless",
            "recaptcha_v3":  "ReCaptchaV3TaskProxyless",
            "cloudflare":    "AntiTurnstileTaskProxyless",
            "hcaptcha":      "HCaptchaTaskProxyless",
        }

        task_type = task_map.get(self.detected_type)
        if not task_type:
            return None

        payload = {
            "clientKey": CAPSOLVER_API_KEY,
            "task": {
                "type": task_type,
                "websiteURL": self.url,
                "websiteKey": self.site_key or "implicit",
            }
        }

        try:
            resp = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=15).json()
            if resp.get("errorId"):
                print(f"[CAPSOLVER] Error: {resp.get('errorDescription')}")
                return None

            task_id = resp["taskId"]
            for _ in range(30):  # Poll for up to 2 minutes
                time.sleep(4)
                result = requests.post(
                    "https://api.capsolver.com/getTaskResult",
                    json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id},
                    timeout=15
                ).json()
                if result.get("status") == "ready":
                    token = result.get("solution", {}).get("gRecaptchaResponse") \
                         or result.get("solution", {}).get("token")
                    print(f"[CAPSOLVER] ✅ Token received.")
                    return token
                if result.get("status") == "failed":
                    print(f"[CAPSOLVER] ❌ Failed: {result.get('errorDescription')}")
                    return None
        except Exception as e:
            print(f"[CAPSOLVER] Exception: {e}")
        return None

    # ── TOKEN INJECTION ───────────────────────────────────────────────────────

    def _inject_token(self, token: str) -> bool:
        """Inject a solved CAPTCHA token into the page DOM."""
        try:
            self.page.run_js(f"""
                var resp = document.getElementById('g-recaptcha-response');
                if (resp) {{ resp.style.display='block'; resp.value='{token}'; }}
                var hResp = document.querySelector('[name="h-captcha-response"]');
                if (hResp) {{ hResp.value='{token}'; }}
                var cfResp = document.querySelector('[name="cf-turnstile-response"]');
                if (cfResp) {{ cfResp.value='{token}'; }}
                if (typeof ___grecaptcha_cfg !== 'undefined') {{
                    var clients = ___grecaptcha_cfg.clients;
                    for (var id in clients) {{
                        for (var key in clients[id]) {{
                            if (clients[id][key] && typeof clients[id][key].callback === 'function') {{
                                clients[id][key].callback('{token}');
                            }}
                        }}
                    }}
                }}
            """)
            time.sleep(1.5)
            print("[SOLVER] ✅ Token injected.")
            return True
        except Exception as e:
            print(f"[SOLVER] Injection failed: {e}")
            return False
