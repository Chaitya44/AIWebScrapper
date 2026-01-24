# 🕷️ AIWebscrapper : Gemini-Powered Universal Web Scraper

AIWebScraper is a Python-based tool that uses Google Gemini AI and DrissionPage to extract structured JSON data from any website. Unlike traditional scrapers, it uses LLMs to understand content, allowing it to bypass anti-bot protections and parse dynamic HTML automatically.

🚀 Overview

This project solves the "Universal Scraper" problem by combining two technologies:
* **DrissionPage:** A browser automation tool used here to handle dynamic JavaScript rendering and study anti-bot behaviors (e.g., lazy loading).
* **Google Gemini 1.5:** An AI model used to semantically understand HTML and normalize it into structured JSON (Schema Enforcement), eliminating the need for hardcoded CSS selectors.

🛠️ Features

* **stealth_mode**: Implements browser fingerprint randomization for research.
* **smart_wait**: Uses DOM-based waiting strategies instead of fixed timers.
* **ai_parsing**: Extracts "Title", "Price", and "Image" automatically without regex.
* **Privacy-First:** API keys are managed via environment variables and never logged.

⚙️ Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/Chaitya44/AIWebscrapper.git](https://github.com/Chaitya44/AIWebscrapper.git)
    cd AIWebscrapper
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Create a `.env` file in the root directory. **Do not share this file.**
    ```ini
    # Required for AI processing
    GEMINI_API_KEY=your_google_api_key_here
    
    # Optional: Local password for the UI
    APP_PASSWORD=admin
    ```

4.  Run the application:
    ```bash
    streamlit run app.py
    ```

## ⚠️ Legal Disclaimer & Ethical Use

**READ BEFORE USING:**

1.  **Educational Purpose Only:** This repository is strictly for educational and research purposes. It is designed to demonstrate how LLMs can parse HTML structures. It is **not** intended for large-scale data harvesting, commercial scraping, or copyright infringement.
2.  **No Liability:** The developer (Chaitya44) assumes no liability for how this tool is used. Any legal consequences arising from the use of this tool are the sole responsibility of the user.
3.  **Respect Terms of Service:** Users are strictly advised to review and adhere to the *Terms of Service* (ToS) and *Robots.txt* of any website they interact with.
4.  **No Commercial Use:** The code and any data derived from it must **not** be used for commercial purposes, resale, or competing products.
5.  **Rate Limiting:** This tool includes artificial delays (`time.sleep`) to prevent server overload. Users should not modify these safety mechanisms to aggressively target servers (DDoS behavior).


🛡️ License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

*Note: The MIT License grants permission for use, but does not override the Terms of Service of target websites. Use responsibly.*

**If you are a copyright holder or website administrator and wish to have specific scraping capabilities removed from this educational tool, please open an Issue.**
