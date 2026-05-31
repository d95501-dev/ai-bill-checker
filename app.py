import pandas as pd
from io import BytesIO
st.success("Analysis Complete ✅")
st.json(data)
st.success("Analysis Complete ✅")

items = data.get("items", [])

if items:

    df = pd.DataFrame(items)

    st.subheader("📋 Bill Items")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    try:
        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)

        calculated_total = float(df["amount"].sum())
    except:
        calculated_total = 0

    try:
        bill_total = float(data.get("total", 0))
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

    difference = abs(calculated_total - bill_total)

    if difference < 1:
        st.success("✅ Bill Total Matched")
    else:
        st.error(
            f"❌ Bill Mismatch (Difference ₹{difference:,.2f})"
        )

    st.divider()

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer,
            sheet_name="Bill Items",
            index=False
        )

    st.download_button(
        "📥 Download Excel",
        data=excel_buffer.getvalue(),
        file_name="bill_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "📄 Download CSV",
        data=csv,
        file_name="bill_report.csv",
        mime="text/csv"
    )

else:
    st.warning("No bill items found.")
items = data.get("items", [])

if items:

    df = pd.DataFrame(items)

    # Amount ko numeric banao
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    st.subheader("📋 Bill Items")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Totals
    calculated_total = float(df["amount"].sum())

    try:
        bill_total = float(data.get("total", 0))
    except:
        bill_total = 0

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="💰 Calculated Total",
            value=f"₹{calculated_total:,.2f}"
        )

    with col2:
        st.metric(
            label="🧾 Bill Total",
            value=f"₹{bill_total:,.2f}"
        )

    difference = abs(calculated_total - bill_total)

    if difference < 1:
        st.success("✅ Bill Total Matched")
    else:
        st.error(
            f"❌ Bill Mismatch | Difference ₹{difference:,.2f}"
        )

    st.divider()

    # Excel Download
    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            sheet_name="Bill Items",
            index=False
        )

    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer.getvalue(),
        file_name="bill_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # CSV Download
    csv = df.to_csv(index=False)

    st.download_button(
        label="📄 Download CSV",
        data=csv,
        file_name="bill_report.csv",
        mime="text/csv"
    )
