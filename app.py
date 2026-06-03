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

# -----------------------------
# API CONFIG
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("API Key not found!")
    st.stop()

# -----------------------------
# FUNCTIONS
# -----------------------------
def analyze_bill(image):
    # Prompt को और सरल रखा है ताकि AI ज्यादा कंफ्यूज न हो
    prompt = "Extract items (name, qty, rate, amount) and total from this bill. Return ONLY JSON."
    try:
        response = model.generate_content([prompt, image])
        if response and response.text:
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        return None
    except Exception as e:
        return None # एरर आने पर चुपचाप None भेजें, ऐप क्रैश न करें

def show_results(data):
    # सबसे महत्वपूर्ण सुधार: डेटा चेक करना
    if data is None or not isinstance(data, dict):
        st.error("AI से डेटा प्राप्त करने में समस्या हुई। कृपया दोबारा कोशिश करें।")
        return
        
    st.subheader("📋 Bill Items")
    items = data.get("items", [])
    if items:
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True)
    
    total = data.get("total", "0")
    st.metric("💰 Total Amount", f"₹ {total}")

# -----------------------------
# UI LOGIC
# -----------------------------
st.title("🧾 Deep CSC - AI Bill Processor")

if IS_LOCAL:
    tab1, tab2 = st.tabs(["📤 Upload & Process", "📠 Scanner & Printer Console"])
else:
    tab1 = st.container()

with tab1:
    uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        if st.button("🔍 Analyze Uploaded Bill"):
            with st.spinner("Analyzing..."):
                result_data = analyze_bill(image)
                show_results(result_data)

if IS_LOCAL:
    with tab2:
        if st.button("🚀 Trigger Flatbed Scan"):
            output_file = os.path.abspath("scan.jpg")
            cmd = [r"C:\Program Files\NAPS2\NAPS2.Console.exe", "--driver", "wia", "--device", "Brother DCP-T820DW", "--source", "glass", "--dpi", "300", "-o", output_file, "-f"]
            try:
                subprocess.run(cmd, check=True)
                if os.path.exists(output_file):
                    img = Image.open(output_file)
                    st.image(img, use_container_width=True)
                    data = analyze_bill(img)
                    show_results(data)
            except Exception as e:
                st.error(f"Scanner error: {e}")
