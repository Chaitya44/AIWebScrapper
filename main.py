import scraper
import ai_agent
import storage

if __name__ == "__main__":
    # 1. Target URL (Safe practice site)
    url = "http://books.toscrape.com/"

    # 2. Run Scraper
    raw_text = scraper.get_website_content(url)

    if raw_text:
        # 3. Run AI
        structured_data = ai_agent.analyze_data(raw_text)
        print(f"🔍 AI Output: {structured_data}")

        # 4. Save to DB
        storage.save_to_db(structured_data)