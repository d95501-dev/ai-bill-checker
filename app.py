import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

st.set_page_config(page_title="AI Bill Checker")
st.title("🧾 AI Bill Checker")

# API Key check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key missing in secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image)
    
    if st.button("Analyze"):
        try:
            # Response lena
            response = model.generate_content(["Extract items and total as JSON", image])
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
