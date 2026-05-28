import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.title("🧾 AI Bill Checker")

# API Key Secrets se lein
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image)
    if st.button("Analyze"):
        response = model.generate_content(["Extract items and total as JSON", image])
        st.write(response.text)
