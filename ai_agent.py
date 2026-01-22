import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY is missing from .env")

genai.configure(api_key=API_KEY)


# AUTO-SELECTOR (Kept from previous fix)
def get_working_model():
    try:
        my_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preference = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
        for model_name in preference:
            if model_name in my_models: return genai.GenerativeModel(model_name)
        if my_models: return genai.GenerativeModel(my_models[0])
    except:
        pass
    return genai.GenerativeModel('models/gemini-pro')


model = get_working_model()


def extract_with_intent(html_text):
    if len(html_text) > 300000:
        html_text = html_text[:300000]

    # --- THE FIX: STRICT SCHEMA INSTRUCTIONS ---
    prompt = f"""
    You are a Data Normalizer.

    TASK: Extract a list of items from the text.

    CRITICAL: You MUST normalize the JSON keys to these standard names:
    1. **"title"**: The main name (Song Name, House Address, Product Title).
    2. **"price"**: The cost or duration (e.g. "$500", "3:45").
    3. **"subtitle"**: The secondary info (Artist Name, Realtor Name, Description).
    4. **"link"**: The URL to the item.
    5. **"image"**: The image URL.
    6. **"details"**: Any other specific info (Beds, Stock Status) as a short string.

    RULES:
    - Output must be a PURE JSON List: `[ {{ "title": "...", "price": "..." }} ]`
    - Do not make up keys. Map the website's data to these 6 keys.

    CONTENT:
    {html_text}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Cleanup
        if text.startswith("```"): text = text.split("\n", 1)[-1]
        if text.endswith("```"): text = text.rsplit("\n", 1)[0]

        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return match.group(0)

        return "[]"

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "[]"