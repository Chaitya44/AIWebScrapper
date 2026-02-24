import streamlit as st
import pandas as pd
import json
import auth
import scraper
import ai_agent

# ============================================================
# STEALTH MODE: Aggressive CSS Override
# ============================================================
st.set_page_config(layout="wide", page_title="Nexus AI Scraper", page_icon="🛸")

# Inject Deep Dark Theme CSS
st.markdown("""
<style>
    /* Deep Space Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #0a0a0a 0%, #000000 100%);
    }
    
    /* Hide Streamlit Chrome */
    header, #MainMenu, footer {
        display: none !important;
    }
    
    /* Typography */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Terminal Status Log */
    .stStatusWidget {
        background-color: #000000 !important;
        border: 1px solid #00FF94 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #00FF94 !important;
    }
    
    /* Glassmorphism Data Panels & Expanders */
    .stExpander, div[data-testid="stDataFrame"], .result-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    /* Terminal Input Container */
    .stChatInputContainer {
        background-color: transparent !important;
        padding-bottom: 20px !important;
    }
    
    /* Terminal Input Bar */
    .stChatInputContainer textarea {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        color: #00FF94 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 4px !important; /* Sharp corners */
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important;
    }
    
    /* Send Button - Ghost Style */
    .stChatInputContainer button {
        background: transparent !important;
        color: #00FF94 !important;
        border: 1px solid #00FF94 !important;
        border-radius: 4px !important;
    }
    
    .stChatInputContainer button:hover {
        background: rgba(0, 255, 148, 0.1) !important;
        box-shadow: 0 0 8px rgba(0, 255, 148, 0.4) !important;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: rgba(0, 229, 255, 0.1) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* DataFrame Styling */
    .stDataFrame {
        border: none !important;
    }
    
    .stDataFrame thead tr th {
        background-color: #111 !important;
        color: #00E5FF !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stDataFrame tbody tr td {
        color: #CCC !important;
        font-family: 'JetBrains Mono', monospace !important;
        background-color: transparent !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: 1px solid #333;
        color: #666;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 229, 255, 0.1) !important;
        border-color: #00E5FF !important;
        color: #00E5FF !important;
    }
    
    /* Download Buttons */
    .stDownloadButton button {
        background: transparent !important;
        color: #FF0055 !important;
        border: 1px solid #FF0055 !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton button:hover {
        background: rgba(255, 0, 85, 0.1) !important;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.4) !important;
    }
    
    h1, h2, h3 {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -1px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'extraction_results' not in st.session_state:
    st.session_state.extraction_results = {}

# ============================================================
# HELPER FUNCTIONS (Must be defined before use)
# ============================================================
def format_category_name(key: str) -> str:
    """Convert snake_case to Title Case with emoji."""
    name = key.replace("_", " ").title()
    emojis = {
        "profile": "👤", "artist": "🎤", "product": "📦", "song": "🎵",
        "album": "💿", "review": "⭐", "price": "💰", "related": "🔗",
        "tour": "🎫", "headline": "📰", "trending": "🔥", "item": "📋"
    }
    for word, emoji in emojis.items():
        if word in key.lower():
            return f"{emoji} {name}"
    return f"📋 {name}"

def render_category_card(key: str, value):
    """Render a single category as a styled card with filtering."""
    
    # FILTER: Skip empty lists
    if isinstance(value, list) and len(value) == 0:
        return

    # FILTER: Skip [object Object] artifacts in string values
    if isinstance(value, str) and "[object Object]" in value:
        return

    st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
    
    if isinstance(value, list) and len(value) > 0:
        # LIST DISPLAY
        st.markdown(f"### {format_category_name(key)}")
        st.caption(f"⚡ Found {len(value)} items")
        
        try:
            df = pd.DataFrame(value)
            
            # SANITIZATION: Filter out columns that might contain objects
            clean_df = df.astype(str) # Convert all to string to be safe
            
            # Smart column ordering
            priority_cols = ['name', 'title', 'product_name', 'track_name', 'headline',
                           'price', 'rating', 'date', 'description', 'link', 'url']
            ordered_cols = [c for c in priority_cols if c in df.columns]
            other_cols = [c for c in df.columns if c not in ordered_cols]
            df = df[ordered_cols + other_cols]
            
            st.dataframe(df, use_container_width=True, height=min(400, 50 + len(df) * 35))
            
            # Download button
            csv_data = df.to_csv(index=False)
            st.download_button(
                f"📥 Download CSV",
                csv_data,
                f"{key}.csv",
                "text/csv",
                key=f"download_{key}_{id(value)}"
            )
        except Exception as e:
            st.json(value)
    
    elif isinstance(value, dict):
        # SINGLE ENTITY DISPLAY
        st.markdown(f"### {format_category_name(key)}")
        for k, v in value.items():
            # FILTER: precise check
            if "[object Object]" in str(v):
                continue
                
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{k.replace('_', ' ').title()}**")
            with col2:
                if isinstance(v, str) and v.startswith("http"):
                    st.markdown(f"[{v[:60]}...]({v})" if len(v) > 60 else f"[{v}]({v})")
                else:
                    st.write(v)
        
        # JSON download
        st.download_button(
            f"📥 Download JSON",
            json.dumps(value, indent=2),
            f"{key}.json",
            "application/json",
            key=f"download_{key}_{id(value)}"
        )
    
    else:
        st.json(value)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_extraction_results(entities):
    """Render multi-entity extraction results with styled cards."""
    
    if len(entities) == 1:
        # Single category - render directly
        key, value = list(entities.items())[0]
        render_category_card(key, value)
    else:
        # Multiple categories - use tabs
        tab_names = [format_category_name(k) for k in entities.keys()]
        tabs = st.tabs(tab_names)
        
        for tab, (key, value) in zip(tabs, entities.items()):
            with tab:
                render_category_card(key, value)

# ============================================================
# AUTHENTICATION
# ============================================================
if not auth.check_password():
    st.stop()

# ============================================================
# HEADER
# ============================================================
import time

st.markdown("""
<div style='text-align: center; padding: 40px 0 20px 0;'>
    <h1 style='color: white; font-size: 56px; font-weight: 800; margin: 0; text-shadow: 0 0 20px rgba(0,255,148,0.3);'>
        NEXUS <span style='color: #00FF94'>TERMINAL</span>
    </h1>
    <p style='color: #8B8D98; font-family: "JetBrains Mono"; font-size: 14px; margin-top: 10px; letter-spacing: 2px;'>
        >> INITIALIZING NEURAL EXTRACTION PROTOCOL_
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display extraction results if available
        if message["role"] == "assistant" and "extraction_id" in message:
            extraction_id = message["extraction_id"]
            if extraction_id in st.session_state.extraction_results:
                render_extraction_results(st.session_state.extraction_results[extraction_id])

# ============================================================
# CHAT INPUT
# ============================================================
if prompt := st.chat_input("█ Enter Target URL..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process extraction
    with st.chat_message("assistant"):
        start_time = time.time()
        with st.status(">> ESTABLISHING CONNECTION...", expanded=True) as status:
            st.write(">> initializing_headless_driver...")
            html = scraper.get_website_content(prompt)
            
            if not html:
                error_msg = "❌ Failed to load the page. The site might be blocking bots."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.stop()
            
            st.write(f">> analyzing_payload: {len(html):,} bytes...")
            entities = ai_agent.extract_multi_entity(html)
            
            if not entities:
                warning_msg = "⚠️ No structured data found on this page."
                st.warning(warning_msg)
                st.session_state.messages.append({"role": "assistant", "content": warning_msg})
                st.stop()
            
            # Count items
            total_items = sum(len(v) if isinstance(v, list) else 1 for v in entities.values())
            
            elapsed = time.time() - start_time
            speed_badge = "⚡ FAST SCRAPE" if elapsed < 12 else f"⏱️ {elapsed:.1f}s"
            
            status.update(
                label=f"✅ EXTRACTION COMPLETE [{speed_badge}]",
                state="complete"
            )
        
        # Create response message
        response_msg = f"**>> SCAN COMPLETE** | Found **{len(entities)} categories** | **{total_items} items** | {speed_badge}"
        st.markdown(response_msg)
        
        # Store results
        extraction_id = len(st.session_state.extraction_results)
        st.session_state.extraction_results[extraction_id] = entities
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_msg,
            "extraction_id": extraction_id
        })
        
        # Render results
        render_extraction_results(entities)
