import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="AI Bill Checker")
st.title("🧾 AI Bill Checker")

# Configure API Key securely
try:
    # Ensure GEMINI_API_KEY is set in Streamlit Cloud Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key not found in Secrets.")
    st.stop()

# Initialize the model explicitly
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill")
    
    if st.button("Analyze"):
        try:
            # Using the established model object
            response = model.generate_content(["Extract items and total as JSON", image])
            st.write(response.text)
        except Exception as e:
            st.error(f"Analysis Error: {e}")
