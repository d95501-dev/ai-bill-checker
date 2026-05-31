import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import re

st.set_page_config(page_title="AI Bill Checker")

st.title("🧾 AI Bill Checker")

api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

uploaded_file = st.file_uploader(
    "Upload Bill",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    if st.button("Analyze"):

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

                text = response.text.strip()

                text = text.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                )

                match = re.search(
                    r"\{.*\}",
                    text,
                    re.DOTALL
                )

                if match:
                    text = match.group(0)

                data = json.loads(text)

                st.success(
                    "Analysis Complete ✅"
                )

                items = data.get(
                    "items",
                    []
                )

                if items:

                    df = pd.DataFrame(items)

                    st.subheader(
                        "📋 Bill Items"
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

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
                            data.get(
                                "total",
                                0
                            )
                        )
                    except:
                        bill_total = 0

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

                    diff = abs(
                        calculated_total -
                        bill_total
                    )

                    if diff < 1:
                        st.success(
                            "✅ Bill Total Matched"
                        )
                    else:
                        st.error(
                            f"❌ Bill Mismatch (₹{diff:,.2f})"
                        )

                    excel_buffer = BytesIO()

                    with pd.ExcelWriter(
                        excel_buffer,
                        engine="openpyxl"
                    ) as writer:
                        df.to_excel(
                            writer,
                            index=False
                        )

                    st.download_button(
                        "📥 Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name="bill_report.xlsx"
                    )

                else:
                    st.warning(
                        "No items found."
                    )

            except Exception as e:
                st.error(
                    f"Analysis Error: {str(e)}"
                )
````
