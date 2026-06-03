import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import subprocess
import os
import platform

# -----------------------------
# ENVIRONMENT DETECTION
# -----------------------------
IS_LOCAL = (
    platform.system() == "Windows"
    and os.path.exists(r"C:\\Program Files\\NAPS2\\NAPS2.Console.exe")
)

st.set_page_config(page_title="Deep CSC - AI Bill Processor", layout="wide")

# -----------------------------
# API CONFIG
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception:
    st.error("API Key missing!")
    st.stop()

# -----------------------------
# BILL ANALYSIS
# -----------------------------
def analyze_bill(image):
    prompt = """
    You are a strict JSON API.

    Read the bill image and extract:
    - vendor_name (string or null)
    - date (string or null)
    - items: array of objects with keys:
        
