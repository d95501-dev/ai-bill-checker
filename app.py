import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# Page Configuration
st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# API Key Config - 'st.secrets' ka istemal (Cloud ke liye zaroori)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key missing! Check Secrets in App Settings.")
    st.stop()

# Model Initializer - 'gemini-1.5-flash' stable version
model = genai.GenerativeModel('gemini-1.5-flash')

# File Uploader
uploaded_file = st.file_uploader("Upload Dairy Bill", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = "Analyze this dairy bill. Extract all items and return in JSON format: {'items': [{'name': '', 'amount': 0}], 'bill_total_written': 0}"
        
        try:
            response = model.generate_content([prompt, image])
            data = json.loads(response.text.replace("```json", "").replace("```", "").strip())
            
            st.subheader("Extracted Details")
            st.json(data)
        except Exception as e:
            st.error(f"Processing Error: {e}")
            st.error(f"AI Processing Error: {e}")
