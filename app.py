import streamlit as st
import platform
import os

# 1. Environment का पता लगाएँ
IS_LOCAL = (
    platform.system() == "Windows" 
    and os.path.exists(r"C:\Program Files\NAPS2\NAPS2.Console.exe")
)

st.title("Deep CSC - AI Bill Processor")

# 2. UI को स्मार्ट तरीके से दिखाएँ
if IS_LOCAL:
    # यह केवल आपके लोकल कंप्यूटर पर दिखेगा
    tab1, tab2 = st.tabs(["📤 Upload & Process", "📠 Scanner Console"])
    
    with tab2:
        st.subheader("📠 Brother Scanner")
        # यहाँ आपका स्कैनर वाला बटन रखें
        if st.button("🚀 Trigger Flatbed Scan"):
            # स्कैनर का कोड यहाँ डालें
            pass
else:
    # यह Cloud पर दिखेगा
    st.info("💡 Tip: You are on the Cloud version. Scanner features are disabled. Please use 'Upload' to process bills.")
    tab1 = st.container()

# 3. Upload सेक्शन हर जगह चलेगा
with tab1:
    uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "png"])
    # बाकी का AI Processing लॉजिक यहाँ रखें
