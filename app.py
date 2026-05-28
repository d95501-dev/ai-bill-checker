import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="AI Bill Checker")

st.title("🧾 AI Bill Checker")

# Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]

# Gemini Configure
genai.configure(api_key=api_key)

# Model
model = genai.GenerativeModel("gemini-1.5-flash")

# Upload Image
uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    if st.button("Analyze Bill"):

        with st.spinner("Analyzing..."):

            prompt = """
            Extract all bill items and total amount.

            Return ONLY valid JSON.

            Format:
            {
              "items": [
                {
                  "name": "",
                  "qty": "",
                  "rate": "",
                  "amount": ""
                }
              ],
              "total": ""
            }
            """

            try:

                response = model.generate_content(
                    [prompt, image]
                )

                result = response.text

                # Remove markdown formatting
                result = result.replace("```json", "")
                result = result.replace("```", "")

                data = json.loads(result)

                st.success("Bill Analyzed Successfully ✅")

                st.json(data)

            except Exception as e:

                st.error("Error while analyzing bill ❌")

                st.exception(e)
