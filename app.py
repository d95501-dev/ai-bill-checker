import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import subprocess
import os
import platform

# -----------------------------
# ENVIRONMENT DETECTION
# -----------------------------
IS_LOCAL = (
    platform.system() == "Windows"
    and os.path.exists(r"C:\Program Files\NAPS2\NAPS2.Console.exe")
)

st.set_page_config(page_title="Deep CSC - AI Bill Processor", layout="wide")

# API Config
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("API Key missing!")
    st.stop()

def analyze_bill(image):
    # बहुत ही सख्त JSON प्रॉम्प्ट
    prompt = """
    Extract: vendor_name, date, items (name, qty, rate, amount), total.
    Return ONLY valid JSON. No extra text, no markdown.
    """
    try:
        response = model.generate_content([prompt, image])
        if response and response.text:
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        return None
    except Exception:
        return None

def show_results(data):
    if data is None:
        st.error("AI से डेटा प्राप्त नहीं हो सका।")
        return
        
    st.subheader("📋 Bill Details")
    
    # यहाँ सुरक्षा: अगर key मौजूद न हो तो 'Unknown' दिखाएं, .upper() न लगाएं
    vendor = data.get("vendor_name", "Unknown Vendor")
    date = data.get("date", "Unknown Date")
    
    st.write(f"🏪 Vendor: {vendor}")
    st.write(f"🗓️ Invoice Date: {date}")
    
    items = data.get("items", [])
    if items:
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True)
    
    total = data.get("total", "0")
    st.metric("💰 Total Amount", f"₹ {total}")

st.title("🧾 Deep CSC - AI Bill Processor")

# UI Logic
if IS_LOCAL:
    tab1, tab2 = st.tabs(["📤 Upload & Process", "📠 Scanner"])
else:
    tab1 = st.container()

with tab1:
    uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        if st.button("🔍 Analyze Bill"):
            with st.spinner("Analyzing..."):
                data = analyze_bill(image)
                show_results(data)
