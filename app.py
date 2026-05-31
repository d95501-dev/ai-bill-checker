import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

st.set_page_config(page_title="AI Bill Checker")

st.title("🧾 AI Bill Checker")

api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

# Available Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

uploaded_file = st.file_uploader(
    "Upload Bill",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill", use_container_width=True)

    if st.button("Analyze"):

        prompt = """
        Extract bill items and total amount.
        Return ONLY valid JSON.

        Example:
        {
          "items":[
            {
              "name":"Rice",
              "qty":"2",
              "rate":"50",
              "amount":"100"
            }
          ],
          "total":"100"
        }
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

            st.success("Analysis Complete ✅")
            st.json(data)

        except Exception as e:
            st.error(f"Analysis Error: {str(e)}")
