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
# यह चेक करता है कि क्या यह Windows है और NAPS2 मौजूद है
IS_LOCAL = (
    platform.system() == "Windows"
    and os.path.exists(r"C:\Program Files\NAPS2\NAPS2.Console.exe")
)

# Page Config
st.set_page_config(page_title="Deep CSC - AI Bill Processor", layout="wide")

# -----------------------------
# API CONFIG
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except:
    st.error("API Key missing!")

# -----------------------------
# FUNCTIONS
# -----------------------------
def analyze_bill(image):
    prompt = "Extract items (name, qty, rate, amount) and total from this bill. Return JSON only."
    response = model.generate_content([prompt, image])
    text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def show_results(data):
    st.subheader("📋 Bill Items")
    df = pd.DataFrame(data.get("items", []))
    st.dataframe(df, use_container_width=True)
    st.metric("💰 Total Amount", f"₹ {data.get('total', 0)}")

# -----------------------------
# UI LOGIC
# -----------------------------
st.title("🧾 Deep CSC - AI Bill Processor")

if IS_LOCAL:
    tab1, tab2 = st.tabs(["📤 Upload & Process", "📠 Scanner & Printer Console"])
else:
    tab1 = st.container()
    st.info("🌐 Cloud Mode: Scanner hardware is not accessible here. Please upload files.")

# --- TAB 1: UPLOAD ---
with tab1:
    uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        if st.button("🔍 Analyze Uploaded Bill"):
            with st.spinner("Analyzing..."):
                data = analyze_bill(image)
                show_results(data)

# --- TAB 2: SCANNER (ONLY LOCAL) ---
if IS_LOCAL:
    with tab2:
        st.subheader("📠 Brother Scanner Controller")
        dpi = st.selectbox("Select DPI", [100, 200, 300, 600], index=2)
        
        if st.button("🚀 Trigger Flatbed Scan"):
            output_file = os.path.abspath("scan.jpg")
            if os.path.exists(output_file): os.remove(output_file)

            cmd = [
                r"C:\Program Files\NAPS2\NAPS2.Console.exe",
                "--driver", "wia",
                "--device", "Brother DCP-T820DW",
                "--source", "glass",
                "--dpi", str(dpi),
                "-o", output_file, "-f"
            ]
            
            with st.spinner("Scanning..."):
                try:
                    subprocess.run(cmd, check=True)
                    if os.path.exists(output_file):
                        st.success("✅ Scan Complete!")
                        img = Image.open(output_file)
                        st.image(img, use_container_width=True)
                        data = analyze_bill(img)
                        show_results(data)
                except Exception as e:
                    st.error(f"Scanner Error: {e}")
