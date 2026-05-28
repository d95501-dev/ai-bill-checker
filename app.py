import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

st.set_page_config(page_title="AI Bill Checker Pro", layout="centered")
st.title("🧾 AI Bill Checker")

# API Key - SECURE RAKHEIN (App settings mein add karein)
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key missing! Settings > Secrets mein GEMINI_API_KEY add karein.")
    st.stop()

genai.configure(api_key=api_key)

# STABLE MODEL NAME
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Choose Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill")
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this dairy bill. Extract items and total.
        Return ONLY JSON: {"items": [{"name": "Item", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            response = model.generate_content([prompt, image])
            data = json.loads(response.text.replace("```json", "").replace("```", "").strip())
            
            st.json(data) # Yahan se aap result dekh sakte hain
            st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"Error: {e}")
