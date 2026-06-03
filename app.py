import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import subprocess
import os

# Page Setup
st.set_page_config(page_title="Professional AI Bill Checker", layout="wide")

st.title("📠 Professional AI Bill Checker")

# API Configuration
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("API Key not set in secrets.")
    st.stop()

# Layout: Two columns for Scanner and Analysis
col1, col2 = st.columns([1, 1])

output_file = "scan.jpg"

with col1:
    st.subheader("1. Scan Process")
    if st.button("🚀 Trigger Flatbed Scan"):
        with st.spinner("Scanner working..."):
            cmd = [
                r"C:\Program Files\NAPS2\NAPS2.Console.exe",
                "--driver", "wia",
                "--device", "Brother DCP-T820DW",
                "--source", "glass",
                "--dpi", "300",
                "-o", output_file,
                "-f"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(output_file):
                st.success("✅ Scan Complete")
            else:
                st.error(f"Scan failed: {result.stderr}")

    if os.path.exists(output_file):
        img = Image.open(output_file)
        st.image(img, caption="Scanned Bill", use_container_width=True)

with col2:
    st.subheader("2. AI Analysis")
    if st.button("🔍 Analyze Scanned Bill"):
        if not os.path.exists(output_file):
            st.warning("Please perform a scan first!")
        else:
            with st.spinner("AI is analyzing..."):
                try:
                    img = Image.open(output_file)
                    prompt = "Extract items (name, qty, rate, amount) and total from this bill. Return JSON only."
                    response = model.generate_content([prompt, img])
                    
                    text = response.text.replace("```json", "").replace("```", "")
                    data = json.loads(text)
                    
                    df = pd.DataFrame(data.get("items", []))
                    st.subheader("📋 Bill Items")
                    st.dataframe(df, use_container_width=True)
                    
                    total = data.get("total", 0)
                    st.metric("Total Amount", f"₹{total}")
                except Exception as e:
                    st.error(f"Error processing bill: {e}")

# Optional: File Uploader for backup
st.divider()
uploaded_file = st.file_uploader("Or Upload Bill Image Manually", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.image(uploaded_file, use_container_width=True)
