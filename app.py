import streamlit as st
import pandas as pd
import json
import auth
import scraper
import ai_agent

st.set_page_config(layout="wide", page_title="Universal Scraper (Final)")

if not auth.check_password():
    st.stop()

st.title("🎓 Universal Scraper (Final Edition)")
st.caption("DrissionPage (Stealth) + Gemini (Schema Enforcer)")

url = st.text_input("Target URL", placeholder="https://...")
start = st.button("🚀 Run Scraper", type="primary")

if start and url:
    st.info("1. Launching Stealth Browser...")
    html = scraper.get_website_content(url)

    if html:
        st.info(f"2. Analyzing {len(html)} chars with AI...")
        json_str = ai_agent.extract_with_intent(html)

        try:
            data = json.loads(json_str)
            if data:
                st.success(f"✅ Found {len(data)} items!")

                # --- VISUAL CLEANUP ---
                df = pd.DataFrame(data)

                # Reorder columns to put "Title" first
                cols = ['title', 'price', 'subtitle', 'link', 'image', 'details']
                # Only keep columns that actually exist in the data
                existing_cols = [c for c in cols if c in df.columns]
                df = df[existing_cols]

                # Configure the Table for Pretty Display
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "title": st.column_config.TextColumn("Item Name", width="medium"),
                        "price": st.column_config.TextColumn("Price/Value", width="small"),
                        "image": st.column_config.ImageColumn("Preview"),
                        "link": st.column_config.LinkColumn("Link"),
                    },
                    height=600
                )

                st.download_button("📥 Download CSV", df.to_csv(index=False), "scraped_data.csv")
            else:
                st.warning("AI found no data. The page might be empty (blocked).")
        except:
            st.error("Failed to parse JSON.")
            with st.expander("Debug Raw Output"):
                st.text(json_str)
    else:
        st.error("Browser failed to load page.")