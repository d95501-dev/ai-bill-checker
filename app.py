import streamlit as st
import streamlit as st
# ... बाकी imports ...

# Professional Dashboard Styling
st.markdown("""
    <style>
    /* खाली बॉक्स को प्रोफेशनल कार्ड में बदलना */
    .dashboard-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #4b6eff;
        color: white;
        margin-bottom: 20px;
    }
    /* हेडर और टेक्स्ट का स्टाइल */
    .stApp { background-color: #0e1117; }
    </style>
""", unsafe_allow_html=True)

# खाली बॉक्स की जगह यह कोड लिखें
st.markdown("""
    <div class="dashboard-card">
        <h3>🖥️ Deep CSC - Hardware Connectivity Bridge</h3>
        <p>सिस्टम तैयार है। कृपया अपना कार्य करने के लिए 'Scanner' या 'Printer' मोड चुनें।</p>
    </div>
""", unsafe_allow_html=True)
import google.generativeai as genai
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import re

st.set_page_config(page_title="AI Bill Checker", page_icon="🧾", layout="wide")

# डैशबोर्ड स्टाइलिंग के लिए CSS
st.markdown("""
    <style>
    .welcome-card {
        background-color: #1e1e2f;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #4b6eff;
        margin-bottom: 20px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧾 AI Bill Checker")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Model Error: {e}")
    st.stop()

# --- डैशबोर्ड का खाली बॉक्स हिस्सा ---
if "uploaded_file" not in locals() or uploaded_file is None:
    st.markdown("""
        <div class="welcome-card">
            <h3>Welcome to Deep CSC</h3>
            <p>कृपया एक बिल इमेज अपलोड करें ताकि AI उसका विश्लेषण कर सके।</p>
        </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    if st.button("🔍 Analyze Bill"):
        with st.spinner("Analyzing Bill..."):
            prompt = """
            Read the bill carefully. Extract all bill items and total amount.
            Return ONLY valid JSON format:
            {"items":[{"name":"Item","qty":"0","rate":"0","amount":"0"}], "total":"0"}
            """
            try:
                response = model.generate_content([prompt, image])
                text = response.text.strip().replace("```json", "").replace("```", "")
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match: text = match.group(0)
                
                data = json.loads(text)
                st.success("✅ Analysis Complete")

                items = data.get("items", [])
                if not items:
                    st.warning("No bill items found.")
                    st.stop()

                df = pd.DataFrame(items)
                st.subheader("📋 Bill Items")
                st.dataframe(df, use_container_width=True, hide_index=True)

                if "amount" in df.columns:
                    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

                calculated_total = float(df["amount"].sum())
                bill_total = float(data.get("total", 0))

                c1, c2 = st.columns(2)
                with c1: st.metric("💰 Calculated Total", f"₹{calculated_total:,.2f}")
                with c2: st.metric("🧾 Bill Total", f"₹{bill_total:,.2f}")

                diff = abs(calculated_total - bill_total)
                if diff < 1: st.success("✅ Bill Total Matched")
                else: st.error(f"❌ Bill Mismatch (Difference ₹{diff:,.2f})")

                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Bill Items")

                st.download_button("📥 Download Excel", data=excel_buffer.getvalue(), 
                                   file_name="bill_report.xlsx", 
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Analysis Error: {e}")
