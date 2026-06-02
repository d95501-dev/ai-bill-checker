import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import re

st.set_page_config(page_title="AI Bill Checker", page_icon="🧾", layout="wide")

st.title("🧾 AI Bill Checker")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# बिल अपलोड करने का सेक्शन
uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    if st.button("🔍 Analyze Bill"):
        with st.spinner("Analyzing Bill..."):
            prompt = "Read the bill, extract items and total as JSON. Format: {'items':[{'name':'','qty':'','rate':'','amount':''}], 'total':''}"
            try:
                response = model.generate_content([prompt, image])
                text = response.text.strip().replace("```json", "").replace("```", "")
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match: text = match.group(0)
                data = json.loads(text)
                
                st.success("✅ Analysis Complete")
                df = pd.DataFrame(data.get("items", []))
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Total display
                total = float(data.get("total", 0))
                st.metric("🧾 Bill Total", f"₹{total:,.2f}")
            except Exception as e:
                st.error(f"Analysis Error: {e}")
