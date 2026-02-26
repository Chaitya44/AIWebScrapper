from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
import json
import traceback
import os
import scraper
import ai_agent
from fastapi.responses import JSONResponse

app = FastAPI(title="NEXUS SCRAPER API", version="3.0.0")

# CORS — explicit origins (wildcard + credentials = blocked by browsers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aria-19.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ────────────────────────────────────────────────

class ScraperConfig(BaseModel):
    stealthMode: bool = True
    headlessMode: bool = False  # Visible browser = more trusted by websites
    geminiParsing: bool = True
    deepScroll: bool = False


class ScrapeRequest(BaseModel):
    url: str
    config: ScraperConfig = ScraperConfig()
    geminiKey: str = None  # BYOK: user-provided Gemini API key


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
@app.head("/")
async def root():
    return {"status": "alive"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "NEXUS SCRAPER API",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/scrape")
async def scrape_url(request: ScrapeRequest):
    print(f"\n{'='*60}")
    print(f"[API] Scrape request: {request.url}")
    print(f"[API] Config: headless={request.config.headlessMode}, stealth={request.config.stealthMode}")
    print(f"{'='*60}")

    try:
        loop = asyncio.get_event_loop()

        # ── Phase 1: Scrape the page ─────────────────────────────────────
        print("[API] Phase 1: Scraping...")
        scrape_result = await loop.run_in_executor(
            None,
            scraper.get_website_content,
            request.url,
            request.config.headlessMode
        )

        # Unpack (html, api_data) tuple
        html, api_data = scrape_result if isinstance(scrape_result, tuple) else (scrape_result, "")

        if not html:
            raise HTTPException(status_code=500, detail="Failed to fetch website content. The page may be blocking scrapers or the URL may be invalid.")

        print(f"[API] HTML retrieved: {len(html):,} chars")
        if api_data:
            print(f"[API] API data captured: {len(api_data):,} chars")

        # Combine HTML + API data for richer extraction
        combined = html
        if api_data:
            combined = html + "\n\n===== INTERCEPTED API DATA (JSON from XHR/Fetch calls) =====\n" + api_data

        # ── Phase 2: AI Extraction via GeminiOrganizer ───────────────────
        print("[API] Phase 2: Gemini AI extraction (schema-aware)...")
        # BYOK: pass user key (never logged)
        result = await loop.run_in_executor(
            None,
            lambda: ai_agent.extract_structured(combined, api_key=request.geminiKey, source_url=request.url)
        )

        api_payload = result.to_api_response()
        
        # Ensure payload is JSON-serializable
        serializable_payload = json.loads(json.dumps(api_payload, default=str))

        if serializable_payload.get('entityCount', 0) == 0 and serializable_payload.get('totalItems', 0) == 0 and not request.geminiKey:
            raise HTTPException(status_code=400, detail="No API key provided. Please enter your Gemini API key in the settings.")
        print(f"[API] ✅ Extracted {serializable_payload.get('entityCount')} categories, {serializable_payload.get('totalItems')} items")

        return {
            "status": "success",
            **serializable_payload,
            "timestamp": datetime.now().isoformat(),
            "url": request.url
        }

    except HTTPException as he:
        print(f"[API] ❌ HTTPException: {he.detail}")
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        print(f"[API] ❌ Error: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("[API] NEXUS SCRAPER API v3.0 — Schema-Aware Edition")
    print("=" * 60)
    print("[INFO] API URL:       http://localhost:8000")
    print("[INFO] Health Check:  http://localhost:8000/api/health")
    print("[INFO] Scrape:        POST http://localhost:8000/api/scrape")
    print("=" * 60 + "\n")

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
