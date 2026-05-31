import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

uploaded_file = st.file_uploader(
    "Upload Bill",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    if st.button("Analyze"):

        prompt = """
        Extract bill items and total amount.
        Return ONLY JSON.
        """

        try:
            response = model.generate_content([prompt, image])

            text = response.text.strip()

            text = text.replace("```json", "")
            text = text.replace("```", "")

            match = re.search(r"\{.*\}", text, re.DOTALL)

            if match:
                text = match.group(0)

            data = json.loads(text)

            st.json(data)

        except Exception as e:
            st.error(str(e))
                    st.error(f"Analysis Error: {error_msg}")

