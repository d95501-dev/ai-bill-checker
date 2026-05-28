import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# 2. Configure API Key securely
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API Key not found! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# 3. Initialize Model
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. File Upload
uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this dairy bill. Extract all items and return in JSON format: 
        {"items": [{"name": "Item Name", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            response = model.generate_content([prompt, image])
            # Clean output
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_text)
            st.json(data)
        except Exception as e:
            st.error(f"Processing Error: {e}")
