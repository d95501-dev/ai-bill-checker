import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# 1. Page Setup
st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# 2. Securely Load API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key not set in Secrets!")
    st.stop()

# 3. Model Configuration (Using stable google-generativeai SDK)
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. File Uploader
uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this dairy bill. Extract all items (date, name, qty, rate, amount) 
        and the total written amount. Return ONLY valid JSON in this format:
        {"items": [{"name": "Item", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            # Direct Model call with stable SDK
            response = model.generate_content([prompt, image])
            st.json(response.text) # Check raw output first
        except Exception as e:
            st.error(f"Error: {e}")
