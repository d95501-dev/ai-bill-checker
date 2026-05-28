import streamlit as st
import os
import json
from google import genai
from google.genai import types
from PIL import Image

# Streamlit Page Setup
st.set_page_config(page_title="AI Bill Checker Pro", layout="centered")

st.title("🧾 AI Bill Checker (Advanced LLM Approach)")
st.write("Upload your handwritten or printed dairy bill")

# --- API KEY ADDED HERE ---
# आपकी Google AI Studio से जनरेट की गई चाबी यहाँ जोड़ दी गई है
GEMINI_API_KEY = "AIzaSyC_P4I-q4tpwWwSKQhELo1VTW3ZpMdPj30"

# Initialize Gemini Client
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.warning("⚠️ कृपया कोड में अपनी Gemini API Key दर्ज करें।")
    client = None
else:
    client = genai.Client(api_key=GEMINI_API_KEY)

# File Uploader
uploaded_file = st.file_uploader("Choose Bill Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and client is not None:
    st.success("Bill Uploaded Successfully ✅")
    
    # Open image using PIL
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)
    
    st.write("🤖 AI is analyzing the bill (Reading Handwriting & Math)...")
    
    try:
        # Prompt designed to extract JSON data from the dairy bill
        prompt = """
        You are an expert billing auditor. Analyze this handwritten or printed Indian dairy bill image.
        Extract all individual item rows with their calculated amounts.
        Identify the 'Total' written on the bill.
        
        Provide the output STRICTLY in the following JSON format:
        {
            "items": [
                {"date": "DD/MM/YY", "name": "Item Name in Hindi/English", "qty": "quantity", "rate": number, "amount": number}
            ],
            "bill_total_written": number
        }
        """
        
        # Call Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        # Parse the JSON response from Gemini
        bill_data = json.loads(response.text)
        
        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------
        st.subheader("📄 Extracted Items Table")
        
        # Create a clean UI table
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
            calculated_sum += item.get("amount", 0)
            
        st.table(table_data)
        
        # Final Total Checking
        bill_total = bill_data.get("bill_total_written", 0)
        
        st.subheader("🧮 Math Verification")
        st.write(f"**Calculated Sum (Items Total):** ₹{calculated_sum}")
        st.write(f"**Total Written on Bill:** ₹{bill_total}")
        
        if calculated_sum == bill_total:
            st.success("✅ Bill Matched Perfectly! No calculation error found.")
        else:
            diff = abs(calculated_sum - bill_total)
            st.error(f"❌ Bill Mismatch! Difference found: ₹{diff}")
            st.info("💡 Suggestion: Please manually check the handwritten rates and item multiplies.")

    except Exception as e:
        st.error(f"AI Processing Error: {e}")
