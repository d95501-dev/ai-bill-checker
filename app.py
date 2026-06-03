import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import subprocess
import os
import platform

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
    prompt = "Extract items (name, qty, rate, amount), total, and vendor_name from this bill. Return ONLY JSON."
    try:
        response = model.generate_content([prompt, image])
        if not response or not response.text:
            return None
        
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        # यहाँ AI का Raw output कैप्चर करें ताकि पता चले क्या गलती है
        st.error(f"Error: {e}")
        return None

def show_results(data):
    if not data:
        st.error("No valid JSON data received from AI.")
        return
        
    st.subheader("📋 Bill Items")
    
    # 1. Vendor display (बिना .upper() के)
    vendor = data.get("vendor_name", "Unknown Vendor")
    st.write(f"🏪 Vendor: {vendor}")
    
    # 2. DataFrame display
    items = data.get("items", [])
    if items:
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True)
    
    # 3. Total display
    total = data.get("total", "0")
    st.metric("💰 Total Amount", f"₹ {total}")

st.title("🧾 Deep CSC - AI Bill Processor")

if IS_LOCAL:
    tab1, tab2 = st.tabs(["📤 Upload & Process", "📠 Scanner & Printer Console"])
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
