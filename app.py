import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="AI Bill Checker", layout="centered")
st.title("🧾 AI Bill Checker")

# 2. Securely Configure API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API Key not found in Streamlit Secrets. Please add it.")
    st.stop()

# 3. Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Upload and Analyze
uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # FIX: 'width=None' hata diya hai, isse error fix ho jayega
    st.image(image, caption="Uploaded Bill") 
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing...")
        prompt = """Analyze this bill. Extract items (name, amount) and the total. 
        Return ONLY valid JSON format:
        {"items": [{"name": "Item Name", "amount": 0}], "bill_total_written": 0}"""
        
        try:
            response = model.generate_content([prompt, image])
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            # Result Display
            st.subheader("📋 Bill Items")
            df = pd.DataFrame(data["items"])
            st.table(df)
            
            st.subheader("💰 Total Summary")
            st.metric("Total Written on Bill", f"₹{data['bill_total_written']}")
            
        except Exception as e:
            st.error(f"Processing Error: {e}")
