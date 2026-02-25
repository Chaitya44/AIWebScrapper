"""
GeminiOrganizer - Universal Data Structuring Engine
Uses Gemini 2.0 to map raw web content into a strict, self-describing JSON schema.
Ensures 100% column alignment by generating the schema from the data itself.

Features:
  - Model fallback chain (gemini-2.0-flash → gemini-1.5-flash → gemini-2.5-flash)
  - Pre-processing to strip HTML noise and save tokens
  - Schema-first extraction for perfectly aligned tables
"""

import os
import json
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ───────────────────────────────────────────────────────────────────
API_KEY = os.getenv("GEMINI_API_KEY")

# ⚡ Model fallback chain — tries each in order if quota is hit
MODEL_CHAIN = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


# ── PROMPT TEMPLATE ──────────────────────────────────────────────────────────

ORGANIZER_PROMPT = """
You are a Universal Web Data Extraction Engine. Your job is to capture ALL meaningful information from ANY webpage and organize it into clean, structured JSON.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — UNDERSTAND THE PAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analyze the entire page. It could be ANYTHING:
- An e-commerce page with products
- A blog or news site with articles
- A social media profile with posts
- A music/video platform with tracks or playlists
- A company page with team members
- A dashboard with stats and metrics
- A forum with threads and replies
- A Wikipedia-style page with text sections
- A restaurant menu, pricing page, event listing, or anything else

Your job: figure out what data exists on this page and capture ALL of it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — DISCOVER CATEGORIES & SCHEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Group the data into logical categories. Examples:
- Products, Songs, Playlists, Articles, Users, Comments, Prices, Stats, Sections, Events, etc.
- If the page has one main entity (e.g. a profile), use a single-item category.
- If the page is text-heavy, create a "PageContent" category with sections/paragraphs.
- ALWAYS create a "PageInfo" category with: pageTitle, pageDescription, pageType.

Schema rules:
- Field names must be camelCase (e.g. "songTitle", "artistName", "playCount").
- Each field must have a declared type: "string" | "number" | "url" | "date" | "boolean".
- If a value is missing for a row, use null — NEVER omit the field.
- Extract as many meaningful fields as possible per item.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — EXTRACT & NORMALIZE DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Using the discovered schema, extract up to 30 items per category.
Every item MUST have every field from the schema (null if missing).
Clean the data: strip HTML tags, normalize currencies to numbers, parse dates to ISO format.
For text content: extract full text, don't truncate meaningful content.
For links: capture both the text and the href URL.
⚠️ CRITICAL: Convert ALL relative URLs (like /platform, /docs/scaling) to FULL absolute URLs using the source domain: {source_url}
For example: /platform → {source_url}/platform

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Return ONLY a JSON object with this exact structure:

{{
  "schema": {{
    "<CategoryName>": {{
      "fields": {{
        "<fieldName>": {{ "type": "<type>", "description": "<brief description>" }}
      }}
    }}
  }},
  "data": {{
    "<CategoryName>": [
      {{ "<fieldName>": <value_or_null> }}
    ]
  }}
}}

RULES:
- DO NOT include any text outside of the JSON.
- Every item in "data" MUST contain ALL fields from its "schema".
- Use null for missing values — NEVER omit a field.
- Category names should be PascalCase (e.g. "Products", "SongList", "TeamMembers").
- You MUST extract data. An empty result is a failure. Even if the page seems sparse, extract whatever text/links/info exists.
- Prefer more categories with fewer items over one giant category.
- If an "INTERCEPTED API DATA" section is present below the HTML, use it as the PRIMARY data source — it contains JSON from XHR/Fetch calls that the page loaded dynamically and is often more complete than the HTML.
- Merge data from both HTML and API data sections. Avoid duplicates.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOURCE URL: {source_url}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAW HTML CONTENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{html_content}
"""


# ── MAIN CLASS ────────────────────────────────────────────────────────────────

class GeminiOrganizer:
    """
    Transforms raw, noisy HTML into a perfectly aligned JSON dataset.

    Usage:
        organizer = GeminiOrganizer()
        result = organizer.organize(cleaned_html)
        # result.data       -> {"Products": [{...}, ...]}
        # result.schema     -> {"Products": {"fields": {...}}}
    """

    def __init__(self, max_chars: int = 80_000):
        self.max_chars = max_chars

    def _preprocess_html(self, html: str) -> str:
        """Strip noise, truncate, remove binary junk to save tokens."""
        # Remove base64 images
        html = re.sub(r'src="data:image/[^"]+"', 'src=""', html)
        # Remove SVG path data
        html = re.sub(r'd="[A-Za-z0-9\s.,\-]+"', '', html)
        # Remove inline styles
        html = re.sub(r'style="[^"]*"', '', html)
        # Remove class attributes (noise for AI)
        html = re.sub(r'class="[^"]*"', '', html)
        # Collapse whitespace
        html = " ".join(html.split())
        return html[:self.max_chars]

    @staticmethod
    def _resolve_relative_urls(data: dict, base_url: str) -> dict:
        """Post-process: convert any remaining relative URLs to absolute."""
        from urllib.parse import urljoin
        if not base_url:
            return data
        for category, items in data.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if isinstance(val, str) and val.startswith('/') and not val.startswith('//'):
                                item[key] = urljoin(base_url, val)
        return data

    def organize(self, raw_html: str, api_key: str = None, source_url: str = "") -> "OrganizedResult":
        """
        Core method. Feed HTML in, get a fully-typed, schema-aligned result out.
        Uses model fallback chain if quota is hit.
        api_key: optional user-provided key (BYOK). Falls back to env var.
        source_url: the URL that was scraped (used to resolve relative URLs).
        """
        key = api_key or API_KEY
        if not key:
            print("[ORGANIZER] ❌ No API key provided (neither user key nor GEMINI_API_KEY env var)")
            return OrganizedResult({}, {})

        start = time.time()
        clean_html = self._preprocess_html(raw_html)
        print(f"[ORGANIZER] HTML: {len(raw_html):,} → {len(clean_html):,} chars")

        prompt = ORGANIZER_PROMPT.format(html_content=clean_html, source_url=source_url or "unknown")

        last_error = None
        for model_name in MODEL_CHAIN:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0  # Maximum determinism
                    )
                )

                elapsed = time.time() - start
                print(f"[ORGANIZER] ⚡ '{model_name}' done in {elapsed:.2f}s")

                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]

                parsed = json.loads(text.strip())

                # Validate structure
                schema = parsed.get("schema", {})
                data = parsed.get("data", {})

                # Enforce schema alignment: ensure every row has all fields
                for category, items in data.items():
                    if isinstance(items, list) and category in schema:
                        fields = list(schema[category].get("fields", {}).keys())
                        for item in items:
                            if isinstance(item, dict):
                                for field in fields:
                                    if field not in item:
                                        item[field] = None

                # Post-process: resolve any remaining relative URLs
                data = self._resolve_relative_urls(data, source_url)

                return OrganizedResult(schema=schema, data=data)

            except json.JSONDecodeError as e:
                print(f"[ORGANIZER] ❌ JSON parse error from '{model_name}': {e}")
                last_error = e
                continue
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"[ORGANIZER] ⚠️ '{model_name}' quota hit, trying next...")
                    last_error = e
                    time.sleep(2)
                    continue
                # Non-quota error
                print(f"[ORGANIZER] ❌ Error from '{model_name}': {e}")
                last_error = e
                continue

        print(f"[ORGANIZER] ❌ All models exhausted. Last error: {last_error}")
        return OrganizedResult({}, {})


# ── RESULT CONTAINER ─────────────────────────────────────────────────────────

class OrganizedResult:
    """
    Clean container for the organizer output.
    Provides helper properties so other modules don't need to know the raw JSON shape.
    """

    def __init__(self, schema: dict, data: dict):
        self.schema = schema
        self.data = data

    @property
    def categories(self) -> list[str]:
        return list(self.data.keys())

    @property
    def total_items(self) -> int:
        return sum(len(v) for v in self.data.values() if isinstance(v, list))

    def to_api_response(self) -> dict:
        """Return the full response payload for the API."""
        return {
            "schema": self.schema,
            "data": self.data,
            "entityCount": len(self.categories),
            "totalItems": self.total_items,
        }

    def __repr__(self):
        return (
            f"<OrganizedResult categories={self.categories} "
            f"total={self.total_items}>"
        )
