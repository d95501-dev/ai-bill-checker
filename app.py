import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import os
import platform

IS_LOCAL = (
    platform.system() == "Windows"
    and os.path.exists(r"C:\Program Files\NAPS2\NAPS2.Console.exe")
)

st.set_page_config(page_title="Deep CSC - AI Bill Processor", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("API Key missing!")
    st.stop()

def analyze_bill(image):
    prompt = """
    You are a strict JSON extractor. Read the bill image and return ONLY valid JSON.
    Fields (use null when missing):
    - vendor_name
    - date
    - items: array of {name, qty, rate, amount}
    - total
    Return ONLY JSON. No markdown, no explanation, no backticks.
    """
    try:
        response = model.generate_content([prompt, image])
        if not response or not getattr(response, "text", None):
            st.error("AI returned empty response.")
            return None

        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        st.error(f"AI error: {e}")
        return None

def show_results(data):
    if not data:
        st.error("AI से डेटा प्राप्त नहीं हो सका।")
        return

    st.subheader("📋 Bill Details")

    vendor = data.get("vendor_name") or "Unknown Vendor"
    date = data.get("date") or "Unknown Date"

    st.write(f"🏪 Vendor: {vendor}")
    st.write(f"🗓️ Invoice Date: {date}")

    items = data.get("items") or []
    if isinstance(items, list) and items:
        cleaned = []
        for it in items:
            if isinstance(it, dict):
                cleaned.append({
                    "name": it.get("name") or "",
                    "qty": it.get("qty") or "",
                    "rate": it.get("rate") or "",
                    "amount": it.get("amount") or ""
                })
        if cleaned:
            st.dataframe(pd.DataFrame(cleaned), use_container_width=True)
    else:
        st.info("No items detected.")

    total = data.get("total") or "0"
    st.metric("💰 Total Amount", f"₹ {total}")

    with st.expander("Raw JSON (debug)"):
        st.json(data)

st.title("🧾 Deep CSC - AI Bill Processor")

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
                show_results(data)
