import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import re

st.set_page_config(
page_title="AI Bill Checker",
page_icon="🧾",
layout="wide"
)

st.title("🧾 AI Bill Checker")

# Load API Key

try:
api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
st.error("GEMINI_API_KEY not found in Streamlit Secrets.")
st.stop()

# Configure Gemini

genai.configure(api_key=api_key)

try:
model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
st.error(f"Model Error: {e}")
st.stop()

# Upload Image

uploaded_file = st.file_uploader(
"Upload Bill Image",
type=["jpg", "jpeg", "png"]
)

if uploaded_file:

````
image = Image.open(uploaded_file)

st.image(
    image,
    caption="Uploaded Bill",
    use_container_width=True
)

if st.button("🔍 Analyze Bill"):

    with st.spinner("Analyzing bill..."):

        prompt = """
        Read this bill carefully.

        Extract all bill items and total amount.

        Return ONLY valid JSON.

        Example:

        {
          "items":[
            {
              "name":"Milk",
              "qty":"2",
              "rate":"58",
              "amount":"116"
            }
          ],
          "total":"116"
        }
        """

        try:

            response = model.generate_content(
                [prompt, image]
            )

            text = response.text.strip()

            text = text.replace("```json", "")
            text = text.replace("```", "")

            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL
            )

            if match:
                text = match.group(0)

            data = json.loads(text)

            st.success("✅ Analysis Complete")

            items = data.get("items", [])

            if not items:
                st.warning("No bill items found.")
                st.stop()

            df = pd.DataFrame(items)

            st.subheader("📋 Bill Items")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Amount column numeric
            if "amount" in df.columns:
                df["amount"] = pd.to_numeric(
                    df["amount"],
                    errors="coerce"
                ).fillna(0)

            calculated_total = float(
                df["amount"].sum()
            )

            try:
                bill_total = float(
                    data.get("total", 0)
                )
            except:
                bill_total = 0

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "💰 Calculated Total",
                    f"₹{calculated_total:,.2f}"
                )

            with col2:
                st.metric(
                    "🧾 Bill Total",
                    f"₹{bill_total:,.2f}"
                )

            difference = abs(
                calculated_total - bill_total
            )

            if difference < 1:
                st.success(
                    "✅ Bill Total Matched"
                )
            else:
                st.error(
                    f"❌ Bill Mismatch (Difference ₹{difference:,.2f})"
                )

            st.divider()

            # Excel Download
            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:
                df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Bill Items"
                )

            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name="bill_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # CSV Download
            csv_data = df.to_csv(
                index=False
            )

            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name="bill_report.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(
                f"Analysis Error: {str(e)}"
            )
````

