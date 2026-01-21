# FILE: app.py
import streamlit as st
import pandas as pd
import json
import scraper
import ai_agent
import storage
import os
from dotenv import load_dotenv

# 1. Load the Vault
load_dotenv()

# 2. Page Config
st.set_page_config(page_title="Pro Web Scraper", page_icon="🕵️‍♀️", layout="wide")

SECRET_PASSWORD = os.getenv("APP_PASSWORD")

# Safety fallback: If no password is set in .env, block access
if not SECRET_PASSWORD:
    st.error("⚠️ Security Error: APP_PASSWORD is missing")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    password = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if password == SECRET_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password!")
    st.stop()



st.title("🕵️‍♀️ Pro Web Scraper")
st.markdown("##### *Select your goal, enter a link, and let AI do the rest.*")

with st.sidebar:
    st.header("⚙️ Settings")
    scrape_mode = st.selectbox(
        "🎯 Scraping Template:",
        [
            "🛒 E-Commerce (Products & Prices)",
            "👥 Lead Generation (Emails & Contacts)",
            "📰 News & Articles (Text & Dates)",
            "🏠 Real Estate (Properties & Locations)",
            "🧠 Universal / Auto-Detect"
        ]
    )
    if st.button("🗑️ Clear Database"):
        try:
            import os

            if os.path.exists("universal_scraper.db"):
                os.remove("universal_scraper.db")
                st.success("History cleared!")
        except:
            pass

url = st.text_input("Target Website URL:", placeholder="e.g., https://www.amazon.in/s?k=laptops")

if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
    if not url:
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("🕵️‍♀️ Accessing site & extracting data..."):
            # 1. Scrape
            raw_text = scraper.get_website_content(url)

            if raw_text:
                with st.expander("Show Raw Scraper Text (Debug)"):
                    st.write(raw_text[:1000])

                # 2. AI Extract
                json_result = ai_agent.extract_with_intent(raw_text, scrape_mode)

                # 3. Show Results
                try:
                    data_list = json.loads(json_result)
                    if data_list:
                        st.success(f"🎉 Found {len(data_list)} items!")
                        df = pd.DataFrame(data_list)
                        st.dataframe(df, use_container_width=True)
                        storage.save_dynamic_data(url, scrape_mode, json_result)
                    else:
                        st.warning("AI found no data.")
                except Exception as e:
                    st.error("Error parsing AI response.")
                    st.text(json_result)
            else:
                st.error("❌ Failed to access website.")