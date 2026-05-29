import streamlit as st
from google import genai
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

# Naya Official Client initialization - Ye bina error ke key handle karega
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Client Init Error: {e}")
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
                # Naye library ka content generation method
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[prompt, image]
                )
                
                text = response.text

                # Markdown format clean karna agar AI add kare toh
                text = text.replace("```json", "")
                text = text.replace("```", "")

                data = json.loads(text)
                st.success("Analysis Complete ✅")
                st.json(data)

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("Gemini API quota exceeded. Try later.")
                elif "400" in error_msg:
                    st.error("API Key issue or Invalid Request. Check your key in Secrets.")
                else:
                    st.error(f"Analysis Error: {error_msg}")
