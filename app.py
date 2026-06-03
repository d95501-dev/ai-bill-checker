import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
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
    You are a strict JSON extractor. Read the bill image and return ONLY valid JSON.
    Fields (use null when missing):
    - vendor_name (string or null)
    - date (string or null)
    - items: array of {name, qty, rate, amount} (or empty array)
    - total (number or string or null)

    Return ONLY JSON. No markdown, no explanation, no backticks.
    """
    try:
        response = model.generate_content([prompt, image])

        # सुरक्षित चेक — response या response.text None हो सकता है
        if not response or not getattr(response, "text", None):
            st.error("AI returned empty response.")  # debug message
            return None

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as je:
            st.error(f"JSON parse error: {je}")
            # debugging के लिए raw output दिखाएं
            st.code(raw)
            return None

        return data
    except Exception as e:
        st.error(f"AI error: {e}")
        return None

def show_results(data):
    if not data:
        st.error("AI से डेटा प्राप्त नहीं हो सका।")
        return

    st.subheader("📋 Bill Details")

    # None-safe extraction: अगर key missing या None है तो fallback
    vendor = data.get("vendor_name") or "Unknown Vendor"
    vendor = str(vendor)  # अगर uppercase लगता है तो: str(vendor).upper()

    date = data.get("date") or "Unknown Date"
    date = str(date)

    st.write(f"🏪 Vendor: {vendor}")
    st.write(f"🗓️ Invoice Date: {date}")

    items = data.get("items") or []
    if isinstance(items, list) and items:
        # validate items entries to avoid unexpected None values
        cleaned = []
        for it in items:
            if not isinstance(it, dict):
                continue
            name = it.get("name") or ""
            qty = it.get("qty") or ""
            rate = it.get("rate") or ""
            amount = it.get("amount") or ""
            cleaned.append({"name": name, "qty": qty, "rate": rate, "amount": amount})
        df = pd.DataFrame(cleaned)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No items detected.")

    total = data.get("total")
    if total is None:
        total_display = "0"
    else:
        total_display = str(total)
    st.metric("💰 Total Amount", f"₹ {total_display}")

    # Debug: raw JSON inspector (temporary, helpful to trace None fields)
    with st.expander("Raw JSON (debug)"):
        st.json(data)

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
        st.image(image, caption="Uploaded Bill", use_column_width=True)

        if st.button("🔍 Analyze Bill"):
            with st.spinner("Analyzing..."):
                data = analyze_bill(image)
                try:
                    show_results(data)
                except Exception as e:
                    # extra safety so UI पर technical traceback न टूटे, पर debugging info मिले
                    st.error(f"Structural Parsing Fault: {e}")
