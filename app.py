import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import subprocess
import os

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(
    page_title="AI Bill Checker Pro",
    layout="wide"
)

st.title("🧾 AI Bill Checker Pro")

# -----------------------------
# GEMINI API
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("❌ Gemini API Key not found")
    st.stop()

# -----------------------------
# FUNCTIONS
# -----------------------------
def analyze_bill(image):
    prompt = """
    Extract bill details and return ONLY valid JSON.

    Format:
    {
      "items":[
        {
          "name":"",
          "qty":"",
          "rate":"",
          "amount":""
        }
      ],
      "total":""
    }
    """

    response = model.generate_content([prompt, image])

    text = response.text
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)


def show_results(data):
    st.subheader("📋 Bill Items")

    df = pd.DataFrame(data.get("items", []))
    st.dataframe(df, use_container_width=True)

    total = data.get("total", 0)
    st.metric("💰 Total Amount", f"₹ {total}")


# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(
    ["📤 Upload Bill", "📠 Scanner Scan"]
)

# ==================================================
# UPLOAD BILL
# ==================================================
with tab1:

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

        if st.button("🔍 Analyze Uploaded Bill"):

            with st.spinner("Analyzing Bill..."):

                try:
                    data = analyze_bill(image)
                    show_results(data)

                except Exception as e:
                    st.error(str(e))


# ==================================================
# SCANNER TAB
# ==================================================
with tab2:

    st.subheader("📠 Brother Scanner")

    dpi = st.selectbox(
        "Select DPI",
        [100, 200, 300, 600],
        index=2
    )

    if st.button("🚀 Trigger Flatbed Scan"):

        with st.spinner("Scanning Document..."):

            output_file = "scan.jpg"

            cmd = [
                r"C:\Program Files\NAPS2\NAPS2.Console.exe",
                "--driver", "wia",
                "--device", "Brother DCP-T820DW",
                "--source", "glass",
                "--dpi", str(dpi),
                "-o", output_file,
                "-f"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if os.path.exists(output_file):

                st.success("✅ Scan Complete")

                image = Image.open(output_file)

                st.image(
                    image,
                    caption="Scanned Bill",
                    use_container_width=True
                )

                # AUTO ANALYZE
                with st.spinner("Analyzing Bill..."):

                    try:
                        data = analyze_bill(image)
                        show_results(data)

                    except Exception as e:
                        st.error(str(e))

            else:

                st.error("Scanner Error")
                st.code(result.stderr)
