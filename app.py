import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.title("🧾 AI Bill Checker")

# API Key
api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

# Updated Model
model = genai.GenerativeModel("gemini-2.0-flash")

uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image)

    if st.button("Analyze"):

        prompt = """
        Extract all bill items and total.

        Return ONLY JSON.
        """

        try:

            response = model.generate_content(
                [prompt, image]
            )

            text = response.text

            text = text.replace("```json", "")
            text = text.replace("```", "")

            data = json.loads(text)

            st.json(data)

        except Exception as e:

            st.error(f"Analysis Error: {e}")
