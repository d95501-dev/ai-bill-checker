import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import re

st.set_page_config(page_title="AI Bill Checker", page_icon="🧾", layout="wide")

st.title("🧾 AI Bill Checker")

# API Configuration
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error("API Key not found or Config error.")
    st.stop()

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    if st.button("🔍 Analyze Bill"):
        with st.spinner("Analyzing..."):
            prompt = "Extract items (name, qty, rate, amount) and total from this bill. Return JSON only."
            try:
                response = model.generate_content([prompt, image])
                text = response.text.replace("```json", "").replace("```", "")
                data = json.loads(text)
                
                df = pd.DataFrame(data.get("items", []))
                st.subheader("📋 Bill Items")
                st.dataframe(df, use_container_width=True)
                
                total = data.get("total", 0)
                st.metric("Total Amount", f"₹{total}")
                
            except Exception as e:
                st.error("Error: Could not process the bill.")
