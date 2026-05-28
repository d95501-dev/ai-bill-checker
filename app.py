import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# 2. Securely Configure API Key
try:
    # This retrieves the key from the Secrets menu in your app settings
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API Key not found in Streamlit Secrets. Please add it.")
    st.stop()

# 3. Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Upload and Analyze
uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this bill. Extract items (name, amount) and the total. 
        Return ONLY JSON: {"items": [{"name": "Item", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            response = model.generate_content([prompt, image])
            # Remove markdown code blocks if the AI includes them
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            st.json(data)
        except Exception as e:
            st.error(f"Processing Error: {e}")
