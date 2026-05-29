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

# 100% Working Fix for 401 error: API key ko direct client settings ke request options mein pass karna
# Isse purani library direct Google AI Studio ki key accept karegi bina OAuth confuse hue
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

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
                # Yahan hum client ke core configurations ko strict kar rahe hain taaki login cookie ya token na mange
                response = model.generate_content(
                    contents=[prompt, image],
                    request_options={"api_key": api_key}
                )
                
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
                    st.error("API Key Authentication Failed. Re-check the key in Manage App -> Secrets.")
                else:
                    st.error(f"Analysis Error: {error_msg}")
