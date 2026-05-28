import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# Streamlit Page Setup
st.set_page_config(page_title="AI Bill Checker Pro", layout="centered")

st.title("🧾 AI Bill Checker")
st.write("Upload your handwritten or printed dairy bill")

# --- API KEY CONFIGURATION ---
# Hum st.secrets ka use karenge jo Streamlit Cloud ke liye secure hai
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key not found in Secrets. Please configure in Streamlit Settings.")
    st.stop()

# File Uploader
uploaded_file = st.file_uploader("Choose Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success("Bill Uploaded Successfully ✅")
    
    # Open image using PIL
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    if st.button("Analyze Bill"):
        st.write("🤖 AI is analyzing the bill...")
        
        try:
            prompt = """
            You are an expert billing auditor. Analyze this handwritten or printed Indian dairy bill image.
            Extract all individual item rows with their calculated amounts.
            Identify the 'Total' written on the bill.
            
            Provide the output STRICTLY in the following JSON format:
            {
                "items": [
                    {"date": "DD/MM/YY", "name": "Item Name", "qty": "quantity", "rate": 0, "amount": 0}
                ],
                "bill_total_written": 0
            }
            """
            
            # Gemini Call
            response = model.generate_content([prompt, image])
            
            # Clean JSON response
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            bill_data = json.loads(json_text)
            
            # Display Results
            st.subheader("📄 Extracted Items Table")
            table_data = []
            calculated_sum = 0
            
            for item in bill_data.get("items", []):
                table_data.append({
                    "Date": item.get("date", "-"),
                    "Particulars": item.get("name", "-"),
                    "Qty": item.get("qty", "-"),
                    "Rate (₹)": item.get("rate", 0),
                    "Amount (₹)": item.get("amount", 0)
                })
                calculated_sum += float(item.get("amount", 0))
            
            st.table(table_data)
            
            # Math Verification
            bill_total = float(bill_data.get("bill_total_written", 0))
            st.subheader("🧮 Math Verification")
            st.write(f"**Calculated Sum:** ₹{calculated_sum}")
            st.write(f"**Total Written on Bill:** ₹{bill_total}")
            
            if abs(calculated_sum - bill_total) < 1:
                st.success("✅ Bill Matched Perfectly!")
            else:
                st.error(f"❌ Bill Mismatch! Difference: ₹{abs(calculated_sum - bill_total)}")

        except Exception as e:
            st.error(f"AI Processing Error: {e}")
