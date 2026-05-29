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

# Purani library ke liye global configuration ka sabse stable tarika
genai.configure(api_key=api_key)

# Stable model call
model = genai.GenerativeModel("gemini-1.5-flash")

# Upload Box
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
                # Purani library me content pass karne ka standard tareeqa bina kisi extra argument ke
                response = model.generate_content([prompt, image])
                text = response.text

                # Markdown clean up
                text = text.replace("```json", "")
                text = text.replace("```", "")

                data = json.loads(text)
                st.success("Analysis Complete ✅")
                st.json(data)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("Gemini API quota exceeded. Try later.")
                elif "401" in error_msg or "400" in error_msg:
                    st.error("API Key Authentication Failed. Re-check your key inside Manage App -> Secrets.")
                else:
                    st.error(f"Analysis Error: {error_msg}")

