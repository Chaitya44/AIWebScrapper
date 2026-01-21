# FILE: ai_agent.py
import os
import re
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


def get_ai_client():
    if not API_KEY:
        raise ValueError("❌ API Key not found! Check your .env file.")
    return genai.Client(api_key=API_KEY)


def extract_with_intent(raw_text, mode):
    print(f"🧠 AI switching to mode: {mode}")
    client = get_ai_client()

    if "E-Commerce" in mode:
        system_instruction = "You are an E-Commerce Scraping Bot. Extract Product Title, Price, Rating, Availability."
    elif "Lead Generation" in mode:
        system_instruction = "You are a Sales Lead Researcher. Extract Name, Job Title, Email, Phone."
    elif "News" in mode:
        system_instruction = "You are a News Aggregator. Extract Headline, Author, Date, Summary."
    elif "Real Estate" in mode:
        system_instruction = "You are a Real Estate Analyst. Extract Property Title, Price, Location, Specs."
    else:
        system_instruction = "You are a General Data Extractor. Identify lists and tables."

    prompt = f"""
    {system_instruction}
    INSTRUCTIONS: Extract matching items into a JSON Array. Return ONLY valid JSON.
    Raw Text: {raw_text[:15000]}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.text.strip().replace("```json", "").replace("```", "")
    except Exception as e:
        print(f"AI Error: {e}")
        return "[]"