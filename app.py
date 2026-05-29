import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="AI Bill Checker")

st.title("🧾 AI Bill Checker")

# Streamlit Secrets se key load karna
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# FIX: Yahan hum client ke andar direct API Key pass kar rahe hain
# Isse 401 ACCESS_TOKEN_TYPE_UNSUPPORTED error bilkul bypass ho jayega
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    api_key=api_key
)

# Upload
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
        with st.spinner("Analyzing Bill..."):
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
                response = model.generate_content(
                    [prompt, image]
                )
                text = response.text

                # Remove markdown
                text = text.replace("```json", "")
                text = text.replace("```", "")

                data = json.loads(text)
                st.success("Analysis Complete ✅")
                st.json(data)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("Gemini API quota exceeded. Try later.")
                elif "404" in error_msg:
                    st.error("Model not found.")
                else:
                    st.error(f"Analysis Error: {error_msg}")
