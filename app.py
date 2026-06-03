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
# यह चेक करेगा कि क्या हम Windows पर हैं और NAPS2 मौजूद है
IS_LOCAL = (
    platform.system() == "Windows"
    and os.path.exists(r"C:\Program Files\NAPS2\NAPS2.Console.exe")
)

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="AI Bill Checker Pro", layout="wide")
st.title("🧾 AI Bill Checker Pro")

# -----------------------------
# GEMINI API
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("❌ Gemini API Key not found")
    st.stop()

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
    total = data.get("total", 0)
    st.metric("💰 Total Amount", f"₹ {total}")

# -----------------------------
# TABS & UI LOGIC
# -----------------------------
if IS_LOCAL:
    tab1, tab2 = st.tabs(["📤 Upload Bill", "📠 Scanner Scan"])
else:
    tab1 = st.container()

# ==================================================
# TAB 1: UPLOAD BILL
# ==================================================
with tab1:
    uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Bill", use_container_width=True)
        if st.button("🔍 Analyze Uploaded Bill"):
            with st.spinner("Analyzing..."):
                try:
                    data = analyze_bill(image)
                    show_results(data)
                except Exception as e:
                    st.error(f"Error: {e}")

# ==================================================
# TAB 2: SCANNER (LOCAL ONLY)
# ==================================================
if IS_LOCAL:
    with tab2:
        st.subheader("📠 Brother Scanner")
        dpi = st.selectbox("Select DPI", [100, 200, 300, 600], index=2)

        if st.button("🚀 Trigger Flatbed Scan"):
            output_file = os.path.abspath("scan.jpg")
            if os.path.exists(output_file):
                os.remove(output_file)

            cmd = [
                r"C:\Program Files\NAPS2\NAPS2.Console.exe",
                "--driver", "wia",
                "--device", "Brother DCP-T820DW",
                "--source", "glass",
                "--dpi", str(dpi),
                "-o", output_file,
                "-f"
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if os.path.exists(output_file):
                    st.success("✅ Scan Complete")
                    image = Image.open(output_file)
                    st.image(image, use_container_width=True)
                    data = analyze_bill(image)
                    show_results(data)
                else:
                    st.error("Scanner Error")
                    st.code(result.stderr)
            except Exception as e:
                st.error(str(e))

# ==================================================
# CLOUD FALLBACK: CAMERA
# ==================================================
if not IS_LOCAL:
    st.divider()
    st.info("📷 Scanner hardware is local only. Use camera or upload below.")
    camera_file = st.camera_input("Take Bill Photo")
    if camera_file:
        image = Image.open(camera_file)
        if st.button("🔍 Analyze Camera Bill"):
            with st.spinner("Analyzing..."):
                data = analyze_bill(image)
                show_results(data)
