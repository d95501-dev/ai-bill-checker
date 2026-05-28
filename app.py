import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# Secrets check
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key set nahi hai.")
    st.stop()

# Model initialize (Stable method)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill")
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this bill. Extract items (name, amount) and total.
        Return valid JSON: {"items": [{"name": "Item", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            response = model.generate_content([prompt, image])
            # Safely clean response
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            st.table(pd.DataFrame(data["items"]))
            st.metric("Total", f"₹{data['bill_total_written']}")
        except Exception as e:
            st.error(f"Error: {e}")
