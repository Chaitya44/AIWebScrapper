import streamlit as st
import os
from dotenv import load_dotenv


def check_password():
    """
    Simple, robust login check using native Streamlit UI.
    """
    load_dotenv()
    SECRET_PASSWORD = os.getenv("APP_PASSWORD")

    # Initialize Session State
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # If already logged in, return True
    if st.session_state.authenticated:
        return True

    # --- NATIVE LOGIN UI ---
    st.title("🔐 Login Required")

    with st.form("login_form"):
        password = st.text_input("Enter Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if password == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password")

    return False